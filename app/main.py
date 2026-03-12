import logging

from fastapi import FastAPI

from app.core.config import settings
from app.core.database import close_client, get_db
from app.core.security import get_password_hash
from app.repositories import user_repository
from app.routes import (
    admin_auth_routes,
    admin_report_routes,
    auth_routes,
    health_routes,
    todo_routes,
)


logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
    )

    # Include routers
    app.include_router(health_routes.router)
    app.include_router(auth_routes.router)
    app.include_router(todo_routes.router)
    app.include_router(admin_auth_routes.router)
    app.include_router(admin_report_routes.router)

    @app.on_event("startup")
    async def on_startup() -> None:
        # Touch the DB so the client is created.
        _ = get_db()

        # Seed admin user if not present.
        admin = await user_repository.get_user_by_email(settings.ADMIN_EMAIL)
        if not admin:
            logger.info("Seeding initial admin user with email %s", settings.ADMIN_EMAIL)
            hashed = get_password_hash(settings.ADMIN_PASSWORD)
            await user_repository.create_user(
                {
                    "name": "Admin",
                    "email": settings.ADMIN_EMAIL,
                    "password_hash": hashed,
                    "role": "admin",
                    "is_active": True,
                    "is_verified": True,
                }
            )

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        await close_client()

    return app


app = create_app()

