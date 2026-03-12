from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class UserResponse(UserBase):
    pass


class UserMeResponse(UserBase):
    pass

