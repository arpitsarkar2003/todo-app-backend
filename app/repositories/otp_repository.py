from datetime import datetime
from typing import Any, Dict, Optional

from motor.motor_asyncio import AsyncIOMotorCollection

from app.core.database import get_otps_collection
from app.utils.time_utils import utcnow


def _otps_collection() -> AsyncIOMotorCollection:
    return get_otps_collection()


async def create_otp(email: str, otp_code: str, expires_at: datetime) -> Dict[str, Any]:
    doc = {
        "email": email,
        "otp_code": otp_code,
        "expires_at": expires_at,
        "created_at": utcnow(),
    }
    result = await _otps_collection().insert_one(doc)
    created = await _otps_collection().find_one({"_id": result.inserted_id})
    created["id"] = str(created.pop("_id"))
    return created


async def get_latest_valid_otp(email: str) -> Optional[Dict[str, Any]]:
    now = utcnow()
    doc = await (
        _otps_collection()
        .find({"email": email, "expires_at": {"$gt": now}})
        .sort("created_at", -1)
        .limit(1)
        .to_list(length=1)
    )
    if not doc:
        return None
    otp = doc[0]
    otp["id"] = str(otp.pop("_id"))
    return otp


async def delete_otps_for_email(email: str) -> None:
    await _otps_collection().delete_many({"email": email})

