"""
Fixed version of app/schemas/trade.py
Includes:
1. 'scrip_code' in TradeRequest
2. 'TradeListResponse' (fixed missing class)
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from app.models.trade import OrderSide, OrderType, OrderStatus


class TradeRequest(BaseModel):
    """Schema for trade request"""
    # Core parameters
    symbol: str = Field(..., min_length=1, description="Trading symbol (e.g., RELIANCE, INFY)")
    exchange: str = Field(..., min_length=1, description="Exchange (NSE, BSE, NFO, etc.)")
    scrip_code: Optional[int] = Field(None, description="Numeric ScripCode for 5paisa (from search result)")
    side: OrderSide = Field(..., description="BUY or SELL")
    quantity: int = Field(..., gt=0, description="Quantity to trade")
    order_type: OrderType = Field(..., description="Order type: MARKET, LIMIT, SL, SL_M")
    
    # Target execution
    account_ids: Optional[List[int]] = Field(None, description="Specific account IDs")
    
    # Price parameters
    price: Optional[float] = Field(None, gt=0, description="Price for LIMIT/SL orders")
    trigger_price: Optional[float] = Field(None, gt=0, description="Trigger price for SL/SL_M orders")
    
    # Advanced parameters
    product: str = Field(default="MIS", description="Product type: CNC, MIS, NRML, etc.")
    disclosed_quantity: Optional[int] = Field(None, gt=0, description="Quantity to disclose publicly")
    
    # BO/CO specific (Trigger/Target/Stoploss)
    Target: Optional[float] = Field(None, gt=0, description="Profit target")
    Stoploss: Optional[float] = Field(None, gt=0, description="Stoploss")
    trailing_stoploss: Optional[float] = Field(None, gt=0, alias="Trail. Stoploss")
    
    # Metadata from UI
    variety: Optional[str] = Field("regular", description="regular, bo, co, amo")
    validity: Optional[str] = Field("DAY", description="DAY, IOC")
    tag: Optional[str] = None
    
    # UI Toggles / Orchestration
    amo: bool = Field(False)
    groupAcc: bool = Field(False)
    diffQty: bool = Field(False)
    multiplier: bool = Field(False)
    
    # Splitting
    split: str = Field("NO")
    splitQty: Optional[int] = None
    
    # Used for different quantities mode
    accounts_with_qty: Optional[List[dict]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "RELIANCE",
                "exchange": "NSE",
                "scrip_code": 2885,
                "side": "BUY",
                "quantity": 10,
                "order_type": "LIMIT",
                "price": 2500.0,
                "product": "INTRADAY",
                "account_ids": [1]
            }
        }


class TradeExecutionDetail(BaseModel):
    account_id: int
    broker: str
    order_id: Optional[str] = None
    status: OrderStatus
    executed_price: Optional[float] = None
    executed_quantity: Optional[int] = None
    error_reason: Optional[str] = None # Support Text from SQLAlchemy if needed
    execution_time_ms: Optional[float] = None
    
    class Config:
        from_attributes = True


class TradeResponse(BaseModel):
    trade_id: int
    owner_id: Optional[int] = None
    symbol: str
    exchange: str
    side: str
    quantity: int
    order_type: str
    price: Optional[float]
    created_at: datetime
    details: List[TradeExecutionDetail] = Field(validation_alias="executions")
    total_execution_time_ms: Optional[float] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True


class TradeListResponse(BaseModel):
    """Schema for list of trades"""
    trades: List[TradeResponse]
    total: int