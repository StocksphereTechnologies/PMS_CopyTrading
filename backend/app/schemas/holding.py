from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class Holding(BaseModel):
    pseAcc: str
    trdAcc: str

    exchange: str
    symbol: str

    totqty: int
    ltp: float
    currval: float

    quantity: int
    t1qty: int

    pnl: float

    product: str

    nsesymbol: str
    bsesymbol: str
    isin: str

    insttoken: str

    collateralQty: int
    collateralType: str
    haircut: float

    avgPrice: float

    day: str
    platform: str
    broker: str

    account_id: int | None = None

    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class HoldingListResponse(BaseModel):
    holdings: List[Holding]
    total: int