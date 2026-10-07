import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(64), nullable=False)  # 'google_calendar', 'outlook_calendar'
    provider_event_id = Column(String(255), nullable=False)
    summary = Column(String(512), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(Text, nullable=True)
    meeting_link = Column(Text, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False, index=True)
    is_all_day = Column(Boolean, default=False, nullable=False)
    attendees = Column(JSON, default=list, nullable=False)
    has_conflict = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="calendar_events")

    __table_args__ = (
        UniqueConstraint("user_id", "provider", "provider_event_id", name="uq_user_calendar_event"),
    )
