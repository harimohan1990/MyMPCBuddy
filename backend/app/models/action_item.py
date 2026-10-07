import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class ActionItem(Base):
    __tablename__ = "action_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    notification_id = Column(String(36), ForeignKey("notifications.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(512), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(32), default="MEDIUM", nullable=False)
    deadline = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(32), default="PENDING", nullable=False)  # 'PENDING', 'IN_PROGRESS', 'COMPLETED', 'DISMISSED'
    suggested_by = Column(String(32), default="AI", nullable=False)  # 'AI', 'RULE', 'USER'
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="action_items")
    notification = relationship("Notification", back_populates="action_items")
