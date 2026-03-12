from typing import Any, Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

from app.core.database import get_users_collection
from app.utils.time_utils import utcnow


def _users_collection() -> AsyncIOMotorCollection:
    return get_users_collection()


def _serialize_user(document: Dict[str, Any]) -> Dict[str, Any]:
    document["id"] = str(document.pop("_id"))
    return document


async def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    now = utcnow()
    user_data.setdefault("created_at", now)
    user_data.setdefault("updated_at", now)
    result = await _users_collection().insert_one(user_data)
    created = await _users_collection().find_one({"_id": result.inserted_id})
    return _serialize_user(created)


async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    user = await _users_collection().find_one({"email": email})
    if not user:
        return None
    return _serialize_user(user)


async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    try:
        oid = ObjectId(user_id)
    except Exception:
        return None
    user = await _users_collection().find_one({"_id": oid})
    if not user:
        return None
    return _serialize_user(user)


async def update_user(user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        oid = ObjectId(user_id)
    except Exception:
        return None
    updates["updated_at"] = utcnow()
    await _users_collection().update_one({"_id": oid}, {"$set": updates})
    user = await _users_collection().find_one({"_id": oid})
    if not user:
        return None
    return _serialize_user(user)


async def count_users() -> int:
    return await _users_collection().count_documents({})


async def get_recent_users(limit: int = 5) -> List[Dict[str, Any]]:
    cursor = (
        _users_collection()
        .find({})
        .sort("created_at", -1)
        .limit(limit)
    )
    users: List[Dict[str, Any]] = []
    async for doc in cursor:
        users.append(_serialize_user(doc))
    return users

