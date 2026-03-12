from datetime import datetime

from pydantic import BaseModel, EmailStr


class OTPInDB(BaseModel):
    id: str  # string version of Mongo ObjectId
    email: EmailStr
    otp_code: str
    expires_at: datetime
    created_at: datetime

