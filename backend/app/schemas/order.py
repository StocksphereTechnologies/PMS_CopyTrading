"""
Order schemas for request/response validation
"""

from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class Order(BaseModel):
    """Unified order schema"""

    symbol: str = Field(..., description="Trading symbol")
    trdAcc: str = Field(..., description="Trading account id")
    pseAcc: str = Field(default="", description="Pseudo account")

    id: str = Field(..., description="Order ID")
    updateTime: str = Field(default="", description="Order update time")
    status: str = Field(default="", description="Order status")

    qty: int = Field(default=0, description="Order quantity")
    price: float = Field(default=0.0, description="Order price")

    variety: str = Field(default="")
    trade: str = Field(default="")
    order: str = Field(default="")
    product: str = Field(default="")

    exch: str = Field(default="")
    trigPrc: float = Field(default=0.0)

    fillQty: int = Field(default=0)
    pendQty: int = Field(default=0)

    avgPrc: float = Field(default=0.0)

    exchId: str = Field(default="")
    parentId: str = Field(default="")

    discQty: int = Field(default=0)

    amo: bool = Field(default=False)

    validity: str = Field(default="")
    rejectReason: str = Field(default="")

    brStatus: str = Field(default="")
    brExch: str = Field(default="")
    brSymbol: str = Field(default="")

    day: str = Field(default="DAY")
    client: str = Field(default="")

    platform: str = Field(default="")
    broker: str = Field(default="")

    copyTrace: str = Field(default="")

    account_id: int = Field(...)

    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """Response for list of orders"""
    orders: List[Order]
    total_orders: int