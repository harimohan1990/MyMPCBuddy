from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.provider_account import ProviderAccount
from app.models.notification import Notification
from app.models.action_item import ActionItem
from app.models.calendar_event import CalendarEvent
from app.providers.registry import ProviderRegistry
from app.services.normalization import NormalizationService
from app.core.logging import logger


class SyncService:
    @staticmethod
    async def sync_all_for_user(db: AsyncSession, user_id: str) -> Dict[str, Any]:
        """
        Synchronizes all active connected provider accounts for a user.
        """
        stmt = select(ProviderAccount).where(
            ProviderAccount.user_id == user_id,
            ProviderAccount.is_active == True
        )
        result = await db.execute(stmt)
        accounts = result.scalars().all()

        sync_summary = {
            "total_accounts": len(accounts),
            "synced": 0,
            "failed": 0,
            "new_notifications": 0,
            "details": []
        }

        for account in accounts:
            account.sync_status = "syncing"
            await db.commit()

            try:
                provider = ProviderRegistry.get(
                    name=account.provider,
                    encrypted_access_token=account.encrypted_access_token,
                    encrypted_refresh_token=account.encrypted_refresh_token,
                    account_id=account.provider_account_id
                )

                if not provider:
                    account.sync_status = "error"
                    account.sync_error = f"Unsupported provider: {account.provider}"
                    sync_summary["failed"] += 1
                    continue

                events = await provider.fetch_notifications(limit=50)
                new_count = 0

                for event in events:
                    # Check deduplication
                    chk_stmt = select(Notification).where(
                        Notification.user_id == user_id,
                        Notification.provider == event.provider,
                        Notification.provider_event_id == event.provider_event_id
                    )
                    existing = (await db.execute(chk_stmt)).scalar_one_or_none()
                    if not existing:
                        notification = NormalizationService.event_to_notification(user_id, event)
                        db.add(notification)
                        await db.flush()

                        # Auto-extract action item if action_required
                        if notification.action_required:
                            action_item = ActionItem(
                                user_id=user_id,
                                notification_id=notification.id,
                                title=f"Action: {notification.title}",
                                description=f"Extracted from {notification.provider}: {notification.content[:200]}",
                                priority=notification.priority,
                                deadline=datetime.now(timezone.utc) + timedelta(days=1),
                                status="PENDING",
                                suggested_by="RULE"
                            )
                            db.add(action_item)

                        new_count += 1

                account.last_synced_at = datetime.now(timezone.utc)
                account.sync_status = "idle"
                account.sync_error = None
                sync_summary["synced"] += 1
                sync_summary["new_notifications"] += new_count
                sync_summary["details"].append({
                    "provider": account.provider,
                    "account_id": account.provider_account_id,
                    "new_items": new_count
                })

            except Exception as e:
                logger.error(f"Sync error for user {user_id}, provider {account.provider}: {str(e)}")
                account.sync_status = "error"
                account.sync_error = str(e)
                sync_summary["failed"] += 1

        await db.commit()
        return sync_summary

    @staticmethod
    async def seed_initial_demo_data_if_empty(db: AsyncSession, user_id: str):
        """
        Populates realistic multi-provider notifications & calendar events
        for first-time setup so the inbox and dashboard are immediately functional.
        """
        chk = await db.execute(select(Notification).where(Notification.user_id == user_id))
        if chk.scalars().first():
            return

        now = datetime.now(timezone.utc)

        sample_notifications = [
            {
                "provider": "whatsapp",
                "provider_event_id": "wa_msg_101",
                "type": "chat",
                "sender": {"name": "Rahul Verma", "address": "+15550192834", "avatar_url": None},
                "recipient": "me",
                "title": "Project Alpha Sync",
                "content": "Can we discuss the project deliverables at 5 PM today? Let me know if that works.",
                "priority": "HIGH",
                "category": "WORK",
                "action_required": True,
                "timestamp": now - timedelta(minutes=25),
                "thread_id": "wa_thread_101",
                "source_url": "https://web.whatsapp.com",
            },
            {
                "provider": "gmail",
                "provider_event_id": "gmail_msg_202",
                "type": "email",
                "sender": {"name": "Elena Rostova (HR)", "address": "elena.hr@acmecorp.com", "avatar_url": None},
                "recipient": "me",
                "title": "Interview schedule confirmation: Staff Distributed Systems Engineer",
                "content": "Hi Hari, Please confirm your availability for the panel interview scheduled for tomorrow at 2:00 PM EST. Details and Zoom link attached.",
                "priority": "HIGH",
                "category": "WORK",
                "action_required": True,
                "timestamp": now - timedelta(hours=1, minutes=10),
                "thread_id": "gmail_thread_202",
                "source_url": "https://mail.google.com",
            },
            {
                "provider": "teams",
                "provider_event_id": "teams_msg_303",
                "type": "chat",
                "sender": {"name": "Sarah Chen (Engineering Lead)", "address": "sarah.chen@teams.internal", "avatar_url": None},
                "recipient": "me",
                "title": "PR #418 Review Requested",
                "content": "Hey Hari, please review PR #418 (OAuth PKCE Refactor) when you have a moment today. Blocking deployment.",
                "priority": "HIGH",
                "category": "WORK",
                "action_required": True,
                "timestamp": now - timedelta(hours=2),
                "thread_id": "teams_thread_303",
                "source_url": "https://teams.microsoft.com",
            },
            {
                "provider": "calendar",
                "provider_event_id": "cal_evt_404",
                "type": "calendar",
                "sender": {"name": "Google Calendar", "address": "calendar-notification@google.com", "avatar_url": None},
                "recipient": "me",
                "title": "Architecture Review: Core MCP Gateway",
                "content": "Team meeting starts in 30 minutes in Meeting Room B and Google Meet.",
                "priority": "CRITICAL",
                "category": "MEETING",
                "action_required": False,
                "timestamp": now - timedelta(minutes=5),
                "thread_id": "cal_evt_404",
                "source_url": "https://calendar.google.com",
            },
            {
                "provider": "github",
                "provider_event_id": "gh_alert_505",
                "type": "pr_review",
                "sender": {"name": "github-actions[bot]", "address": "notifications@github.com", "avatar_url": None},
                "recipient": "me",
                "title": "CI Build Failed on main: Commit 7f2b9a",
                "content": "Workflow 'Production Test Suite' failed on job 'Integration Tests (PostgreSQL 16)'. 2 tests failed.",
                "priority": "MEDIUM",
                "category": "WORK",
                "action_required": True,
                "timestamp": now - timedelta(hours=3, minutes=15),
                "thread_id": "gh_pr_505",
                "source_url": "https://github.com",
            },
            {
                "provider": "gmail",
                "provider_event_id": "gmail_msg_606",
                "type": "email",
                "sender": {"name": "Stripe Billing", "address": "invoicing@stripe.com", "avatar_url": None},
                "recipient": "me",
                "title": "Invoice for Cloud Infrastructure (Receipt #3829)",
                "content": "Your monthly invoice for Cloud Compute and Redis instances is ready. Amount charged: $42.50.",
                "priority": "LOW",
                "category": "FINANCE",
                "action_required": False,
                "timestamp": now - timedelta(hours=6),
                "thread_id": "gmail_thread_606",
                "source_url": "https://mail.google.com",
            }
        ]

        for s in sample_notifications:
            content_hash = NormalizationService.compute_content_hash(s["provider"], s["provider_event_id"], s["content"])
            notif = Notification(
                user_id=user_id,
                provider=s["provider"],
                provider_event_id=s["provider_event_id"],
                type=s["type"],
                sender=s["sender"],
                recipient=s["recipient"],
                title=s["title"],
                content=s["content"],
                content_hash=content_hash,
                timestamp=s["timestamp"],
                priority=s["priority"],
                category=s["category"],
                is_read=False,
                is_archived=False,
                is_starred=False,
                action_required=s["action_required"],
                thread_id=s["thread_id"],
                source_url=s["source_url"],
                metadata_json={},
            )
            db.add(notif)
            await db.flush()

            if s["action_required"]:
                db.add(ActionItem(
                    user_id=user_id,
                    notification_id=notif.id,
                    title=s["title"],
                    description=s["content"][:200],
                    priority=s["priority"],
                    deadline=now + timedelta(hours=8),
                    status="PENDING",
                    suggested_by="RULE"
                ))

        # Sample Calendar Events
        sample_calendar_events = [
            {
                "provider": "google_calendar",
                "provider_event_id": "cal_ev_1",
                "summary": "Core MCP Gateway Architecture Review",
                "description": "Discuss tiered permissions and token encryption.",
                "location": "Virtual / Meet",
                "meeting_link": "https://meet.google.com/abc-defg-hij",
                "start_time": now + timedelta(minutes=30),
                "end_time": now + timedelta(minutes=90),
                "is_all_day": False,
                "attendees": ["alex@company.com", "sarah@company.com"],
                "has_conflict": False,
            },
            {
                "provider": "google_calendar",
                "provider_event_id": "cal_ev_2",
                "summary": "1:1 with Engineering Manager",
                "description": "Sprint review & Q4 roadmap review.",
                "location": "Zoom",
                "meeting_link": "https://zoom.us/j/123456789",
                "start_time": now + timedelta(hours=3),
                "end_time": now + timedelta(hours=3, minutes=30),
                "is_all_day": False,
                "attendees": ["manager@company.com"],
                "has_conflict": False,
            },
            {
                "provider": "outlook_calendar",
                "provider_event_id": "cal_ev_3",
                "summary": "Distributed Systems Interview Panel",
                "description": "Technical panel for Senior Backend Engineer candidate.",
                "location": "Teams Call",
                "meeting_link": "https://teams.microsoft.com/l/meetup-join/199",
                "start_time": now + timedelta(hours=5),
                "end_time": now + timedelta(hours=6),
                "is_all_day": False,
                "attendees": ["recruiter@acme.com", "candidate@gmail.com"],
                "has_conflict": False,
            }
        ]

        for cev in sample_calendar_events:
            db.add(CalendarEvent(
                user_id=user_id,
                provider=cev["provider"],
                provider_event_id=cev["provider_event_id"],
                summary=cev["summary"],
                description=cev["description"],
                location=cev["location"],
                meeting_link=cev["meeting_link"],
                start_time=cev["start_time"],
                end_time=cev["end_time"],
                is_all_day=cev["is_all_day"],
                attendees=cev["attendees"],
                has_conflict=cev["has_conflict"]
            ))

        await db.commit()

    @staticmethod
    async def seed_default_provider_accounts(db: AsyncSession, user_id: str):
        """
        Connects default provider accounts for Gmail, Teams, GitHub, and WhatsApp.
        """
        from app.models.provider_account import ProviderAccount
        from app.core.security import encrypt_token

        now = datetime.now(timezone.utc)
        providers_data = [
            {
                "provider": "gmail",
                "account_id": "hari.mohan@gmail.com",
                "scopes": ["gmail.readonly", "gmail.send", "calendar.readonly", "userinfo.email"]
            },
            {
                "provider": "teams",
                "account_id": "hari.mohan@teams.enterprise.com",
                "scopes": ["Mail.Read", "Chat.Read", "Calendars.Read", "User.Read"]
            },
            {
                "provider": "github",
                "account_id": "harimohan",
                "scopes": ["read:user", "notifications", "repo"]
            },
            {
                "provider": "whatsapp",
                "account_id": "+15550192834 (Official Cloud API)",
                "scopes": ["whatsapp_business_messaging (Meta Cloud API isolated)"]
            }
        ]

        for p in providers_data:
            chk = await db.execute(select(ProviderAccount).where(
                ProviderAccount.user_id == user_id,
                ProviderAccount.provider == p["provider"]
            ))
            existing = chk.scalars().first()
            if not existing:
                db.add(ProviderAccount(
                    user_id=user_id,
                    provider=p["provider"],
                    provider_account_id=p["account_id"],
                    encrypted_access_token=encrypt_token(f"demo_access_token_{p['provider']}_active"),
                    encrypted_refresh_token=encrypt_token(f"demo_refresh_token_{p['provider']}_active"),
                    token_expires_at=now + timedelta(days=90),
                    granted_scopes=p["scopes"],
                    is_active=True,
                    last_synced_at=now,
                    sync_status="idle"
                ))
            else:
                existing.is_active = True
                existing.last_synced_at = now
                existing.sync_status = "idle"

        await db.commit()
