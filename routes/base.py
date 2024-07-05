import os
from fastapi import APIRouter

base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],
)


# Get request
@base_router.get("/")
async def health():
    app_name = os.getenv("APP_NAME")
    app_version = os.getenv("APP_VERSION")
    return {
        "name": app_name,
        "version": app_version,
    }
