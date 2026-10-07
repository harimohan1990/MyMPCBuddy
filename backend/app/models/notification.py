import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON, Text, UniqueConstraint, Index
from sqlalchemy.orm import relationship

from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(64), nullable=False, index=True)
    provider_event_id = Column(String(255), nullable=False)
    type = Column(String(64), nullable=False)  # 'email', 'chat', 'calendar', 'pr_review', etc.
    sender = Column(JSON, nullable=False)      # {"name": "...", "address": "...", "avatar_url": "..."}
    recipient = Column(String(255), nullable=True)
    title = Column(String(512), nullable=False)
    content = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=False, index=True)  # SHA-256 for deduplication
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    priority = Column(String(32), default="MEDIUM", nullable=False, index=True)  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    category = Column(String(64), default="INFORMATIONAL", nullable=False, index=True)  # 'WORK', 'PERSONAL', etc.
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    is_archived = Column(Boolean, default=False, nullable=False, index=True)
    is_starred = Column(Boolean, default=False, nullable=False)
    action_required = Column(Boolean, default=False, nullable=False, index=True)
    thread_id = Column(String(255), nullable=True)
    source_url = Column(Text, nullable=True)
    metadata_json = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="notifications")
    action_items = relationship("ActionItem", back_populates="notification")

    __table_args__ = (
        UniqueConstraint("user_id", "provider", "provider_event_id", name="uq_user_provider_event"),
        Index("idx_user_provider_priority", "user_id", "priority", "is_read"),
    )
