from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserInDB(BaseModel):
    id: Optional[str] = None  # string version of Mongo ObjectId
    name: str
    email: EmailStr
    password_hash: Optional[str] = None
    role: str = "user"
    is_active: bool = True
    is_verified: bool = True
    created_at: datetime
    updated_at: datetime

