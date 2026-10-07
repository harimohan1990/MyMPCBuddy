from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional


class ProviderAccountResponse(BaseModel):
    id: str
    provider: str
    provider_account_id: str
    granted_scopes: List[str]
    is_active: bool
    last_synced_at: Optional[datetime]
    sync_status: str
    sync_error: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OAuthInitiateResponse(BaseModel):
    provider: str
    authorization_url: str
    state: str
