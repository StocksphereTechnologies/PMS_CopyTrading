"""
Marketwatch schemas for 5paisa / StockSphere
MANDATORY: This file MUST be replaced for the latest data fields to work.
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List


class InstrumentData(BaseModel):
    """Schema for instrument data"""
    model_config = ConfigDict(extra='allow') # Allow extra fields to prevent crashes

    symbol: str
    exchange: str
    instrument_token: Optional[str] = None
    scrip_code: Optional[int] = None
    name: Optional[str] = None

    last_price: Optional[float] = 0.0
    change: Optional[float] = 0.0
    change_percent: Optional[float] = 0.0

    volume: Optional[int] = 0
    high: Optional[float] = 0.0
    low: Optional[float] = 0.0
    open: Optional[float] = 0.0
    close: Optional[float] = 0.0

    # Depth & OI fields
    oi: Optional[int] = 0
    ltq: Optional[int] = 0
    avg_price: Optional[float] = 0.0
    total_buy_qty: Optional[int] = 0
    total_sell_qty: Optional[int] = 0

    buy_price: Optional[float] = 0.0
    sell_price: Optional[float] = 0.0
    
    # Required for frontend table
    last_trade_time: Optional[str] = "--"
    prev_close: Optional[float] = 0.0


class MarketwatchResponse(BaseModel):
    """Schema for marketwatch response"""
    instruments: List[InstrumentData]
    total: int
    timestamp: str
    
    class Config:
        from_attributes = True