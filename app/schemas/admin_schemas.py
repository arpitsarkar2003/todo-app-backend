from datetime import datetime
from typing import List

from pydantic import BaseModel, EmailStr


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminUserSummary(BaseModel):
    id: str
    name: str
    email: EmailStr
    created_at: datetime


class AdminTodoSummary(BaseModel):
    id: str
    title: str
    is_completed: bool
    user_id: str
    created_at: datetime


class UserTodoCount(BaseModel):
    user_id: str
    email: EmailStr
    total_todos: int
    completed_todos: int
    pending_todos: int


class AdminReportSummary(BaseModel):
    total_users: int
    total_todos: int
    total_completed_todos: int
    total_pending_todos: int
    recent_users: List[AdminUserSummary]
    recent_todos: List[AdminTodoSummary]
    user_todo_counts: List[UserTodoCount]

