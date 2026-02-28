"""
Account schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.account import BrokerName


class ZerodhaAccountCreate(BaseModel):
    """Schema for creating a Zerodha account"""
    broker_name: BrokerName = BrokerName.ZERODHA
    trading_login_id: str = Field(..., min_length=1,    description="Zerodha Client ID")
    trading_password: str = Field(..., min_length=1, description="Zerodha login password")
    totp_secret_key: str = Field(..., min_length=1, description="Zerodha TOTP seed/secret")
    api_key: str = Field(..., min_length=1, description="Kite Connect API Key")
    api_secret: str = Field(..., min_length=1, description="Kite Connect API Secret")
    nickname: Optional[str] = Field(None, description="Optional nickname for the account")
    is_enabled: bool = True


class FivePaisaAccountCreate(BaseModel):
    """Schema for creating a 5paisa account"""
    broker_name: BrokerName = BrokerName.FIVEPAISA
    trading_login_id: str = Field(..., min_length=1, description="5paisa Client ID")
    mpin: str = Field(..., min_length=6, max_length=6, description="6-digit MPIN")
    totp_secret_key: str = Field(..., min_length=1, description="5paisa TOTP seed/secret")
    user_key: str = Field(..., min_length=1, description="5paisa API User Key")
    app_source: str = Field(..., min_length=1, description="5paisa API App Source")
    api_key: Optional[str] = Field(None, description="5paisa App Name (optional)")
    api_secret: Optional[str] = Field(None, description="5paisa Encryption Key (optional)")
    nickname: Optional[str] = Field(None, description="Optional nickname for the account")
    is_enabled: bool = True

# need to change frontend a bit as per backend (please) 
class AccountCreate(BaseModel):
    """Unified schema for creating an account (supports both brokers)"""
    broker_name: BrokerName
    
    # Common fields
    trading_login_id: str = Field(..., min_length=1)
    totp_secret_key: str = Field(..., min_length=1)
    nickname: Optional[str] = None
    is_enabled: bool = True
    
    # Zerodha specific
    trading_password: Optional[str] = None  # For Zerodha
    api_key: Optional[str] = None  # Kite API key for Zerodha, App Name for 5paisa
    api_secret: Optional[str] = None  # Kite API secret for Zerodha, Encryption key for 5paisa
    
    # 5paisa specific
    mpin: Optional[str] = None  # For 5paisa (used in get_totp_session as 'pin')
    user_id: Optional[str] = None  # For 5paisa USER_ID (different from trading_login_id/client_code)
    login_password: Optional[str] = None  # For 5paisa PASSWORD (different from MPIN, used in FivePaisaClient)
    user_key: Optional[str] = None  # For 5paisa
    app_source: Optional[str] = None  # For 5paisa


class AccountUpdate(BaseModel):
    """Schema for updating an account"""
    trading_login_id: Optional[str] = None
    trading_password: Optional[str] = None
    mpin: Optional[str] = None
    totp_secret_key: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    user_key: Optional[str] = None
    app_source: Optional[str] = None
    nickname: Optional[str] = None
    is_enabled: Optional[bool] = None
    multiplier: Optional[float] = None
    split_freeze_limit: Optional[int] = None


class AccountResponse(BaseModel):
    """Schema for account response (no sensitive data)"""
    account_id: int
    owner_id: Optional[int] = None  # User who owns this account {user_id from user table not broker user id}
    broker_name: str
    nickname: Optional[str] = None
    trading_login_id: str  
    is_enabled: bool
    is_validated: Optional[bool] = False  
    is_paid: Optional[bool] = True  
    multiplier: float = 1.0
    split_freeze_limit: Optional[int] = None
    token_generated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AccountListResponse(BaseModel):
    """Schema for list of accounts"""
    accounts: list[AccountResponse]
    total: int
