"""All MongoDB access for tickets lives here, so routes never touch the database directly.

That keeps routes small and makes the storage easy to swap or test.
"""

import re
from datetime import UTC, datetime
from typing import Any

from pymongo import ASCENDING, DESCENDING, ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase

from app.models.ticket import (
    Priority,
    ResolveRequest,
    Status,
    Ticket,
    TicketCreate,
    TicketUpdate,
    WorkNote,
    WorkNoteCreate,
)

NUMBER_OFFSET = 10000  # first ticket is INC0010001, like a fresh ServiceNow instance


class TicketRepository:
    def __init__(self, db: AsyncDatabase) -> None:
        self.tickets = db["tickets"]
        self.counters = db["counters"]

    async def ensure_indexes(self) -> None:
        await self.tickets.create_index("number", unique=True)
        await self.tickets.create_index([("status", ASCENDING), ("created_at", DESCENDING)])

    async def _next_number(self) -> str:
        # $inc is atomic, so two tickets created at the same moment never get the same number.
        # upsert=True creates the counter on the very first ticket.
        counter = await self.counters.find_one_and_update(
            {"_id": "ticket_number"},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return f"INC{NUMBER_OFFSET + counter['seq']:07d}"

    async def create(self, data: TicketCreate) -> Ticket:
        ticket = Ticket(**data.model_dump(), number=await self._next_number())
        await self.tickets.insert_one(ticket.model_dump())
        return ticket

    async def get(self, number: str) -> Ticket | None:
        doc = await self.tickets.find_one({"number": number}, {"_id": 0})
        return Ticket(**doc) if doc else None

    async def list(
        self,
        *,
        status: Status | None = None,
        priority: Priority | None = None,
        q: str | None = None,
        limit: int = 20,
        skip: int = 0,
    ) -> tuple[list[Ticket], int]:
        query: dict[str, Any] = {}
        if status:
            query["status"] = status
        if priority:
            query["priority"] = priority
        if q:
            # Plain text match for now. Semantic search (embeddings) comes in step 4.
            pattern = {"$regex": re.escape(q), "$options": "i"}
            query["$or"] = [{"short_description": pattern}, {"description": pattern}]

        total = await self.tickets.count_documents(query)
        cursor = (
            self.tickets.find(query, {"_id": 0})
            .sort("created_at", DESCENDING)
            .skip(skip)
            .limit(limit)
        )
        return [Ticket(**doc) async for doc in cursor], total

    async def update(self, number: str, changes: TicketUpdate) -> Ticket | None:
        fields = changes.model_dump(exclude_unset=True)
        fields["updated_at"] = datetime.now(UTC)
        doc = await self.tickets.find_one_and_update(
            {"number": number},
            {"$set": fields},
            projection={"_id": 0},
            return_document=ReturnDocument.AFTER,
        )
        return Ticket(**doc) if doc else None

    async def add_work_note(self, number: str, note: WorkNoteCreate) -> Ticket | None:
        work_note = WorkNote(**note.model_dump())
        doc = await self.tickets.find_one_and_update(
            {"number": number},
            {
                "$push": {"work_notes": work_note.model_dump()},
                "$set": {"updated_at": work_note.created_at},
            },
            projection={"_id": 0},
            return_document=ReturnDocument.AFTER,
        )
        return Ticket(**doc) if doc else None

    async def resolve(self, number: str, req: ResolveRequest) -> Ticket | None:
        now = datetime.now(UTC)
        doc = await self.tickets.find_one_and_update(
            {"number": number},
            {
                "$set": {
                    "status": Status.RESOLVED,
                    "resolution_notes": req.resolution_notes,
                    "resolved_by": req.resolved_by,
                    "resolved_at": now,
                    "updated_at": now,
                }
            },
            projection={"_id": 0},
            return_document=ReturnDocument.AFTER,
        )
        return Ticket(**doc) if doc else None
