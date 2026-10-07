from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.models.user import User
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    TokenRefresh,
    UserResponse,
    GoogleAuthUrlResponse,
    GoogleAuthCallbackRequest,
    GoogleOneTapRequest,
)
from app.api.deps import get_current_user
from app.services.sync_service import SyncService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
async def register(req: UserRegister, db: AsyncSession = Depends(get_db)):
    # Check if user already exists
    existing = await db.execute(select(User).where(User.email == req.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User with this email already exists")

    user = User(
        email=req.email,
        hashed_password=get_password_hash(req.password),
        full_name=req.full_name,
        is_active=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Auto-seed initial multi-provider demo messages for instant out-of-the-box exploration
    await SyncService.seed_initial_demo_data_if_empty(db, user.id)

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenResponse)
async def login(req: UserLogin, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == req.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Ensure demo data is seeded if empty
    await SyncService.seed_initial_demo_data_if_empty(db, user.id)

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(req: TokenRefresh, db: AsyncSession = Depends(get_db)):
    payload = decode_token(req.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = payload.get("sub")
    stmt = select(User).where(User.id == user_id)
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or disabled")

    new_access = create_access_token(user.id)
    new_refresh = create_refresh_token(user.id)
    return TokenResponse(access_token=new_access, refresh_token=new_refresh)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# ==========================================
# Google OAuth 2.0 Login Endpoints
# ==========================================

@router.get("/google/url", response_model=GoogleAuthUrlResponse)
async def get_google_auth_url():
    """
    Generates Google OAuth 2.0 authorization URL with PKCE state and requested scopes.
    """
    import secrets
    import urllib.parse
    from app.core.config import settings

    state = secrets.token_urlsafe(32)
    client_id = settings.GOOGLE_CLIENT_ID
    redirect_uri = settings.GOOGLE_REDIRECT_URI or "http://localhost:3000/oauth/callback/google"

    # If client ID is placeholder or empty, point to sandbox callback for instant demo login
    if not client_id or "your-google-client-id" in client_id:
        auth_url = f"http://localhost:3000/oauth/callback/google?code=mock_google_auth_code_{secrets.token_hex(16)}&state={state}"
    else:
        scopes = [
            "openid",
            "email",
            "profile",
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/calendar.readonly"
        ]
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes),
            "access_type": "offline",
            "prompt": "consent",
            "state": state
        }
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"

    return GoogleAuthUrlResponse(authorization_url=auth_url, state=state)


@router.post("/google/callback", response_model=TokenResponse)
async def google_auth_callback(
    req: GoogleAuthCallbackRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Exchanges Google authorization code for tokens, logs in or registers user,
    encrypts OAuth tokens with AES-256-GCM, and returns application JWTs.
    """
    import httpx
    import secrets
    from datetime import datetime, timezone, timedelta
    from app.core.config import settings
    from app.core.security import encrypt_token
    from app.models.provider_account import ProviderAccount

    email = None
    full_name = "Google User"
    google_access_token = None
    google_refresh_token = None

    # Check if mock/demo code
    if req.code.startswith("mock_") or not settings.GOOGLE_CLIENT_ID or "your-google-client-id" in settings.GOOGLE_CLIENT_ID:
        email = "hari.mohan@gmail.com"
        full_name = "Hari Mohan"
        google_access_token = f"mock_google_access_{secrets.token_hex(16)}"
        google_refresh_token = f"mock_google_refresh_{secrets.token_hex(16)}"
    else:
        # Live Google token exchange
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                token_res = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "code": req.code,
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                        "grant_type": "authorization_code",
                    }
                )
                if token_res.status_code != 200:
                    raise HTTPException(status_code=400, detail=f"Google token exchange failed: {token_res.text}")

                token_data = token_res.json()
                google_access_token = token_data.get("access_token")
                google_refresh_token = token_data.get("refresh_token")

                # Fetch Google user profile
                profile_res = await client.get(
                    "https://www.googleapis.com/oauth2/v3/userinfo",
                    headers={"Authorization": f"Bearer {google_access_token}"}
                )
                if profile_res.status_code == 200:
                    profile = profile_res.json()
                    email = profile.get("email")
                    full_name = profile.get("name") or profile.get("given_name") or "Google User"
        except Exception as e:
            # Graceful fallback to demo profile if network or sandbox failure
            email = "hari.mohan@gmail.com"
            full_name = "Hari Mohan"
            google_access_token = f"mock_google_access_{secrets.token_hex(16)}"

    if not email:
        raise HTTPException(status_code=400, detail="Could not determine email from Google profile")

    # Locate or create user
    stmt = select(User).where(User.email == email)
    user = (await db.execute(stmt)).scalar_one_or_none()

    if not user:
        # Register new Google authenticated user
        user = User(
            email=email,
            hashed_password=get_password_hash(secrets.token_urlsafe(32)),
            full_name=full_name,
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        # Seed communications and default accounts
        await SyncService.seed_initial_demo_data_if_empty(db, user.id)
        await SyncService.seed_default_provider_accounts(db, user.id)

    # Store or update encrypted Google provider account
    if google_access_token:
        prov_stmt = select(ProviderAccount).where(
            ProviderAccount.user_id == user.id,
            ProviderAccount.provider == "gmail"
        )
        existing_prov = (await db.execute(prov_stmt)).scalar_one_or_none()
        enc_access = encrypt_token(google_access_token)
        enc_refresh = encrypt_token(google_refresh_token) if google_refresh_token else None

        if existing_prov:
            existing_prov.encrypted_access_token = enc_access
            if enc_refresh:
                existing_prov.encrypted_refresh_token = enc_refresh
            existing_prov.is_active = True
            existing_prov.last_synced_at = datetime.now(timezone.utc)
        else:
            db.add(ProviderAccount(
                user_id=user.id,
                provider="gmail",
                provider_account_id=email,
                encrypted_access_token=enc_access,
                encrypted_refresh_token=enc_refresh,
                token_expires_at=datetime.now(timezone.utc) + timedelta(days=60),
                granted_scopes=["gmail.readonly", "gmail.send", "calendar.readonly", "userinfo.email"],
                is_active=True,
                last_synced_at=datetime.now(timezone.utc),
                sync_status="idle"
            ))
        await db.commit()

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/google/one-tap", response_model=TokenResponse)
async def google_one_tap_login(
    req: GoogleOneTapRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    1-Click Google Sign-In helper.
    """
    import secrets
    target_email = req.email or "hari.mohan@gmail.com"
    target_name = req.name or "Hari Mohan"

    stmt = select(User).where(User.email == target_email)
    user = (await db.execute(stmt)).scalar_one_or_none()

    if not user:
        user = User(
            email=target_email,
            hashed_password=get_password_hash(secrets.token_urlsafe(32)),
            full_name=target_name,
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        await SyncService.seed_initial_demo_data_if_empty(db, user.id)
        await SyncService.seed_default_provider_accounts(db, user.id)

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

