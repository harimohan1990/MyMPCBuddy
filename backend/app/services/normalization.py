import hashlib
import json
from app.providers.base import NormalizedEvent
from app.models.notification import Notification


class NormalizationService:
    @staticmethod
    def compute_content_hash(provider: str, provider_event_id: str, content: str) -> str:
        raw = f"{provider}:{provider_event_id}:{content.strip()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @classmethod
    def event_to_notification(cls, user_id: str, event: NormalizedEvent) -> Notification:
        content_hash = cls.compute_content_hash(event.provider, event.provider_event_id, event.content)
        
        return Notification(
            user_id=user_id,
            provider=event.provider,
            provider_event_id=event.provider_event_id,
            type=event.type,
            sender=event.sender.model_dump(),
            recipient=event.recipient,
            title=event.title,
            content=event.content,
            content_hash=content_hash,
            timestamp=event.timestamp,
            priority=event.priority,
            category=event.category,
            is_read=False,
            is_archived=False,
            is_starred=False,
            action_required=event.action_required,
            thread_id=event.thread_id,
            source_url=event.source_url,
            metadata_json=event.metadata,
        )
