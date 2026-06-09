from dataclasses import dataclass

import pytest

from src.domain import errors
from src.domain.values import MessageId, Text, UserId


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
