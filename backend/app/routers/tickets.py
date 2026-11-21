"""Ticket API.

POST   /tickets                       open a ticket
GET    /tickets                       list, with filters and paging
GET    /tickets/{number}              one ticket
PATCH  /tickets/{number}              change fields (priority, status, assignment group, ...)
POST   /tickets/{number}/work-notes   add a work note
POST   /tickets/{number}/resolve      resolve with resolution notes
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.dependencies import get_ticket_repo
from app.models.ticket import (
    Priority,
    ResolveRequest,
    Status,
    Ticket,
    TicketCreate,
    TicketList,
    TicketUpdate,
    WorkNoteCreate,
)
from app.repositories.tickets import TicketRepository

router = APIRouter(prefix="/tickets", tags=["tickets"])

Repo = Annotated[TicketRepository, Depends(get_ticket_repo)]
TicketNumber = Annotated[str, Path(pattern=r"^INC\d{7}$", examples=["INC0010001"])]


async def _get_open_ticket(repo: TicketRepository, number: str) -> Ticket:
    """Load a ticket that can still be changed. Closed tickets are read-only."""
    ticket = await repo.get(number)
    if ticket is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Ticket {number} not found")
    if ticket.status == Status.CLOSED:
        raise HTTPException(status.HTTP_409_CONFLICT, f"Ticket {number} is closed")
    return ticket


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_ticket(data: TicketCreate, repo: Repo) -> Ticket:
    return await repo.create(data)


@router.get("")
async def list_tickets(
    repo: Repo,
    status_: Annotated[Status | None, Query(alias="status")] = None,
    priority: Priority | None = None,
    q: Annotated[str | None, Query(max_length=100)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    skip: Annotated[int, Query(ge=0)] = 0,
) -> TicketList:
    items, total = await repo.list(status=status_, priority=priority, q=q, limit=limit, skip=skip)
    return TicketList(items=items, total=total, limit=limit, skip=skip)


@router.get("/{number}")
async def get_ticket(number: TicketNumber, repo: Repo) -> Ticket:
    ticket = await repo.get(number)
    if ticket is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Ticket {number} not found")
    return ticket


@router.patch("/{number}")
async def update_ticket(number: TicketNumber, changes: TicketUpdate, repo: Repo) -> Ticket:
    ticket = await _get_open_ticket(repo, number)
    if changes.status == Status.RESOLVED and ticket.status != Status.RESOLVED:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "Use POST /tickets/{number}/resolve to resolve a ticket",
        )
    updated = await repo.update(number, changes)
    assert updated is not None
    return updated


@router.post("/{number}/work-notes", status_code=status.HTTP_201_CREATED)
async def add_work_note(number: TicketNumber, note: WorkNoteCreate, repo: Repo) -> Ticket:
    await _get_open_ticket(repo, number)
    updated = await repo.add_work_note(number, note)
    assert updated is not None
    return updated


@router.post("/{number}/resolve")
async def resolve_ticket(number: TicketNumber, req: ResolveRequest, repo: Repo) -> Ticket:
    ticket = await _get_open_ticket(repo, number)
    if ticket.status == Status.RESOLVED:
        raise HTTPException(status.HTTP_409_CONFLICT, f"Ticket {number} is already resolved")
    updated = await repo.resolve(number, req)
    assert updated is not None
    return updated
