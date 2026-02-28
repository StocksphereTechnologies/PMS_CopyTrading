"""
Pydantic schemas for request/response validation
Field names aligned with the main StockSphere system
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ──────────────────────────────────────────────
# Account Schemas
# ──────────────────────────────────────────────

class AccountCreate(BaseModel):
    """
    Schema for creating a Zerodha account.
    Same fields the big system accepts for Zerodha accounts.
    """
    nickname: Optional[str] = Field(None, description="Friendly name for this account")
    role: str = Field(..., description="Account role: MASTER or CHILD")

    # Trading credentials (same names as big system)
    trading_login_id: str = Field(..., min_length=1, description="Zerodha Client ID (e.g. AB1234)")
    trading_password: str = Field(..., min_length=1, description="Zerodha login password")
    totp_secret_key: str = Field(..., min_length=1, description="TOTP seed/secret for 2FA")

    # Kite Connect API credentials
    api_key: str = Field(..., min_length=1, description="Kite Connect API Key")
    api_secret: str = Field(..., min_length=1, description="Kite Connect API Secret")

    # Optional settings (from big system)
    multiplier: float = Field(1.0, description="Order quantity scaling factor")
    split_freeze_limit: Optional[int] = Field(None, description="Per-account freeze limit override")
    is_enabled: bool = True


class AccountUpdate(BaseModel):
    """Schema for updating an account"""
    nickname: Optional[str] = None
    trading_login_id: Optional[str] = None
    trading_password: Optional[str] = None
    totp_secret_key: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    multiplier: Optional[float] = None
    split_freeze_limit: Optional[int] = None
    is_enabled: Optional[bool] = None


class AccountResponse(BaseModel):
    """Account response (no sensitive credentials exposed)"""
    account_id: int
    nickname: Optional[str] = None
    role: str
    trading_login_id: str
    api_key: str
    is_enabled: bool
    is_validated: bool = False
    multiplier: float = 1.0
    split_freeze_limit: Optional[int] = None
    token_generated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# Copy Trading Pair Schemas
# ──────────────────────────────────────────────

class PairCreate(BaseModel):
    """Schema for creating a master-child copy trading pair"""
    master_account_id: int = Field(..., description="Account ID of the master account")
    child_account_id: int = Field(..., description="Account ID of the child account")
    quantity_multiplier: float = Field(1.0, description="child_qty = master_qty × multiplier")
    copy_modifications: bool = Field(True, description="Whether to copy order modifications")
    copy_cancellations: bool = Field(True, description="Whether to copy order cancellations")


class PairUpdate(BaseModel):
    """Schema for updating a copy trading pair"""
    quantity_multiplier: Optional[float] = None
    copy_modifications: Optional[bool] = None
    copy_cancellations: Optional[bool] = None


class PairResponse(BaseModel):
    """Copy trading pair response"""
    pair_id: int
    master_account_id: int
    child_account_id: int
    quantity_multiplier: float
    is_active: bool
    copy_modifications: bool
    copy_cancellations: bool
    created_at: datetime
    updated_at: datetime

    # Nested account info for convenience
    master_account: Optional[AccountResponse] = None
    child_account: Optional[AccountResponse] = None

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# Copy Trade Log Schemas
# ──────────────────────────────────────────────

class CopyTradeLogResponse(BaseModel):
    """Copy trade log response"""
    log_id: int
    pair_id: int
    master_order_id: str
    child_order_id: Optional[str] = None
    tradingsymbol: str
    exchange: str
    transaction_type: str
    quantity: int
    order_type: Optional[str] = None
    product: Optional[str] = None
    price: Optional[float] = None
    status: str
    error_reason: Optional[str] = None
    master_order_time: Optional[datetime] = None
    child_order_time: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# System Status Schema
# ──────────────────────────────────────────────

class SystemStatus(BaseModel):
    """System health and active pollers status"""
    status: str = "healthy"
    version: str = "1.0.0"
    active_pollers: int = 0
    active_pairs: List[int] = []
