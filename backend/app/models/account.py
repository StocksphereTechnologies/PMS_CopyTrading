"""
Account model for storing trading account information
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class BrokerName(str, enum.Enum):
    """Broker name enum"""
    ZERODHA = "ZERODHA"
    FIVEPAISA = "FIVEPAISA"


class Account(Base):
    """Trading account model with automated login support"""
    __tablename__ = "accounts"
    
    account_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    owner_id = Column(Integer, nullable=True, index=True)  # Foreign key to users.user_id (system user, not broker)
    broker_name = Column(String(50), nullable=False, index=True)
    nickname = Column(String(100), nullable=True)  
    
    # Trading credentials (encrypted)
    # Zerodha: trading_login_id = Client ID, encrypted_password = Password
    # 5paisa: trading_login_id = Client Code, encrypted_password = MPIN
    trading_login_id = Column(String(255), nullable=False)  # Zerodha: Client ID | 5paisa: Client Code
    encrypted_password = Column(Text, nullable=True)  # Zerodha: Password | 5paisa: MPIN - encrypted
    encrypted_totp_secret = Column(Text, nullable=False)  # TOTP seed - encrypted
    
    # 5paisa-specific credentials {not used by Zerodha}
    user_id = Column(String(255), nullable=True)  # 5paisa USER_ID (different from client_code)
    encrypted_login_password = Column(Text, nullable=True)  # 5paisa PASSWORD (different from MPIN) - encrypted
    
    # BROKER_SPECIFIC API credentials
    # For Zerodha: api_key, api_secret (Kite Connect)
    # For 5paisa: user_key, app_source
    api_key = Column(String(255), nullable=True)  # Zerodha Kite API key or 5paisa app_name
    api_secret = Column(Text, nullable=True)  # Zerodha Kite API secret or 5paisa encryption_key
    user_key = Column(String(255), nullable=True)  # 5paisa user_key
    app_source = Column(String(255), nullable=True)  # 5paisa app_source
    
    # Access token and require metadata
    access_token = Column(Text, nullable=True)  
    token_generated_at = Column(DateTime(timezone=True), nullable=True)  
    
    # Advanced Order Orchestration Settings
    multiplier = Column(Float, default=1.0, nullable=False) # Order quantity scaling
    split_freeze_limit = Column(Integer, nullable=True) # Per-account freeze limit override
    
    
    is_enabled = Column(Boolean, default=True, nullable=False, index=True)
    is_validated = Column(Boolean, default=False, nullable=False, index=True)  
    
    # Subscription/Payment {as per the frontend }
    is_paid = Column(Boolean, default=True, nullable=False, index=True)  # Payment status [default TRUE for now]
    subscription_type = Column(String(20), nullable=True)  # 'monthly', 'yearly', 'lifetime'
    subscription_start_date = Column(DateTime(timezone=True), nullable=True)
    subscription_end_date = Column(DateTime(timezone=True), nullable=True)
    
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Account(account_id={self.account_id}, broker_name={self.broker_name}, nickname={self.nickname}, is_enabled={self.is_enabled})>"

