from fastapi import APIRouter, Depends
from helpers import get_settings, Settings

# Set router:
base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],
)


# Health checker:
@base_router.get("/")
async def health(app_settings: Settings = Depends(get_settings)):
    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION
    return {
        "name": app_name,
        "version": app_version,
    }
