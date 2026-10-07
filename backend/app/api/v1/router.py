from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.calendar import router as calendar_router
from app.api.v1.providers import router as providers_router
from app.api.v1.oauth import router as oauth_router
from app.api.v1.mcp import router as mcp_router
from app.api.v1.assistant import router as assistant_router
from app.api.v1.privacy import router as privacy_router
from app.api.v1.audit import router as audit_router
from app.api.v1.infra import router as infra_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(notifications_router)
api_router.include_router(calendar_router)
api_router.include_router(providers_router)
api_router.include_router(oauth_router)
api_router.include_router(mcp_router)
api_router.include_router(assistant_router)
api_router.include_router(privacy_router)
api_router.include_router(audit_router)
api_router.include_router(infra_router)
