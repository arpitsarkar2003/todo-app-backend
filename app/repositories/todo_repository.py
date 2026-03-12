from typing import Any, Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

from app.core.database import get_todos_collection
from app.utils.time_utils import utcnow


def _todos_collection() -> AsyncIOMotorCollection:
    return get_todos_collection()


def _serialize_todo(document: Dict[str, Any]) -> Dict[str, Any]:
    document["id"] = str(document.pop("_id"))
    document["user_id"] = str(document["user_id"])
    return document


async def create_todo(user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    now = utcnow()
    doc: Dict[str, Any] = {
        "title": data["title"],
        "description": data.get("description"),
        "is_completed": False,
        "user_id": ObjectId(user_id),
        "created_at": now,
        "updated_at": now,
    }
    result = await _todos_collection().insert_one(doc)
    created = await _todos_collection().find_one({"_id": result.inserted_id})
    return _serialize_todo(created)


async def get_todos_for_user(user_id: str) -> List[Dict[str, Any]]:
    cursor = _todos_collection().find({"user_id": ObjectId(user_id)}).sort(
        "created_at", -1
    )
    todos: List[Dict[str, Any]] = []
    async for doc in cursor:
        todos.append(_serialize_todo(doc))
    return todos


async def get_todo_for_user(user_id: str, todo_id: str) -> Optional[Dict[str, Any]]:
    try:
        oid = ObjectId(todo_id)
    except Exception:
        return None
    doc = await _todos_collection().find_one({"_id": oid, "user_id": ObjectId(user_id)})
    if not doc:
        return None
    return _serialize_todo(doc)


async def update_todo_for_user(
    user_id: str, todo_id: str, updates: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    try:
        oid = ObjectId(todo_id)
    except Exception:
        return None
    updates["updated_at"] = utcnow()
    await _todos_collection().update_one(
        {"_id": oid, "user_id": ObjectId(user_id)}, {"$set": updates}
    )
    doc = await _todos_collection().find_one(
        {"_id": oid, "user_id": ObjectId(user_id)}
    )
    if not doc:
        return None
    return _serialize_todo(doc)


async def delete_todo_for_user(user_id: str, todo_id: str) -> bool:
    try:
        oid = ObjectId(todo_id)
    except Exception:
        return False
    result = await _todos_collection().delete_one(
        {"_id": oid, "user_id": ObjectId(user_id)}
    )
    return result.deleted_count == 1


async def count_todos() -> int:
    return await _todos_collection().count_documents({})


async def count_completed_todos() -> int:
    return await _todos_collection().count_documents({"is_completed": True})


async def count_pending_todos() -> int:
    return await _todos_collection().count_documents({"is_completed": False})


async def get_recent_todos(limit: int = 5) -> List[Dict[str, Any]]:
    cursor = (
        _todos_collection()
        .find({})
        .sort("created_at", -1)
        .limit(limit)
    )
    todos: List[Dict[str, Any]] = []
    async for doc in cursor:
        todos.append(_serialize_todo(doc))
    return todos


async def get_user_todo_counts() -> List[Dict[str, Any]]:
    pipeline = [
        {
            "$group": {
                "_id": "$user_id",
                "total_todos": {"$sum": 1},
                "completed_todos": {
                    "$sum": {
                        "$cond": ["$is_completed", 1, 0],
                    }
                },
                "pending_todos": {
                    "$sum": {
                        "$cond": ["$is_completed", 0, 1],
                    }
                },
            }
        }
    ]
    cursor = _todos_collection().aggregate(pipeline)
    results: List[Dict[str, Any]] = []
    async for doc in cursor:
        results.append(
            {
                "user_id": str(doc["_id"]),
                "total_todos": int(doc.get("total_todos", 0)),
                "completed_todos": int(doc.get("completed_todos", 0)),
                "pending_todos": int(doc.get("pending_todos", 0)),
            }
        )
    return results

