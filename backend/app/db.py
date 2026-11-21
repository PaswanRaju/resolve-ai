"""Connections to MongoDB and Redis, opened once when the app starts."""

from pymongo import AsyncMongoClient
from redis.asyncio import Redis

from app.config import Settings


class Connections:
    def __init__(self, settings: Settings) -> None:
        self.mongo: AsyncMongoClient = AsyncMongoClient(
            settings.mongo_uri, serverSelectionTimeoutMS=2000
        )
        self.db = self.mongo[settings.mongo_db]
        self.redis: Redis = Redis.from_url(settings.redis_url, socket_connect_timeout=2)

    async def close(self) -> None:
        await self.mongo.close()
        await self.redis.aclose()
