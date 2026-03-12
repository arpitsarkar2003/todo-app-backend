from fastapi import APIRouter

router = APIRouter()


@router.get("/", tags=["health"])
async def root():
    return {"message": "Todo API is running"}


@router.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}

