from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.notification import Notification
from app.models.calendar_event import CalendarEvent
from app.models.action_item import ActionItem
from app.schemas.assistant import DailyBriefingResponse, DailyBriefingItem


class BriefingService:
    @staticmethod
    async def generate_daily_briefing(db: AsyncSession, user_id: str, user_name: str) -> DailyBriefingResponse:
        now = datetime.now(timezone.utc)
        start_of_day = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
        end_of_day = start_of_day + timedelta(days=1)

        # Query urgent / high priority unread notifications
        notif_stmt = (
            select(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_archived == False,
            )
            .order_by(Notification.timestamp.desc())
            .limit(10)
        )
        notifs = (await db.execute(notif_stmt)).scalars().all()

        # Query calendar events for today
        cal_stmt = (
            select(CalendarEvent)
            .where(
                CalendarEvent.user_id == user_id,
                CalendarEvent.start_time >= start_of_day,
                CalendarEvent.start_time < end_of_day,
            )
            .order_by(CalendarEvent.start_time.asc())
        )
        calendar_events = (await db.execute(cal_stmt)).scalars().all()

        # Query pending action items
        action_stmt = (
            select(ActionItem)
            .where(
                ActionItem.user_id == user_id,
                ActionItem.status == "PENDING"
            )
            .order_by(ActionItem.created_at.desc())
        )
        action_items = (await db.execute(action_stmt)).scalars().all()

        # Build urgent items
        urgent_items: List[DailyBriefingItem] = []
        for n in notifs:
            if n.priority in ("CRITICAL", "HIGH") or n.action_required:
                urgent_items.append(
                    DailyBriefingItem(
                        category=n.category,
                        title=n.title,
                        description=f"From {n.sender.get('name', 'Unknown')}: {n.content[:160]}",
                        priority=n.priority,
                        source_provider=n.provider,
                        action_required=n.action_required,
                        source_url=n.source_url
                    )
                )

        cal_overview = [
            {
                "id": c.id,
                "summary": c.summary,
                "time": c.start_time.strftime("%I:%M %p"),
                "location": c.location,
                "link": c.meeting_link,
                "conflict": c.has_conflict,
            }
            for c in calendar_events
        ]

        # Recommended priorities synthesis
        priorities: List[str] = []
        if any("PR" in item.title or "review" in item.title.lower() for item in urgent_items):
            priorities.append("Review pending pull request blockers on GitHub/Teams")
        if any("interview" in item.title.lower() for item in urgent_items):
            priorities.append("Respond to interview schedule confirmation email")
        if calendar_events:
            first_meeting = calendar_events[0]
            priorities.append(f"Prepare for '{first_meeting.summary}' at {first_meeting.start_time.strftime('%I:%M %p')}")
        if not priorities:
            priorities.append("Review unified inbox for unread action items")

        stats = {
            "total_notifications": len(notifs),
            "urgent_items": len(urgent_items),
            "calendar_events": len(calendar_events),
            "pending_action_items": len(action_items),
        }

        first_name = user_name.split()[0] if user_name else "Hari"

        return DailyBriefingResponse(
            greeting=f"Good morning, {first_name}",
            date=now.strftime("%A, %B %d, %Y"),
            summary_headline=f"You have {len(urgent_items)} urgent items requiring attention and {len(calendar_events)} meetings scheduled today.",
            urgent_items=urgent_items[:5],
            calendar_overview=cal_overview,
            stats=stats,
            recommended_priorities=priorities[:4],
        )
