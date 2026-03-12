from fastapi import APIRouter, Depends, status

from app.dependencies.auth_dependencies import get_current_user
from app.schemas.todo_schemas import (
    TodoCreate,
    TodoListResponse,
    TodoResponse,
    TodoUpdate,
)
from app.services import todo_service


router = APIRouter(prefix="/api/v1/todos", tags=["todos"])


@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    payload: TodoCreate,
    current_user=Depends(get_current_user),
):
    todo = await todo_service.create_todo_for_user(
        user_id=current_user["id"], data=payload.dict()
    )
    return todo


@router.get("/", response_model=TodoListResponse)
async def list_my_todos(current_user=Depends(get_current_user)):
    todos = await todo_service.get_user_todos(user_id=current_user["id"])
    return {"todos": todos}


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_my_todo(todo_id: str, current_user=Depends(get_current_user)):
    todo = await todo_service.get_user_todo_by_id(
        user_id=current_user["id"], todo_id=todo_id
    )
    return todo


@router.put("/{todo_id}", response_model=TodoResponse)
async def update_my_todo(
    todo_id: str,
    payload: TodoUpdate,
    current_user=Depends(get_current_user),
):
    updates = {k: v for k, v in payload.dict().items() if v is not None}
    todo = await todo_service.update_user_todo(
        user_id=current_user["id"], todo_id=todo_id, updates=updates
    )
    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_todo(todo_id: str, current_user=Depends(get_current_user)):
    await todo_service.delete_user_todo(
        user_id=current_user["id"], todo_id=todo_id
    )
    return None


@router.patch("/{todo_id}/complete", response_model=TodoResponse)
async def mark_complete(todo_id: str, current_user=Depends(get_current_user)):
    todo = await todo_service.update_user_todo(
        user_id=current_user["id"],
        todo_id=todo_id,
        updates={"is_completed": True},
    )
    return todo


@router.patch("/{todo_id}/incomplete", response_model=TodoResponse)
async def mark_incomplete(todo_id: str, current_user=Depends(get_current_user)):
    todo = await todo_service.update_user_todo(
        user_id=current_user["id"],
        todo_id=todo_id,
        updates={"is_completed": False},
    )
    return todo

