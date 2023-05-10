from fastapi import APIRouter, Depends

from config import Settings, get_settings

router = APIRouter()


@router.get("/")
async def pong(settings: Settings = Depends(get_settings)):
    return {
        "ping": "Welcome to omniroom app",
        "environment": settings.environment,
        "testing": settings.testing,
    }
