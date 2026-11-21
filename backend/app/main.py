"""FastAPI entry point."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import Connections
from app.repositories.tickets import TicketRepository
from app.routers import health, tickets

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    conns = Connections(get_settings())
    app.state.connections = conns
    try:
        await TicketRepository(conns.db).ensure_indexes()
    except Exception as exc:  # keep starting so /health still answers; /health/ready shows why
        logger.warning("Could not create MongoDB indexes: %s", exc)
    yield
    await app.state.connections.close()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(tickets.router)
    return app


app = create_app()
