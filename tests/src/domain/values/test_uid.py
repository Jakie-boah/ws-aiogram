from dataclasses import dataclass
from uuid import UUID, uuid4

import pytest

from src.domain import errors
from src.domain.values.uid import TicketId


@dataclass(slots=True)
class Case:
    will_pass: bool
    value: object


@pytest.mark.parametrize(
    "case",
    (
        Case(will_pass=True, value=uuid4()),
        Case(will_pass=True, value=UUID("12345678-1234-5678-1234-567812345678")),
        Case(will_pass=False, value=None),
        Case(will_pass=False, value="12345678-1234-5678-1234-567812345678"),  # строка, не UUID
        Case(will_pass=False, value=123),
    ),
)
def test_ticket_id(case):
    if case.will_pass:
        assert TicketId(case.value)
    else:
        with pytest.raises(errors.TicketIdValidationError):
            TicketId(case.value)
