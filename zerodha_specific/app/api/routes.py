"""
API Routes for Zerodha Trade Copier
"""
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.encryption import encryption_service
from app.models.models import ZerodhaAccount, CopyTradingPair, CopyTradeLog
from app.schemas.schemas import (
    AccountCreate, AccountUpdate, AccountResponse,
    PairCreate, PairUpdate, PairResponse,
    CopyTradeLogResponse, SystemStatus,
)
from app.services.auto_login import auto_login_service
from app.services.order_poller import order_poller

logger = logging.getLogger(__name__)
router = APIRouter()


# ══════════════════════════════════════════════
# Account Endpoints
# ══════════════════════════════════════════════

@router.post("/accounts", response_model=AccountResponse, tags=["Accounts"])
async def create_account(payload: AccountCreate, db: AsyncSession = Depends(get_db)):
    """Add a Zerodha account (role: MASTER or CHILD)"""
    role = payload.role.upper()
    if role not in ("MASTER", "CHILD"):
        raise HTTPException(400, "Role must be MASTER or CHILD")

    account = ZerodhaAccount(
        nickname=payload.nickname,
        role=role,
        trading_login_id=payload.trading_login_id,
        encrypted_password=encryption_service.encrypt(payload.trading_password),
        encrypted_totp_secret=encryption_service.encrypt(payload.totp_secret_key),
        api_key=payload.api_key,
        api_secret=payload.api_secret,
        multiplier=payload.multiplier,
        split_freeze_limit=payload.split_freeze_limit,
        is_enabled=payload.is_enabled,
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    logger.info(f"Created {role} account: {account.account_id} ({account.trading_login_id})")
    return account


@router.get("/accounts", response_model=List[AccountResponse], tags=["Accounts"])
async def list_accounts(db: AsyncSession = Depends(get_db)):
    """List all Zerodha accounts"""
    result = await db.execute(select(ZerodhaAccount).order_by(ZerodhaAccount.account_id))
    return result.scalars().all()


@router.get("/accounts/{account_id}", response_model=AccountResponse, tags=["Accounts"])
async def get_account(account_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific account"""
    account = await db.get(ZerodhaAccount, account_id)
    if not account:
        raise HTTPException(404, "Account not found")
    return account


@router.put("/accounts/{account_id}", response_model=AccountResponse, tags=["Accounts"])
async def update_account(
    account_id: int, payload: AccountUpdate, db: AsyncSession = Depends(get_db)
):
    """Update an account's settings"""
    account = await db.get(ZerodhaAccount, account_id)
    if not account:
        raise HTTPException(404, "Account not found")

    update_data = payload.model_dump(exclude_unset=True)

    # Encrypt sensitive fields if provided
    if "trading_password" in update_data and update_data["trading_password"]:
        account.encrypted_password = encryption_service.encrypt(update_data.pop("trading_password"))
    if "totp_secret_key" in update_data and update_data["totp_secret_key"]:
        account.encrypted_totp_secret = encryption_service.encrypt(update_data.pop("totp_secret_key"))

    for field, value in update_data.items():
        if hasattr(account, field):
            setattr(account, field, value)

    await db.commit()
    await db.refresh(account)
    return account


@router.delete("/accounts/{account_id}", tags=["Accounts"])
async def delete_account(account_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an account"""
    account = await db.get(ZerodhaAccount, account_id)
    if not account:
        raise HTTPException(404, "Account not found")
    await db.delete(account)
    await db.commit()
    return {"message": f"Account {account_id} deleted"}


@router.post("/accounts/{account_id}/login", tags=["Accounts"])
async def login_account(account_id: int, db: AsyncSession = Depends(get_db)):
    """Trigger manual login for an account"""
    account = await db.get(ZerodhaAccount, account_id)
    if not account:
        raise HTTPException(404, "Account not found")

    password = encryption_service.decrypt(account.encrypted_password)
    totp_secret = encryption_service.decrypt(account.encrypted_totp_secret)

    result = await auto_login_service.login(
        client_id=account.trading_login_id,
        password=password,
        totp_secret=totp_secret,
        api_key=account.api_key,
        api_secret=account.api_secret,
    )

    if result.get("success"):
        account.access_token = result["access_token"]
        account.token_generated_at = result["token_generated_at"]
        account.is_validated = True
        await db.commit()
        return {"message": "Login successful", "token_generated_at": str(account.token_generated_at)}
    else:
        raise HTTPException(400, f"Login failed: {result.get('error')}")


# ══════════════════════════════════════════════
# Copy Trading Pair Endpoints
# ══════════════════════════════════════════════

@router.post("/pairs", response_model=PairResponse, tags=["Pairs"])
async def create_pair(payload: PairCreate, db: AsyncSession = Depends(get_db)):
    """Create a master-child copy trading pair"""
    # Validate accounts exist
    master = await db.get(ZerodhaAccount, payload.master_account_id)
    child = await db.get(ZerodhaAccount, payload.child_account_id)

    if not master:
        raise HTTPException(404, f"Master account {payload.master_account_id} not found")
    if not child:
        raise HTTPException(404, f"Child account {payload.child_account_id} not found")
    if master.role != "MASTER":
        raise HTTPException(400, f"Account {payload.master_account_id} is not a MASTER")
    if child.role != "CHILD":
        raise HTTPException(400, f"Account {payload.child_account_id} is not a CHILD")
    if payload.master_account_id == payload.child_account_id:
        raise HTTPException(400, "Master and child cannot be the same account")

    pair = CopyTradingPair(
        master_account_id=payload.master_account_id,
        child_account_id=payload.child_account_id,
        quantity_multiplier=payload.quantity_multiplier,
        copy_modifications=payload.copy_modifications,
        copy_cancellations=payload.copy_cancellations,
        is_active=False,
    )
    db.add(pair)
    await db.commit()
    await db.refresh(pair)
    logger.info(f"Created pair {pair.pair_id}: {payload.master_account_id} → {payload.child_account_id}")

    # Re-fetch with eager loading to avoid MissingGreenlet on relationship access
    result = await db.execute(
        select(CopyTradingPair)
        .options(selectinload(CopyTradingPair.master_account), selectinload(CopyTradingPair.child_account))
        .where(CopyTradingPair.pair_id == pair.pair_id)
    )
    return result.scalar_one()


@router.get("/pairs", response_model=List[PairResponse], tags=["Pairs"])
async def list_pairs(db: AsyncSession = Depends(get_db)):
    """List all copy trading pairs"""
    result = await db.execute(
        select(CopyTradingPair)
        .options(
            selectinload(CopyTradingPair.master_account),
            selectinload(CopyTradingPair.child_account),
        )
        .order_by(CopyTradingPair.pair_id)
    )
    return result.scalars().all()


@router.put("/pairs/{pair_id}", response_model=PairResponse, tags=["Pairs"])
async def update_pair(
    pair_id: int, payload: PairUpdate, db: AsyncSession = Depends(get_db)
):
    """Update pair settings (multiplier, flags)"""
    pair = await db.get(CopyTradingPair, pair_id)
    if not pair:
        raise HTTPException(404, "Pair not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(pair, field, value)

    await db.commit()
    await db.refresh(pair)

    # Re-fetch with eager loading to avoid MissingGreenlet
    result = await db.execute(
        select(CopyTradingPair)
        .options(selectinload(CopyTradingPair.master_account), selectinload(CopyTradingPair.child_account))
        .where(CopyTradingPair.pair_id == pair.pair_id)
    )
    return result.scalar_one()


@router.delete("/pairs/{pair_id}", tags=["Pairs"])
async def delete_pair(pair_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a pair (stops polling first)"""
    pair = await db.get(CopyTradingPair, pair_id)
    if not pair:
        raise HTTPException(404, "Pair not found")

    if pair_id in order_poller.active_pair_ids:
        await order_poller.stop_pair(pair_id)

    await db.delete(pair)
    await db.commit()
    return {"message": f"Pair {pair_id} deleted"}


# ── Start / Stop Copy Trading ──

@router.post("/pairs/{pair_id}/start", tags=["Pairs"])
async def start_copy_trading(pair_id: int, db: AsyncSession = Depends(get_db)):
    """Start copy trading for a pair (begins polling master's orders)"""
    pair = await db.get(CopyTradingPair, pair_id)
    if not pair:
        raise HTTPException(404, "Pair not found")

    if pair_id in order_poller.active_pair_ids:
        return {"message": f"Pair {pair_id} is already active"}

    # Ensure both accounts are logged in
    master = await db.get(ZerodhaAccount, pair.master_account_id)
    child = await db.get(ZerodhaAccount, pair.child_account_id)

    master_ok = await auto_login_service.ensure_valid_token(master)
    child_ok = await auto_login_service.ensure_valid_token(child)

    if not master_ok:
        raise HTTPException(400, "Master account login failed — check credentials")
    if not child_ok:
        raise HTTPException(400, "Child account login failed — check credentials")

    # Persist token updates
    db.add(master)
    db.add(child)

    pair.is_active = True
    await db.commit()

    await order_poller.start_pair(pair_id)
    return {"message": f"Copy trading started for pair {pair_id}"}


@router.post("/pairs/{pair_id}/stop", tags=["Pairs"])
async def stop_copy_trading(pair_id: int, db: AsyncSession = Depends(get_db)):
    """Stop copy trading for a pair"""
    pair = await db.get(CopyTradingPair, pair_id)
    if not pair:
        raise HTTPException(404, "Pair not found")

    await order_poller.stop_pair(pair_id)
    pair.is_active = False
    await db.commit()
    return {"message": f"Copy trading stopped for pair {pair_id}"}


# ══════════════════════════════════════════════
# Copy Trade Log Endpoints
# ══════════════════════════════════════════════

@router.get("/pairs/{pair_id}/logs", response_model=List[CopyTradeLogResponse], tags=["Logs"])
async def get_copy_trade_logs(
    pair_id: int, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    """Get copy trade history for a pair"""
    result = await db.execute(
        select(CopyTradeLog)
        .where(CopyTradeLog.pair_id == pair_id)
        .order_by(CopyTradeLog.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


# ══════════════════════════════════════════════
# System Status
# ══════════════════════════════════════════════

@router.get("/status", response_model=SystemStatus, tags=["System"])
async def system_status():
    """System health check and active poller status"""
    return SystemStatus(
        status="healthy",
        version="1.0.0",
        active_pollers=order_poller.active_count,
        active_pairs=order_poller.active_pair_ids,
    )
