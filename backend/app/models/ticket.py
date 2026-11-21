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


class WorkNoteCreate(BaseModel):
    """What an engineer sends to add a work note."""

    author: str = Field(min_length=1)
    body: str = Field(min_length=1)


class WorkNote(WorkNoteCreate):
    """A note an engineer adds while working the ticket. These feed the RAG index later."""

    created_at: datetime = Field(default_factory=_now)


class TicketCreate(BaseModel):
    """What a user sends to open a ticket."""

    short_description: str = Field(min_length=5, max_length=160)
    description: str = Field(min_length=1)
    category: str = "general"
    priority: Priority = Priority.MODERATE
    caller: str = Field(min_length=1)


class TicketUpdate(BaseModel):
    """Fields an engineer can change. Every field is optional: only sent fields change.

    Resolving goes through its own endpoint, because it needs resolution notes.
    """

    short_description: str | None = Field(default=None, min_length=5, max_length=160)
    description: str | None = Field(default=None, min_length=1)
    category: str | None = None
    priority: Priority | None = None
    status: Status | None = None
    assignment_group: str | None = None


class ResolveRequest(BaseModel):
    resolution_notes: str = Field(min_length=10)
    resolved_by: str = Field(min_length=1)


class Ticket(TicketCreate):
    """A stored ticket."""

    number: str = Field(pattern=r"^INC\d{7}$", examples=["INC0010001"])
    status: Status = Status.NEW
    assignment_group: str | None = None
    work_notes: list[WorkNote] = Field(default_factory=list)
    resolution_notes: str | None = None
    resolved_by: str | None = None
    resolved_at: datetime | None = None
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class TicketList(BaseModel):
    items: list[Ticket]
    total: int
    limit: int
    skip: int
