from dataclasses import dataclass

import pytest

from src.domain import errors
from src.domain.values import MessageId, Text, UserId
from src.domain.values.numbers import AdminId, ClientId


@dataclass(slots=True)
class Case:
    will_pass: bool
    value: str | int


@pytest.mark.parametrize(
    "case",
    (
        Case(will_pass=True, value=1),
        Case(will_pass=True, value=999999),
        Case(will_pass=False, value=0),
        Case(will_pass=False, value=-1),
    ),
)
def test_message_id(case):
    if case.will_pass:
        assert MessageId(case.value)
    else:
        with pytest.raises(errors.MessageIdValidationError):
            MessageId(case.value)


@pytest.mark.parametrize(
    "case",
    (
        Case(will_pass=True, value=1),
        Case(will_pass=True, value=620755101),
        Case(will_pass=False, value=0),
        Case(will_pass=False, value=-1),
    ),
)
def test_user_id(case):
    if case.will_pass:
        assert UserId(case.value)
    else:
        with pytest.raises(errors.UserIdValidationError):
            UserId(case.value)


@pytest.mark.parametrize(
    "case",
    (
        Case(will_pass=True, value="hello from client"),
        Case(will_pass=False, value=""),
        Case(will_pass=False, value="   "),
    ),
)
def test_text(case):
    if case.will_pass:
        assert Text(case.value)
    else:
        with pytest.raises(errors.TextValidationError):
            Text(case.value)


@pytest.mark.parametrize(
    "case",
    (
        Case(will_pass=True, value=1),
        Case(will_pass=True, value=620755101),
        Case(will_pass=False, value=0),
        Case(will_pass=False, value=-1),
    ),
)
def test_client_id(case):
    # валидация унаследована от UserId → та же ошибка
    if case.will_pass:
        assert ClientId(case.value)
    else:
        with pytest.raises(errors.UserIdValidationError):
            ClientId(case.value)


@pytest.mark.parametrize(
    "case",
    (
        Case(will_pass=True, value=1),
        Case(will_pass=True, value=620755101),
        Case(will_pass=False, value=0),
        Case(will_pass=False, value=-1),
    ),
)
def test_admin_id(case):
    if case.will_pass:
        assert AdminId(case.value)
    else:
        with pytest.raises(errors.UserIdValidationError):
            AdminId(case.value)


def test_client_and_admin_ids_are_distinct_types():
    # страж различия: один и тот же value, но разные типы — это разные VO.
    # ломается, если кто-то приделает кастомный __eq__ или сольёт типы.
    assert ClientId(5) != AdminId(5)
    assert ClientId(5) == ClientId(5)
    assert AdminId(5) == AdminId(5)
