from fastapi import APIRouter, Depends, status

from app.dependencies.auth_dependencies import get_current_user
from app.schemas.auth_schemas import (
    AuthResponse,
    LoginRequest,
    OTPRequest,
    OTPVerifyRequest,
    RegisterRequest,
)
from app.schemas.user_schemas import UserMeResponse
from app.services import auth_service


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest):
    return await auth_service.register_user(
        name=payload.name, email=payload.email, password=payload.password
    )


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest):
    return await auth_service.login_with_password(
        email=payload.email, password=payload.password
    )


@router.post("/request-otp", status_code=status.HTTP_200_OK)
async def request_otp(payload: OTPRequest):
    await auth_service.request_otp(email=payload.email)
    # Always respond with generic message.
    return {"message": "If the email exists, an OTP has been sent."}


@router.post("/verify-otp", response_model=AuthResponse)
async def verify_otp(payload: OTPVerifyRequest):
    return await auth_service.verify_otp_and_login(
        email=payload.email, otp_code=payload.otp_code
    )


@router.get("/me", response_model=UserMeResponse)
async def get_me(current_user=Depends(get_current_user)):
    return current_user

