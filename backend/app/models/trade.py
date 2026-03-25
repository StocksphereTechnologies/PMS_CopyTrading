"""
Trade models for storing trade execution information
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class OrderStatus(str, enum.Enum):
    """Order status enum"""
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"
    CANCELLED = "CANCELLED"


class OrderSide(str, enum.Enum):
    """Order side enum"""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, enum.Enum):
    """Order type enum"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    SL = "SL"  
    SL_M = "SL_M"  


class Trade(Base):
    """Main trade record - one per UI action"""
    __tablename__ = "trades"
    
    trade_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    owner_id = Column(Integer, nullable=True, index=True)  
    symbol = Column(String(100), nullable=False, index=True)
    exchange = Column(String(50), nullable=False)
    side = Column(Enum(OrderSide), nullable=False)
    quantity = Column(Integer, nullable=False)
    order_type = Column(Enum(OrderType), nullable=False)
    price = Column(Float, nullable=True)
    trigger_price = Column(Float, nullable=True)
    product = Column(String(50), nullable=True)  # CNC, MIS, NRML, etc.
    
    # Advanced / BO / CO fields
    target = Column(Float, nullable=True)
    stoploss = Column(Float, nullable=True)
    trailing_stoploss = Column(Float, nullable=True)
    
    # Variety and Validity
    variety = Column(String(50), nullable=True, default="regular") # regular, bo, co, amo
    validity = Column(String(50), nullable=True, default="DAY") # DAY, IOC
    tag = Column(String(100), nullable=True)
    
    # Orchestration features
    is_amo = Column(Boolean, default=False)
    split_type = Column(String(20), default="NO") # NO, AUTO, QTY
    split_qty = Column(Integer, nullable=True)
    multiplier_active = Column(Boolean, default=False)
    group_acc_active = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    executions = relationship("TradeExecution", back_populates="trade", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Trade(trade_id={self.trade_id}, symbol={self.symbol}, side={self.side}, product={self.product})>"


class TradeExecution(Base):
    """Individual execution per account"""
    __tablename__ = "trade_executions"
    
    execution_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    trade_id = Column(Integer, ForeignKey("trades.trade_id"), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"), nullable=False, index=True)
    broker = Column(String(50), nullable=False)
    order_id = Column(String(255), nullable=True)  
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    executed_price = Column(Float, nullable=True)
    executed_quantity = Column(Integer, nullable=True)
    error_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    trade = relationship("Trade", back_populates="executions")
    
    def __repr__(self):
        return f"<TradeExecution(execution_id={self.execution_id}, trade_id={self.trade_id}, broker={self.broker}, status={self.status})>"