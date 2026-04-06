from fastapi import APIRouter

from .run import router as run_router
from .health import router as health_router


api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(run_router)
