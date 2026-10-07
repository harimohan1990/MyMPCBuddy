import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    event_type = Column(String(64), nullable=False, index=True)  # 'MCP_TOOL_EXEC', 'OAUTH_CONNECT', 'DATA_PURGE', etc.
    tool_name = Column(String(128), nullable=True)
    permission_level = Column(String(32), nullable=True)  # 'READ', 'WRITE', 'DESTRUCTIVE'
    provider = Column(String(64), nullable=True)
    status = Column(String(32), nullable=False)  # 'SUCCESS', 'CONFIRMATION_REJECTED', 'FAILED'
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    payload_summary = Column(JSON, default=dict, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    user = relationship("User", back_populates="audit_logs")
