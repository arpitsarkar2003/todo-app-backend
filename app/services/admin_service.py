from typing import Any, Dict, List

from fastapi import HTTPException, status

from app.core.security import verify_password
from app.repositories import todo_repository, user_repository


async def admin_login(email: str, password: str) -> Dict[str, Any]:
    user = await user_repository.get_user_by_email(email)
    if not user or user.get("role") != "admin" or not user.get("password_hash"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
        )

    if not verify_password(password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is disabled",
        )

    return user


async def get_summary_report() -> Dict[str, Any]:
    total_users = await user_repository.count_users()
    total_todos = await todo_repository.count_todos()
    total_completed_todos = await todo_repository.count_completed_todos()
    total_pending_todos = await todo_repository.count_pending_todos()

    recent_users = await user_repository.get_recent_users(limit=5)
    recent_todos = await todo_repository.get_recent_todos(limit=5)

    user_counts = await todo_repository.get_user_todo_counts()

    # Enrich user_counts with user email.
    enriched_counts: List[Dict[str, Any]] = []
    for entry in user_counts:
        user = await user_repository.get_user_by_id(entry["user_id"])
        enriched_counts.append(
            {
                "user_id": entry["user_id"],
                "email": user["email"] if user else "",
                "total_todos": entry["total_todos"],
                "completed_todos": entry["completed_todos"],
                "pending_todos": entry["pending_todos"],
            }
        )

    return {
        "total_users": total_users,
        "total_todos": total_todos,
        "total_completed_todos": total_completed_todos,
        "total_pending_todos": total_pending_todos,
        "recent_users": recent_users,
        "recent_todos": recent_todos,
        "user_todo_counts": enriched_counts,
    }

