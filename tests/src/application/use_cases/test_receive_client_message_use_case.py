import datetime

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.application.dto.client_message import ReceiveClientMessage
from src.application.interfaces.postgres.repositories.errors import ActiveTicketAlreadyExistsError
from src.application.use_cases.receive_client_message_use_case import ReceiveClientMessageUseCase
from src.domain.entities.ticket import Ticket
from src.domain.values import ClientId, MessageType, TicketCloseReason, TicketState
from src.infrastructure.postgres.repositories.ticket import ImplPostgresTicketRepository
from src.infrastructure.postgres.tables import messages_table, tickets_table


CLIENT = ClientId(777)
OTHER_CLIENT = ClientId(888)
MINUTE = datetime.timedelta(minutes=1)
NOW = datetime.datetime(2026, 7, 22, 12, 0, tzinfo=datetime.timezone.utc)


def dto(
        client_id: ClientId = CLIENT,
        text: str = "привет",
        sent_at: datetime.datetime = NOW,
        message_type: MessageType = MessageType.TEXT,
) -> ReceiveClientMessage:
    return ReceiveClientMessage(
        user_id=client_id.value,
        text=text,
        sent_at=sent_at,
        message_type=message_type,
    )


@pytest.fixture(name="use_case")
def use_case_factory(logger, uow):
    return ReceiveClientMessageUseCase(logger=logger, uow=uow)


@pytest_asyncio.fixture(name="competitor")
async def competitor_factory(engine):
    """Второй коннект — конкурент, который ходит в базу мимо нашей транзакции."""
    maker = async_sessionmaker(bind=engine, expire_on_commit=False)

    class Competitor:
        @staticmethod
        async def open_ticket(client_id: ClientId, now: datetime.datetime = NOW) -> Ticket:
            entity = Ticket.open(client_id=client_id, now=now)
            async with maker() as other_session:
                await ImplPostgresTicketRepository(other_session).save(entity)
                await other_session.commit()
            return entity

        @staticmethod
        async def close_ticket(entity: Ticket) -> None:
            async with maker() as other_session:
                repository = ImplPostgresTicketRepository(other_session)
                loaded = await repository.get(entity.id)
                loaded.close(reason=TicketCloseReason.RESOLVED, now=NOW + MINUTE)
                await repository.save(loaded)
                await other_session.commit()

    return Competitor()


async def fetch_tickets(session, client_id: ClientId):
    rows = await session.execute(
        select(tickets_table).where(tickets_table.c.client_id == client_id.value)
    )
    return rows.mappings().all()


async def fetch_messages(session):
    rows = await session.execute(select(messages_table).order_by(messages_table.c.sent_at))
    return rows.mappings().all()


# --------------------------------------------------------------------------
# 1. Механика savepoint: что он делает с транзакцией
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_savepoint_keeps_outer_transaction_alive(uow, session, competitor):
    # полезная работа, накопленная до конфликта
    mine = Ticket.open(client_id=OTHER_CLIENT, now=NOW)
    await uow.ticket.save(mine)

    # конкурент занял активный тикет CLIENT и закоммитился
    winner = await competitor.open_ticket(CLIENT)

    with pytest.raises(ActiveTicketAlreadyExistsError):
        async with uow.savepoint():
            await uow.ticket.save(Ticket.open(client_id=CLIENT, now=NOW))

    # транзакция жива: следующий запрос выполняется, а не падает
    found = await uow.ticket.find_active_by_client(CLIENT)
    assert found is not None
    assert found.id == winner.id

    # и работа, сделанная до конфликта, не потерялась
    await uow.commit()
    rows = await fetch_tickets(session, OTHER_CLIENT)
    assert len(rows) == 1
    assert rows[0].id == mine.id.value


@pytest.mark.asyncio
async def test_without_savepoint_transaction_is_dead(uow, competitor):
    await uow.ticket.save(Ticket.open(client_id=OTHER_CLIENT, now=NOW))
    await competitor.open_ticket(CLIENT)

    with pytest.raises(ActiveTicketAlreadyExistsError):
        await uow.ticket.save(Ticket.open(client_id=CLIENT, now=NOW))

    # без savepoint транзакция в aborted — любой следующий запрос падает
    with pytest.raises(SQLAlchemyError):
        await uow.ticket.find_active_by_client(CLIENT)


# --------------------------------------------------------------------------
# 2. Юзкейс без гонки
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_creates_ticket_and_message(use_case, session):
    await use_case(dto())

    tickets = await fetch_tickets(session, CLIENT)
    assert len(tickets) == 1
    assert tickets[0].status == TicketState.OPEN
    assert tickets[0].last_activity_at == NOW

    messages = await fetch_messages(session)
    assert len(messages) == 1
    assert messages[0].ticket_id == tickets[0].id
    assert messages[0].text == "привет"
    assert messages[0].sender_id == CLIENT.value


@pytest.mark.asyncio
async def test_reuses_active_ticket(use_case, session):
    await use_case(dto(text="раз", sent_at=NOW))
    await use_case(dto(text="два", sent_at=NOW + MINUTE))

    tickets = await fetch_tickets(session, CLIENT)
    assert len(tickets) == 1
    assert tickets[0].last_activity_at == NOW + MINUTE

    messages = await fetch_messages(session)
    assert len(messages) == 2
    assert {row.ticket_id for row in messages} == {tickets[0].id}
    assert [row.text for row in messages] == ["раз", "два"]


# --------------------------------------------------------------------------
# 3. Гонка find-or-create
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_race_lost_joins_winner_ticket(use_case, uow, session, competitor):
    """Конкурент вклинивается ровно между find_active_by_client и save."""
    reads = []
    winner = {}
    original_find = uow.ticket.find_active_by_client

    async def find_then_lose_race(client_id):
        result = await original_find(client_id)
        reads.append(result)

        if len(reads) == 1:
            # мы уже прочитали None — и вот теперь нас обгоняют
            winner["ticket"] = await competitor.open_ticket(client_id)

        return result

    uow.ticket.find_active_by_client = find_then_lose_race

    await use_case(dto())

    # первое чтение — пусто, второе (после отката savepoint) — уже победитель
    assert len(reads) == 2
    assert reads[0] is None
    assert reads[1] is not None
    assert reads[1].id == winner["ticket"].id

    # тикет ровно один, наш проигравший не сохранился
    tickets = await fetch_tickets(session, CLIENT)
    assert len(tickets) == 1
    assert tickets[0].id == winner["ticket"].id.value

    # сообщение не потерялось и приклеилось к тикету победителя
    messages = await fetch_messages(session)
    assert len(messages) == 1
    assert messages[0].ticket_id == winner["ticket"].id.value
    assert messages[0].text == "привет"


@pytest.mark.asyncio
async def test_race_lost_and_winner_closed_reraises(use_case, uow, competitor):
    """Победителя закрыли до того, как мы успели его перечитать — guard срабатывает."""
    reads = []
    winner = {}
    original_find = uow.ticket.find_active_by_client

    async def find_then_lose_race(client_id):
        if not reads:
            reads.append(None)
            result = await original_find(client_id)
            winner["ticket"] = await competitor.open_ticket(client_id)
            return result

        # второе чтение: активного тикета уже нет — победителя успели закрыть
        await competitor.close_ticket(winner["ticket"])
        return await original_find(client_id)

    uow.ticket.find_active_by_client = find_then_lose_race

    with pytest.raises(ActiveTicketAlreadyExistsError):
        await use_case(dto())


