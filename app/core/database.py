from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings


_mongo_client: Optional[AsyncIOMotorClient] = None


def get_client() -> AsyncIOMotorClient:
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = AsyncIOMotorClient(settings.MONGODB_URI)
    return _mongo_client


def get_db() -> AsyncIOMotorDatabase:
    client = get_client()
    return client[settings.MONGODB_DB_NAME]


def get_users_collection():
    db = get_db()
    return db["users"]


def get_todos_collection():
    db = get_db()
    return db["todos"]


def get_otps_collection():
    db = get_db()
    return db["otps"]


async def close_client() -> None:
    global _mongo_client
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None

