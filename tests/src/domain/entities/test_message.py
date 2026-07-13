from src.domain.entities.message import Message
from src.domain.values import UserId, SenderType, Text, MessageType
from faker import Faker
from zoneinfo import ZoneInfo

fake = Faker()


def test_message_create():
    user_id = UserId(fake.pyint(min_value=1, max_value=1000000))
    sender_type = SenderType.CLIENT
    text = Text(fake.text())
    now = fake.date_time(ZoneInfo("Europe/Moscow"))

    message = Message.new_message(
        sender_id=user_id,
        sender_type=sender_type,
        text=text,
        sent_at=now
    )

    assert message.id is not None
    assert message.sender_id == user_id
    assert message.sender_type == sender_type
    assert message.text == text
    assert message.sent_at == now
    assert message.msg_type == MessageType.TEXT

    assert message.delivered_at is None
    assert message.read_at is None
