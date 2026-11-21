"""Ticket data models, loosely based on a ServiceNow incident."""

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class Priority(StrEnum):
    CRITICAL = "1-critical"
    HIGH = "2-high"
    MODERATE = "3-moderate"
    LOW = "4-low"


class Status(StrEnum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    RESOLVED = "resolved"
    CLOSED = "closed"


def _now() -> datetime:
    return datetime.now(UTC)


class WorkNote(BaseModel):
    """A note an agent adds while working the ticket. These feed the RAG index later."""

    author: str
    body: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=_now)


class TicketCreate(BaseModel):
    """What a user sends to open a ticket."""

    short_description: str = Field(min_length=5, max_length=160)
    description: str = Field(min_length=1)
    category: str = "general"
    priority: Priority = Priority.MODERATE
    caller: str


class Ticket(TicketCreate):
    """A stored ticket."""

    number: str = Field(pattern=r"^INC\d{7}$", examples=["INC0010001"])
    status: Status = Status.NEW
    assignment_group: str | None = None
    work_notes: list[WorkNote] = Field(default_factory=list)
    resolution_notes: str | None = None
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
