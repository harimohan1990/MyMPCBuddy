from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User
from app.models.audit_log import AuditLog
from app.api.deps import get_current_user

router = APIRouter(prefix="/audit", tags=["Audit & Security Logs"])


@router.get("/logs")
async def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(AuditLog)
        .where(AuditLog.user_id == current_user.id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )
    logs = (await db.execute(stmt)).scalars().all()

    return [
        {
            "id": l.id,
            "event_type": l.event_type,
            "tool_name": l.tool_name,
            "permission_level": l.permission_level,
            "provider": l.provider,
            "status": l.status,
            "ip_address": l.ip_address,
            "payload_summary": l.payload_summary,
            "error_message": l.error_message,
            "created_at": l.created_at.isoformat(),
        }
        for l in logs
    ]
