from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional, Dict, Any


class SenderSchema(BaseModel):
    name: Optional[str] = "Unknown"
    address: Optional[str] = ""
    avatar_url: Optional[str] = None


class NotificationResponse(BaseModel):
    id: str
    provider: str
    provider_event_id: str
    type: str
    sender: SenderSchema
    recipient: Optional[str]
    title: str
    content: str
    timestamp: datetime
    priority: str
    category: str
    is_read: bool
    is_archived: bool
    is_starred: bool
    action_required: bool
    thread_id: Optional[str]
    source_url: Optional[str]
    metadata_json: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_archived: Optional[bool] = None
    is_starred: Optional[bool] = None


class NotificationListResponse(BaseModel):
    items: List[NotificationResponse]
    total: int
    page: int
    page_size: int
    unread_count: int


class NotificationSummaryResponse(BaseModel):
    total_notifications: int
    unread_count: int
    action_required_count: int
    critical_count: int
    provider_counts: Dict[str, int]
    priority_counts: Dict[str, int]
