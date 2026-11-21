"""FastAPI dependencies: small functions that routes declare as parameters.

FastAPI calls them per request. In tests they can be overridden with app.dependency_overrides.
"""

from fastapi import Request

from app.repositories.tickets import TicketRepository


def get_ticket_repo(request: Request) -> TicketRepository:
    return TicketRepository(request.app.state.connections.db)
