"""
Position schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Position(BaseModel):
    """Unified position data for a single scrip in an account"""
    id: str = Field(..., description="Unique ID for the position (usually scrip code)")
    symbol: str = Field(..., description="Trading symbol")
    m2m: float = Field(default=0.0, description="Mark-to-Market value")
    pnl: float = Field(default=0.0, description="Total PnL")
    atpnl: float = Field(default=0.0, description="After-tax PnL (or same as m2m)")
    realpl: float = Field(default=0.0, description="Realized P&L")
    unrealpl: float = Field(default=0.0, description="Unrealized P&L")
    netqty: int = Field(default=0, description="Net quantity")
    ltp: float = Field(default=0.0, description="Last traded price")
    buyqty: int = Field(default=0, description="Total buy quantity")
    sellqty: int = Field(default=0, description="Total sell quantity")
    buyval: float = Field(default=0.0, description="Total buy value")
    sellval: float = Field(default=0.0, description="Total sell value")
    netval: float = Field(default=0.0, description="Net value")
    bavg: float = Field(default=0.0, description="Buy average price")
    savg: float = Field(default=0.0, description="Sell average price")
    state: str = Field(default="", description="Position state (e.g. CarryForward, Intraday)")
    direction: str = Field(default="NEUTRAL", description="LONG, SHORT, or NEUTRAL")
    type: str = Field(default="", description="Product type (e.g. CNC, MIS)")
    category: str = Field(default="", description="Exchange or category")
    broker: str = Field(..., description="Broker name (e.g. 5Paisa, Zerodha)")
    overqty: int = Field(default=0, description="Overnight quantity")
    multiplier: float = Field(default=1.0, description="Lot size / multiplier")
    exch: str = Field(default="", description="Exchange (NSE, BSE, etc.)")
    brexch: str = Field(default="", description="Broker-specific exchange")
    brsymbol: str = Field(default="", description="Broker-specific symbol")
    day: str = Field(default="DAY", description="DAY or NET position")
    platform: str = Field(default="WEB", description="Source platform")
    accid: str = Field(..., description="Trading login ID (Broker Client Code)")
    account_id: int = Field(..., description="Internal account ID")
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class PositionListResponse(BaseModel):
    """Response for list of positions"""
    positions: List[Position]
    total_positions: int
    active_positions: int  # count where netqty != 0
