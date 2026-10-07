import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class ProviderAccount(Base):
    __tablename__ = "provider_accounts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(64), nullable=False)  # 'gmail', 'outlook', 'teams', 'calendar', 'github', 'whatsapp'
    provider_account_id = Column(String(255), nullable=False)  # e.g. email address or provider user id
    encrypted_access_token = Column(String, nullable=False)  # AES-256-GCM cipher
    encrypted_refresh_token = Column(String, nullable=True)  # AES-256-GCM cipher
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    granted_scopes = Column(JSON, default=list, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    sync_status = Column(String(64), default="idle", nullable=False)  # 'idle', 'syncing', 'error'
    sync_error = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="provider_accounts")

    __table_args__ = (
        UniqueConstraint("user_id", "provider", "provider_account_id", name="uq_user_provider_account"),
    )
