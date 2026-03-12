from datetime import datetime

from pydantic import BaseModel


class TodoInDB(BaseModel):
    id: str  # string version of Mongo ObjectId
    title: str
    description: str | None = None
    is_completed: bool = False
    user_id: str  # string version of user ObjectId
    created_at: datetime
    updated_at: datetime

