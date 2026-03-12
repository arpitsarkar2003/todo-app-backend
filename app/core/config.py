from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Basic app settings
    APP_NAME: str = "Todo App Backend"
    APP_VERSION: str = "1.0.0"

    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "todo_app_db"

    # JWT
    JWT_SECRET_KEY: str = "CHANGE_ME_IN_ENV"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Admin seed
    ADMIN_EMAIL: str = "admin@todo.com"
    ADMIN_PASSWORD: str = "todo@pass"

    # Optional email/SMTP settings for real email sending
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = Field(default=None)
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

