from typing import Any, Dict, Optional

from app.repositories import user_repository


async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    return await user_repository.get_user_by_id(user_id)


async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    return await user_repository.get_user_by_email(email)

