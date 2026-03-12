from datetime import timedelta

from fastapi import APIRouter, status

from app.core.security import create_access_token
from app.schemas.admin_schemas import AdminLoginRequest
from app.schemas.auth_schemas import AuthenticatedUserResponse, TokenResponse
from app.services import admin_service


router = APIRouter(prefix="/api/v1/admin/auth", tags=["admin-auth"])


@router.post("/login")
async def admin_login(payload: AdminLoginRequest):
    admin_user = await admin_service.admin_login(
        email=payload.email, password=payload.password
    )
    access_token = create_access_token(
        {"sub": admin_user["id"], "role": admin_user["role"]},
        expires_delta=timedelta(minutes=60),
    )
    token = TokenResponse(access_token=access_token)
    user_payload = AuthenticatedUserResponse(
        id=admin_user["id"],
        name=admin_user["name"],
        email=admin_user["email"],
        role=admin_user["role"],
    )
    return {"token": token, "user": user_payload}

