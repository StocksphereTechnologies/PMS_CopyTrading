from pydantic import BaseModel
from typing import List
from datetime import datetime


class AccountSummary(BaseModel):
    pseudoAcc: str
    tradingAcc: str

    m2m: float
    pnl: float
    atPnl: float

    totalPos: int
    openPos: int
    closedPos: int

    marginTotal: float
    marginUtilized: float
    marginAvailable: float

    orderTotal: int
    orderOpen: int
    orderTPend: int


class SymbolSummary(BaseModel):
    exchange: str
    symbol: str

    buyQty: int
    sellQty: int
    netQty: int

    m2m: float
    pnl: float
    atPnl: float

    buyVal: float
    sellVal: float
    netVal: float

    buyAvg: float
    sellAvg: float


class PositionsAnalytics(BaseModel):
    m2m: float
    pnl: float
    atPnl: float

    total: int
    open: int
    closed: int


class OrdersAnalytics(BaseModel):
    total: int
    open: int
    complete: int
    trigPend: int
    cancelled: int
    rejected: int


class MarginAnalytics(BaseModel):
    total: float
    utilized: float
    available: float


class SummaryResponse(BaseModel):

    account_summary: List[AccountSummary]
    symbol_summary: List[SymbolSummary]

    positions_analytics: PositionsAnalytics
    orders_analytics: OrdersAnalytics
    margin_analytics: MarginAnalytics

    last_updated: datetime