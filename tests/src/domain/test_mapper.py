import pytest
from faker import Faker

from src.application.dto.admin_message import AdminMessageDTO
from src.application.dto.client_message import ClientMessageDTO
from src.domain.errors import values as errors
from src.domain.entities.admin_message import AdminMessage
from src.domain.entities.client_message import ClientMessage
from src.domain.mapper import map_admin_message_from_dto, map_client_message_from_dto

fake = Faker()


def test_map_client_message_from_dto():
    dto = ClientMessageDTO(user_id=fake.pyint(min_value=1, max_value=999999), text=fake.text())

    result = map_client_message_from_dto(dto)

    assert isinstance(result, ClientMessage)
    assert result.user_id.value == dto.user_id
    assert result.text.value == dto.text


def test_map_client_message_from_dto_invalid_user_id():
    dto = ClientMessageDTO(user_id=0, text=fake.text())

    with pytest.raises(errors.UserIdValidationError):
        map_client_message_from_dto(dto)


def test_map_admin_message_from_dto():
    dto = AdminMessageDTO(message_id=fake.pyint(min_value=1, max_value=999999), text=fake.text())

    result = map_admin_message_from_dto(dto)

    assert isinstance(result, AdminMessage)
    assert result.message_id.value == dto.message_id
    assert result.text.value == dto.text


def test_map_admin_message_from_dto_invalid_message_id():
    dto = AdminMessageDTO(message_id=0, text=fake.text())

    with pytest.raises(errors.MessageIdValidationError):
        map_admin_message_from_dto(dto)
