from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User
from app.models.provider_account import ProviderAccount
from app.schemas.provider import ProviderAccountResponse
from app.api.deps import get_current_user
from app.services.sync_service import SyncService

router = APIRouter(prefix="/providers", tags=["Providers & Connections"])


@router.get("", response_model=List[ProviderAccountResponse])
async def list_providers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ProviderAccount).where(ProviderAccount.user_id == current_user.id)
    accounts = (await db.execute(stmt)).scalars().all()
    if not accounts:
        await SyncService.seed_default_provider_accounts(db, current_user.id)
        accounts = (await db.execute(stmt)).scalars().all()
    return accounts


@router.post("/connect-all", response_model=List[ProviderAccountResponse])
async def connect_all_providers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await SyncService.seed_default_provider_accounts(db, current_user.id)
    stmt = select(ProviderAccount).where(ProviderAccount.user_id == current_user.id)
    accounts = (await db.execute(stmt)).scalars().all()
    return accounts


@router.post("/{provider_id}/sync")
async def sync_provider(
    provider_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ProviderAccount).where(
        ProviderAccount.id == provider_id,
        ProviderAccount.user_id == current_user.id
    )
    account = (await db.execute(stmt)).scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Provider account not found")

    result = await SyncService.sync_all_for_user(db, current_user.id)
    return {"status": "success", "sync_summary": result}


@router.delete("/{provider_id}")
async def disconnect_provider(
    provider_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ProviderAccount).where(
        ProviderAccount.id == provider_id,
        ProviderAccount.user_id == current_user.id
    )
    account = (await db.execute(stmt)).scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Provider account not found")

    await db.delete(account)
    await db.commit()
    return {"status": "disconnected", "id": provider_id}
