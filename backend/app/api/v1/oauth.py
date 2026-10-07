import urllib.parse
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.core.security import encrypt_token
from app.models.user import User
from app.models.provider_account import ProviderAccount
from app.api.deps import get_current_user
from app.schemas.provider import OAuthInitiateResponse

router = APIRouter(prefix="/oauth", tags=["OAuth & Integrations"])


@router.get("/{provider}/authorize", response_model=OAuthInitiateResponse)
async def get_authorization_url(
    provider: str,
    current_user: User = Depends(get_current_user)
):
    state = secrets.token_urlsafe(32)
    provider_lower = provider.lower()

    if provider_lower == "google" or provider_lower == "gmail":
        if not settings.GOOGLE_CLIENT_ID:
            # Fallback direct simulated redirect URL
            auth_url = f"http://localhost:3000/providers?sandbox_connect=google&state={state}"
        else:
            scopes = [
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/gmail.send",
                "https://www.googleapis.com/auth/calendar.readonly",
                "https://www.googleapis.com/auth/userinfo.email"
            ]
            params = {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "response_type": "code",
                "scope": " ".join(scopes),
                "access_type": "offline",
                "prompt": "consent",
                "state": state
            }
            auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"

        return OAuthInitiateResponse(
            provider="gmail",
            authorization_url=auth_url,
            state=state
        )

    elif provider_lower == "microsoft" or provider_lower == "teams":
        scopes = ["User.Read", "Mail.Read", "Chat.Read", "Calendars.Read", "offline_access"]
        params = {
            "client_id": settings.MICROSOFT_CLIENT_ID or "simulated-ms-client",
            "redirect_uri": settings.MICROSOFT_REDIRECT_URI,
            "response_type": "code",
            "scope": " ".join(scopes),
            "state": state
        }
        auth_url = f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?{urllib.parse.urlencode(params)}"
        return OAuthInitiateResponse(
            provider="teams",
            authorization_url=auth_url,
            state=state
        )

    elif provider_lower == "github":
        scopes = ["read:user", "notifications", "repo"]
        params = {
            "client_id": settings.GITHUB_CLIENT_ID or "simulated-gh-client",
            "redirect_uri": settings.GITHUB_REDIRECT_URI,
            "scope": " ".join(scopes),
            "state": state
        }
        auth_url = f"https://github.com/login/oauth/authorize?{urllib.parse.urlencode(params)}"
        return OAuthInitiateResponse(
            provider="github",
            authorization_url=auth_url,
            state=state
        )

    raise HTTPException(status_code=400, detail=f"Unsupported OAuth provider: {provider}")


@router.post("/connect-sandbox")
async def connect_sandbox_provider(
    provider: str = Body(..., embed=True),
    account_email: str = Body("user@example.com", embed=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Connects or simulates connection of a provider account, encrypts mock/issued tokens using AES-256-GCM,
    and updates the database without exposing raw credentials.
    """
    provider_name = provider.lower()
    stmt = select(ProviderAccount).where(
        ProviderAccount.user_id == current_user.id,
        ProviderAccount.provider == provider_name
    )
    existing = (await db.execute(stmt)).scalar_one_or_none()

    encrypted_access = encrypt_token(f"mock_token_{provider_name}_{secrets.token_hex(16)}")
    encrypted_refresh = encrypt_token(f"mock_refresh_{provider_name}_{secrets.token_hex(16)}")

    scopes_map = {
        "gmail": ["gmail.readonly", "gmail.send", "calendar.readonly"],
        "teams": ["Chat.Read", "Mail.Read", "Calendars.Read"],
        "calendar": ["calendar.readonly", "calendar.events"],
        "github": ["read:user", "notifications", "repo"],
        "whatsapp": ["whatsapp_business_messaging (staged)"],
    }

    if existing:
        existing.is_active = True
        existing.encrypted_access_token = encrypted_access
        existing.encrypted_refresh_token = encrypted_refresh
        existing.last_synced_at = datetime.now(timezone.utc)
        existing.sync_status = "idle"
        account = existing
    else:
        account = ProviderAccount(
            user_id=current_user.id,
            provider=provider_name,
            provider_account_id=account_email,
            encrypted_access_token=encrypted_access,
            encrypted_refresh_token=encrypted_refresh,
            token_expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            granted_scopes=scopes_map.get(provider_name, ["read"]),
            is_active=True,
            last_synced_at=datetime.now(timezone.utc),
            sync_status="idle"
        )
        db.add(account)

    await db.commit()
    await db.refresh(account)
    return {"status": "connected", "provider": account.provider, "account_id": account.provider_account_id}
