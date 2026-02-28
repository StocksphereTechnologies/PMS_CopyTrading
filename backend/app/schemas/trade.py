"""
Trade schemas for request/response validation
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
    side: OrderSide = Field(..., description="BUY or SELL")
    quantity: int = Field(..., gt=0, description="Quantity to trade")
    order_type: OrderType = Field(..., description="Order type: MARKET, LIMIT, SL, SL_M")
    
    # Target execution
    account_ids: Optional[List[int]] = Field(None, description="Specific account IDs to execute on. If None, executes on ALL enabled accounts.")
    
    # Price parameters
    price: Optional[float] = Field(None, gt=0, description="Price for LIMIT/SL orders")
    trigger_price: Optional[float] = Field(None, gt=0, description="Trigger price for SL/SL_M orders")
    
    # Advanced parameters
    product: str = Field(default="MIS", description="Product type: CNC, MIS, NRML, etc.")
    disclosed_quantity: Optional[int] = Field(None, gt=0, description="Quantity to disclose publicly")
    
    # BO/CO specific (Trigger/Target/Stoploss)
    # Using specific names from frontend Trade.tsx
    Target: Optional[float] = Field(None, gt=0, description="Profit target for BO")
    Stoploss: Optional[float] = Field(None, gt=0, description="Stoploss for BO/CO")
    trailing_stoploss: Optional[float] = Field(None, gt=0, alias="Trail. Stoploss")
    
    # Metadata from UI
    variety: Optional[str] = Field("regular", description="regular, bo, co, amo")
    validity: Optional[str] = Field("DAY", description="DAY, IOC")
    tag: Optional[str] = None
    
    # UI Toggles / Orchestration
    amo: bool = Field(False, description="After Market Order")
    groupAcc: bool = Field(False, description="Group Accounts")
    diffQty: bool = Field(False, description="Different Quantities")
    multiplier: bool = Field(False, description="Use Multiplier")
    
    # Splitting
    split: str = Field("NO", description="NO, AUTO, QTY")
    splitQty: Optional[int] = Field(None, description="Quantity for split")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "RELIANCE",
                "exchange": "NSE",
                "side": "BUY",
                "quantity": 10,
                "order_type": "LIMIT",
                "price": 2500.0,
                "product": "INTRADAY",
                "variety": "regular",
                "validity": "DAY",
                "account_ids": [1]
            }
        }


class TradeExecutionDetail(BaseModel):
    """Schema for individual execution detail"""
    account_id: int
    broker: str
    order_id: Optional[str] = None
    status: OrderStatus
    executed_price: Optional[float] = None
    executed_quantity: Optional[int] = None
    error_reason: Optional[str] = None
    execution_time_ms: Optional[float] = None
    
    class Config:
        from_attributes = True


class TradeResponse(BaseModel):
    """Schema for trade response"""
    trade_id: int
    owner_id: Optional[int] = None  
    symbol: str
    exchange: str
    side: str
    quantity: int
    order_type: str
    price: Optional[float]
    created_at: datetime
    # Map 'executions' from model to 'details' in response
    details: List[TradeExecutionDetail] = Field(validation_alias="executions")
    total_execution_time_ms: Optional[float] = None  
        
    class Config:
        from_attributes = True
        populate_by_name = True  # Allow both 'details' and 'executions' as field names


class TradeListResponse(BaseModel):
    """Schema for list of trades"""
    trades: List[TradeResponse]
    total: int
