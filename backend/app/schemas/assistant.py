from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class AssistantQueryRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None


class ActionSuggestion(BaseModel):
    action_type: str  # "DRAFT_REPLY", "SCHEDULE_MEETING", "OPEN_LINK", "ARCHIVE"
    label: str
    tool_name: Optional[str] = None
    parameters: Dict[str, Any] = {}
    requires_confirmation: bool = True


class AssistantQueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]] = []
    suggested_actions: List[ActionSuggestion] = []
    tools_called: List[str] = []


class DailyBriefingItem(BaseModel):
    category: str
    title: str
    description: str
    priority: str
    source_provider: str
    action_required: bool
    source_url: Optional[str] = None


class DailyBriefingResponse(BaseModel):
    greeting: str
    date: str
    summary_headline: str
    urgent_items: List[DailyBriefingItem]
    calendar_overview: List[Dict[str, Any]]
    stats: Dict[str, int]
    recommended_priorities: List[str]
