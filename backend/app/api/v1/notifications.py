from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.core.database import get_db
from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse, NotificationUpdate, NotificationListResponse, NotificationSummaryResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications & Unified Inbox"])


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    provider: Optional[str] = Query(None, description="Filter by provider (gmail, whatsapp, teams, etc.)"),
    priority: Optional[str] = Query(None, description="Filter by priority (CRITICAL, HIGH, MEDIUM, LOW)"),
    category: Optional[str] = Query(None, description="Filter by category (WORK, PERSONAL, etc.)"),
    is_read: Optional[bool] = Query(None),
    is_archived: Optional[bool] = Query(False),
    action_required: Optional[bool] = Query(None),
    search: Optional[str] = Query(None, description="Search in title and content"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    base_query = select(Notification).where(Notification.user_id == current_user.id)

    if is_archived is not None:
        base_query = base_query.where(Notification.is_archived == is_archived)
    if provider:
        base_query = base_query.where(Notification.provider == provider.lower())
    if priority:
        base_query = base_query.where(Notification.priority == priority.upper())
    if category:
        base_query = base_query.where(Notification.category == category.upper())
    if is_read is not None:
        base_query = base_query.where(Notification.is_read == is_read)
    if action_required is not None:
        base_query = base_query.where(Notification.action_required == action_required)
    if search:
        search_fmt = f"%{search.strip()}%"
        base_query = base_query.where(
            (Notification.title.ilike(search_fmt)) | (Notification.content.ilike(search_fmt))
        )

    # Count total
    count_stmt = select(func.count()).select_from(base_query.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    # Count unread
    unread_stmt = select(func.count()).where(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
        Notification.is_archived == False
    )
    unread_count = (await db.execute(unread_stmt)).scalar() or 0

    # Paginated results
    offset = (page - 1) * page_size
    query = base_query.order_by(Notification.timestamp.desc()).offset(offset).limit(page_size)
    items = (await db.execute(query)).scalars().all()

    return NotificationListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        unread_count=unread_count
    )


@router.get("/summary", response_model=NotificationSummaryResponse)
async def get_notification_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Notification).where(
        Notification.user_id == current_user.id,
        Notification.is_archived == False
    )
    results = (await db.execute(stmt)).scalars().all()

    provider_counts = {}
    priority_counts = {}
    unread_count = 0
    action_required_count = 0
    critical_count = 0

    for n in results:
        provider_counts[n.provider] = provider_counts.get(n.provider, 0) + 1
        priority_counts[n.priority] = priority_counts.get(n.priority, 0) + 1
        if not n.is_read:
            unread_count += 1
        if n.action_required:
            action_required_count += 1
        if n.priority == "CRITICAL":
            critical_count += 1

    return NotificationSummaryResponse(
        total_notifications=len(results),
        unread_count=unread_count,
        action_required_count=action_required_count,
        critical_count=critical_count,
        provider_counts=provider_counts,
        priority_counts=priority_counts
    )


@router.patch("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: str,
    update: NotificationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    )
    notif = (await db.execute(stmt)).scalar_one_or_none()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    if update.is_read is not None:
        notif.is_read = update.is_read
    if update.is_archived is not None:
        notif.is_archived = update.is_archived
    if update.is_starred is not None:
        notif.is_starred = update.is_starred

    await db.commit()
    await db.refresh(notif)
    return notif
