from datetime import datetime, timezone, timedelta
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User
from app.models.calendar_event import CalendarEvent
from app.api.deps import get_current_user

router = APIRouter(prefix="/calendar", tags=["Calendar"])


@router.get("/today")
async def get_today_calendar(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    now = datetime.now(timezone.utc)
    start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    end = start + timedelta(days=1)

    stmt = select(CalendarEvent).where(
        CalendarEvent.user_id == current_user.id,
        CalendarEvent.start_time >= start,
        CalendarEvent.start_time < end
    ).order_by(CalendarEvent.start_time.asc())

    events = (await db.execute(stmt)).scalars().all()

    return [
        {
            "id": e.id,
            "provider": e.provider,
            "summary": e.summary,
            "description": e.description,
            "location": e.location,
            "meeting_link": e.meeting_link,
            "start_time": e.start_time.isoformat(),
            "end_time": e.end_time.isoformat(),
            "is_all_day": e.is_all_day,
            "attendees": e.attendees,
            "has_conflict": e.has_conflict,
        }
        for e in events
    ]
