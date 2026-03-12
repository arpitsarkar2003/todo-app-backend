from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status

from app.repositories import todo_repository


async def create_todo_for_user(user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    return await todo_repository.create_todo(user_id=user_id, data=data)


async def get_user_todos(user_id: str) -> List[Dict[str, Any]]:
    return await todo_repository.get_todos_for_user(user_id=user_id)


async def get_user_todo_by_id(user_id: str, todo_id: str) -> Dict[str, Any]:
    todo = await todo_repository.get_todo_for_user(user_id=user_id, todo_id=todo_id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )
    return todo


async def update_user_todo(
    user_id: str, todo_id: str, updates: Dict[str, Any]
) -> Dict[str, Any]:
    todo = await todo_repository.update_todo_for_user(
        user_id=user_id, todo_id=todo_id, updates=updates
    )
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )
    return todo


async def delete_user_todo(user_id: str, todo_id: str) -> None:
    success = await todo_repository.delete_todo_for_user(
        user_id=user_id, todo_id=todo_id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )


async def admin_list_all_todos() -> List[Dict[str, Any]]:
    # Simple admin helper: reuse repository listing.
    # For now we can use get_recent_todos with a high limit,
    # or implement a dedicated listing if needed later.
    return await todo_repository.get_recent_todos(limit=1000)

