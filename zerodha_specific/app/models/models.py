"""
Database models for Zerodha Trade Copier
All fields aligned with the main StockSphere system's Account model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class AccountRole(str, enum.Enum):
    """Account role in copy trading"""
    MASTER = "MASTER"
    CHILD = "CHILD"


class CopyTradeStatus(str, enum.Enum):
    """Status of a copied trade"""
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class ZerodhaAccount(Base):
    """
    Zerodha trading account — same fields as the main system's Account model
    (Zerodha-specific fields only, no 5paisa fields)
    """
    __tablename__ = "zerodha_accounts"

    account_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nickname = Column(String(100), nullable=True)
    role = Column(String(20), nullable=False, index=True)  # MASTER or CHILD

    # ─── Trading Credentials (encrypted) ───
    # Same field names as big system: trading_login_id = Zerodha Client ID
    trading_login_id = Column(String(255), nullable=False)       # Zerodha Client ID (e.g. "AB1234")
    encrypted_password = Column(Text, nullable=True)             # Zerodha login password — encrypted
    encrypted_totp_secret = Column(Text, nullable=False)         # TOTP seed/secret — encrypted

    # ─── Kite Connect API Credentials ───
    # Same field names as big system
    api_key = Column(String(255), nullable=False)                # Kite Connect API Key
    api_secret = Column(Text, nullable=False)                    # Kite Connect API Secret

    # ─── Access Token & Metadata ───
    access_token = Column(Text, nullable=True)                   # Generated access token
    token_generated_at = Column(DateTime(timezone=True), nullable=True)

    # ─── Order Orchestration Settings (from big system) ───
    multiplier = Column(Float, default=1.0, nullable=False)      # Order quantity scaling factor
    split_freeze_limit = Column(Integer, nullable=True)          # Per-account freeze limit override

    # ─── Status Flags ───
    is_enabled = Column(Boolean, default=True, nullable=False, index=True)
    is_validated = Column(Boolean, default=False, nullable=False, index=True)

    # ─── Timestamps ───
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<ZerodhaAccount(id={self.account_id}, client={self.trading_login_id}, role={self.role}, enabled={self.is_enabled})>"


class CopyTradingPair(Base):
    """Links a master account to a child account for trade copying"""
    __tablename__ = "copy_trading_pairs"

    pair_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    master_account_id = Column(Integer, ForeignKey("zerodha_accounts.account_id"), nullable=False, index=True)
    child_account_id = Column(Integer, ForeignKey("zerodha_accounts.account_id"), nullable=False, index=True)

    # ─── Copy Settings ───
    quantity_multiplier = Column(Float, default=1.0, nullable=False)  # child_qty = master_qty × this
    is_active = Column(Boolean, default=False, nullable=False, index=True)
    copy_modifications = Column(Boolean, default=True, nullable=False)   # Copy order modifications
    copy_cancellations = Column(Boolean, default=True, nullable=False)   # Copy order cancellations

    # ─── Timestamps ───
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # ─── Relationships ───
    master_account = relationship("ZerodhaAccount", foreign_keys=[master_account_id])
    child_account = relationship("ZerodhaAccount", foreign_keys=[child_account_id])
    logs = relationship("CopyTradeLog", back_populates="pair", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CopyTradingPair(id={self.pair_id}, master={self.master_account_id}→child={self.child_account_id}, active={self.is_active})>"


class CopyTradeLog(Base):
    """Audit trail of every copied trade"""
    __tablename__ = "copy_trade_logs"

    log_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pair_id = Column(Integer, ForeignKey("copy_trading_pairs.pair_id"), nullable=False, index=True)

    # ─── Master Order Info ───
    master_order_id = Column(String(255), nullable=False, index=True)  # Zerodha order_id from master
    tradingsymbol = Column(String(255), nullable=False)
    exchange = Column(String(50), nullable=False)
    transaction_type = Column(String(20), nullable=False)               # BUY or SELL
    quantity = Column(Integer, nullable=False)                           # Quantity placed on child
    order_type = Column(String(50), nullable=True)                      # MARKET, LIMIT, SL, SL-M
    product = Column(String(50), nullable=True)                         # MIS, CNC, NRML
    price = Column(Float, nullable=True)                                # Master's fill price
    trigger_price = Column(Float, nullable=True)

    # ─── Child Order Info ───
    child_order_id = Column(String(255), nullable=True)                 # Zerodha order_id on child (null if failed)
    status = Column(String(20), nullable=False, default="PENDING")      # PENDING, SUCCESS, FAILED, SKIPPED
    error_reason = Column(Text, nullable=True)                          # Error message if failed

    # ─── Timing ───
    master_order_time = Column(DateTime(timezone=True), nullable=True)  # When master placed the order
    child_order_time = Column(DateTime(timezone=True), nullable=True)   # When child order was placed
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # ─── Relationships ───
    pair = relationship("CopyTradingPair", back_populates="logs")

    def __repr__(self):
        return f"<CopyTradeLog(id={self.log_id}, master_order={self.master_order_id}, status={self.status})>"
