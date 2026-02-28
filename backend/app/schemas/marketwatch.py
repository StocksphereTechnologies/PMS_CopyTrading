# not completed yet

"""
Marketwatch schemas for request/response validation
"""
from pydantic import BaseModel
from typing import Optional, List


class InstrumentData(BaseModel):
    """Schema for instrument data"""
    symbol: str
    exchange: str
    instrument_token: Optional[str] = None
    scrip_code: Optional[int] = None  # For 5paisa
    name: Optional[str] = None
    last_price: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[int] = None
    high: Optional[float] = None
    low: Optional[float] = None
    open: Optional[float] = None
    close: Optional[float] = None


class MarketwatchResponse(BaseModel):
    """Schema for marketwatch response"""
    instruments: List[InstrumentData]
    total: int
    timestamp: str
    
    class Config:
        from_attributes = True
