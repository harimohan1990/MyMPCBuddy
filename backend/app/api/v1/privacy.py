from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func

from app.core.database import get_db
from app.models.user import User
from app.models.notification import Notification
from app.models.calendar_event import CalendarEvent
from app.models.action_item import ActionItem
from app.models.provider_account import ProviderAccount
from app.models.audit_log import AuditLog
from app.api.deps import get_current_user

router = APIRouter(prefix="/privacy", tags=["Privacy & Data Sovereignty"])


@router.get("/stats")
async def get_privacy_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    notifs_count = (await db.execute(select(func.count()).where(Notification.user_id == current_user.id))).scalar() or 0
    cal_count = (await db.execute(select(func.count()).where(CalendarEvent.user_id == current_user.id))).scalar() or 0
    actions_count = (await db.execute(select(func.count()).where(ActionItem.user_id == current_user.id))).scalar() or 0
    providers_count = (await db.execute(select(func.count()).where(ProviderAccount.user_id == current_user.id))).scalar() or 0
    audits_count = (await db.execute(select(func.count()).where(AuditLog.user_id == current_user.id))).scalar() or 0

    return {
        "user_email": current_user.email,
        "connected_providers": providers_count,
        "cached_notifications": notifs_count,
        "calendar_events": cal_count,
        "action_items": actions_count,
        "audit_logs": audits_count,
        "token_encryption": "AES-256-GCM (Authenticated at rest)",
        "zero_passwords_stored": True,
        "prompt_injection_sanitization": "Enabled",
    }


@router.post("/purge")
async def purge_cached_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Securely erases locally stored notifications, action items, and calendar events.
    Does NOT revoke provider credentials unless requested.
    """
    await db.execute(delete(Notification).where(Notification.user_id == current_user.id))
    await db.execute(delete(CalendarEvent).where(CalendarEvent.user_id == current_user.id))
    await db.execute(delete(ActionItem).where(ActionItem.user_id == current_user.id))

    audit = AuditLog(
        user_id=current_user.id,
        event_type="DATA_PURGE",
        status="SUCCESS",
        payload_summary={"scope": "notifications, calendar_events, action_items"}
    )
    db.add(audit)
    await db.commit()

    return {"status": "purged", "message": "All local notifications and calendar cache erased successfully"}


@router.post("/export")
async def export_user_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    notifs = (await db.execute(select(Notification).where(Notification.user_id == current_user.id))).scalars().all()
    actions = (await db.execute(select(ActionItem).where(ActionItem.user_id == current_user.id))).scalars().all()
    cals = (await db.execute(select(CalendarEvent).where(CalendarEvent.user_id == current_user.id))).scalars().all()

    return {
        "user": {"id": current_user.id, "email": current_user.email, "name": current_user.full_name},
        "notifications": [
            {"id": n.id, "provider": n.provider, "title": n.title, "content": n.content, "timestamp": n.timestamp.isoformat()}
            for n in notifs
        ],
        "action_items": [
            {"id": a.id, "title": a.title, "priority": a.priority, "status": a.status}
            for a in actions
        ],
        "calendar_events": [
            {"id": c.id, "summary": c.summary, "start": c.start_time.isoformat()}
            for c in cals
        ]
    }
