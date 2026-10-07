from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class ProviderSender(BaseModel):
    name: Optional[str] = "Unknown"
    address: Optional[str] = ""
    avatar_url: Optional[str] = None


class NormalizedEvent(BaseModel):
    provider: str
    provider_event_id: str
    type: str  # 'email', 'chat', 'calendar', 'pr_review', etc.
    sender: ProviderSender
    recipient: Optional[str] = None
    title: str
    content: str
    timestamp: datetime
    priority: str = "MEDIUM"  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    category: str = "INFORMATIONAL"  # 'WORK', 'PERSONAL', 'MEETING', etc.
    action_required: bool = False
    thread_id: Optional[str] = None
    source_url: Optional[str] = None
    metadata: Dict[str, Any] = {}


class ProviderSyncResult(BaseModel):
    provider: str
    account_id: str
    events_fetched: int
    new_events: int
    errors: List[str] = []


class CommunicationProvider(ABC):
    """
    Abstract Base Class for all communication service adapters
    (Gmail, Outlook, Teams, Google Calendar, GitHub, WhatsApp).
    Enforces the Provider Adapter Pattern so the core application
    never depends on vendor-specific payloads or APIs.
    """

    def __init__(self, access_token: str, refresh_token: Optional[str] = None, account_id: Optional[str] = None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.account_id = account_id

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the canonical provider identifier (e.g. 'gmail', 'teams', 'github')."""
        pass

    @abstractmethod
    async def fetch_notifications(self, since: Optional[datetime] = None, limit: int = 50) -> List[NormalizedEvent]:
        """Fetches and normalizes incoming communications/events."""
        pass

    @abstractmethod
    async def search_messages(self, query: str, limit: int = 20) -> List[NormalizedEvent]:
        """Performs search across the provider's message index."""
        pass

    @abstractmethod
    async def get_message(self, message_id: str) -> Optional[NormalizedEvent]:
        """Retrieves a specific message by its unique provider ID."""
        pass

    @abstractmethod
    async def send_message(self, recipient: str, content: str, subject: Optional[str] = None) -> Dict[str, Any]:
        """
        Sends an outgoing message through the provider.
        CRITICAL: Calls to this method must be gated by user confirmation in the MCP layer.
        """
        pass

    @abstractmethod
    async def refresh_access_token(self) -> Optional[str]:
        """Refreshes the OAuth 2.0 access token using the refresh token."""
        pass
