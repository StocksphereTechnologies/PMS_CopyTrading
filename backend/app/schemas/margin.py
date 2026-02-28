"""
Margin schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SegmentType(str, Enum):
    """Segment type enum"""
    EQUITY = "equity"
    COMMODITY = "commodity"
    TOTAL = "total"


class MarginAvailable(BaseModel):
    """Available margin details"""
    cash: float = Field(default=0.0, description="Available cash")
    opening_balance: float = Field(default=0.0, description="Opening balance")
    live_balance: float = Field(default=0.0, description="Live balance")
    collateral: float = Field(default=0.0, description="Collateral value")
    adhoc_margin: float = Field(default=0.0, description="Adhoc margin")
    intraday_payin: float = Field(default=0.0, description="Intraday payin")


class MarginUtilised(BaseModel):
    """Utilised margin details"""
    debits: float = Field(default=0.0, description="Total debits")
    exposure: float = Field(default=0.0, description="Exposure margin")
    m2m_realised: float = Field(default=0.0, description="Realised M2M")
    m2m_unrealised: float = Field(default=0.0, description="Unrealised M2M")
    option_premium: float = Field(default=0.0, description="Option premium")
    payout: float = Field(default=0.0, description="Payout amount")
    span: float = Field(default=0.0, description="SPAN margin")
    holding_sales: float = Field(default=0.0, description="Holding sales")
    turnover: float = Field(default=0.0, description="Turnover")
    liquid_collateral: float = Field(default=0.0, description="Liquid collateral")
    stock_collateral: float = Field(default=0.0, description="Stock collateral")
    delivery: float = Field(default=0.0, description="Delivery margin")


class SegmentMargin(BaseModel):
    """Margin details for a specific segment"""
    enabled: bool = Field(default=True, description="Whether segment is enabled")
    net: float = Field(default=0.0, description="Net available margin")
    available: MarginAvailable = Field(default_factory=MarginAvailable, description="Available margins")
    utilised: MarginUtilised = Field(default_factory=MarginUtilised, description="Utilised margins")


class AccountMargin(BaseModel):
    """Margin data for a single account"""
    account_id: int
    broker_name: str
    nickname: Optional[str] = None
    trading_login_id: str
    equity: Optional[SegmentMargin] = None
    commodity: Optional[SegmentMargin] = None
    status: Optional[str] = None  # e.g. 'session_invalid' when login failed
    error: Optional[str] = None   # human-readable error message
    last_updated: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MarginListResponse(BaseModel):
    """Response for list of margins"""
    margins: List[AccountMargin]
    total_accounts: int
