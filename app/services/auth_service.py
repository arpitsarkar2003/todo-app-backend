import random
from datetime import timedelta
from typing import Any, Dict

from fastapi import HTTPException, status

from app.core.security import create_access_token, get_password_hash, verify_password
from app.repositories import otp_repository, user_repository
from app.schemas.auth_schemas import AuthResponse, AuthenticatedUserResponse, TokenResponse
from app.services import email_service
from app.utils.time_utils import minutes_from_now


OTP_EXPIRY_MINUTES = 10


def _build_auth_response(user: Dict[str, Any]) -> AuthResponse:
    access_token = create_access_token(
        {"sub": user["id"], "role": user["role"]},
        expires_delta=timedelta(minutes=60),
    )
    token = TokenResponse(access_token=access_token)
    user_payload = AuthenticatedUserResponse(
        id=user["id"],
        name=user["name"],
        email=user["email"],
        role=user["role"],
    )
    return AuthResponse(token=token, user=user_payload)


async def register_user(name: str, email: str, password: str) -> AuthResponse:
    existing = await user_repository.get_user_by_email(email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )

    hashed = get_password_hash(password)
    user_data: Dict[str, Any] = {
        "name": name,
        "email": email,
        "password_hash": hashed,
        "role": "user",
        "is_active": True,
        "is_verified": True,
    }
    user = await user_repository.create_user(user_data)
    return _build_auth_response(user)


async def login_with_password(email: str, password: str) -> AuthResponse:
    user = await user_repository.get_user_by_email(email)
    if not user or not user.get("password_hash"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    return _build_auth_response(user)


async def request_otp(email: str) -> None:
    # Always behave as if it worked, to avoid leaking whether the email exists.
    otp_code = f"{random.randint(0, 999999):06d}"
    expires_at = minutes_from_now(OTP_EXPIRY_MINUTES)
    await otp_repository.create_otp(email=email, otp_code=otp_code, expires_at=expires_at)
    email_service.send_otp_email(email=email, otp_code=otp_code)


async def verify_otp_and_login(email: str, otp_code: str) -> AuthResponse:
    otp = await otp_repository.get_latest_valid_otp(email)
    if not otp or otp["otp_code"] != otp_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )

    # Clean up OTPs for this email (best-effort).
    await otp_repository.delete_otps_for_email(email)

    user = await user_repository.get_user_by_email(email)
    if user:
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled",
            )
        # Mark verified if not already.
        if not user.get("is_verified", False):
            user = await user_repository.update_user(user["id"], {"is_verified": True})
    else:
        # Create OTP-only user.
        user_data: Dict[str, Any] = {
            "name": "User",
            "email": email,
            "password_hash": None,
            "role": "user",
            "is_active": True,
            "is_verified": True,
        }
        user = await user_repository.create_user(user_data)

    return _build_auth_response(user)

