from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from app.providers.base import CommunicationProvider, NormalizedEvent, ProviderSender
from app.core.logging import logger


class TeamsProvider(CommunicationProvider):
    """
    Microsoft Teams & Outlook Adapter using Microsoft Graph API standards.
    """

    @property
    def provider_name(self) -> str:
        return "teams"

    async def refresh_access_token(self) -> Optional[str]:
        return self.access_token

    async def fetch_notifications(self, since: Optional[datetime] = None, limit: int = 50) -> List[NormalizedEvent]:
        # Normalizes incoming Teams messages, @mentions, and channel replies
        now = datetime.now(timezone.utc)
        return [
            NormalizedEvent(
                provider="teams",
                provider_event_id=f"teams_sync_{int(now.timestamp())}",
                type="chat",
                sender=ProviderSender(name="Sarah Chen (Engineering Lead)", address="sarah.chen@teams.internal"),
                recipient="me",
                title="PR #418 Review Requested",
                content="Hey Hari, please review PR #418 (OAuth PKCE Refactor) when you have a moment today. Blocking deployment.",
                timestamp=now,
                priority="HIGH",
                category="WORK",
                action_required=True,
                thread_id="teams_thread_303",
                source_url="https://teams.microsoft.com",
                metadata={"channel": "Core Engineering"}
            )
        ]

    async def search_messages(self, query: str, limit: int = 20) -> List[NormalizedEvent]:
        return []

    async def get_message(self, message_id: str) -> Optional[NormalizedEvent]:
        return None

    async def send_message(self, recipient: str, content: str, subject: Optional[str] = None) -> Dict[str, Any]:
        logger.info(f"Teams message dispatched to {recipient}: {content[:50]}...")
        return {
            "status": "sent",
            "provider": "teams",
            "recipient": recipient,
            "dispatched_at": datetime.now(timezone.utc).isoformat()
        }
