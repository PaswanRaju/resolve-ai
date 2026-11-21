import pytest
from pydantic import ValidationError

from app.models.ticket import Priority, Status, Ticket


def make_ticket(**overrides) -> Ticket:
    data = {
        "number": "INC0010001",
        "short_description": "VPN disconnects every 10 minutes",
        "description": "GlobalProtect drops on home Wi-Fi.",
        "caller": "jdoe",
    }
    data.update(overrides)
    return Ticket(**data)


def test_defaults() -> None:
    t = make_ticket()
    assert t.status is Status.NEW
    assert t.priority is Priority.MODERATE
    assert t.work_notes == []


def test_rejects_bad_ticket_number() -> None:
    with pytest.raises(ValidationError):
        make_ticket(number="12345")


def test_rejects_short_description_too_short() -> None:
    with pytest.raises(ValidationError):
        make_ticket(short_description="hi")
