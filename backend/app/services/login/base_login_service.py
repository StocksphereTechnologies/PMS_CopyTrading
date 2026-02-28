"""
Base login service interface for automated broker authentication
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.models.account import Account


class BaseLoginService(ABC):
    """Abstract base class for broker login services"""
    
    @abstractmethod
    async def login(self, account: Account) -> Dict[str, Any]:
        """
        Perform automated login and obtain access token
        
        Args:
            account: Account model with credentials
            
        Returns:
            Dictionary with:
                - access_token: Obtained access token
                - token_generated_at: Timestamp when token was generated
                - success: Boolean indicating success
                - error: Error message if failed
        """
        pass
    
    @abstractmethod
    async def is_token_valid(self, account: Account) -> bool:
        """
        Check if current access token is valid
        
        Args:
            account: Account model
            
        Returns:
            True if token is valid, False otherwise
        """
        pass
    
    @abstractmethod
    async def ensure_valid_token(self, account: Account) -> bool:
        """
        Ensure account has a valid token, auto-login if needed
        
        Args:
            account: Account model
            
        Returns:
            True if token is now valid, False if login failed
        """
        pass
    
    def is_token_expired(self, account: Account, expiry_hours: int = 24) -> bool:
        """
        Check if token is expired based on token_generated_at
        
        Args:
            account: Account model
            expiry_hours: Hours after which token is considered expired
            
        Returns:
            True if expired, False otherwise
        """
        if not account.token_generated_at:
            return True
        
        expiry_time = account.token_generated_at + timedelta(hours=expiry_hours)
        return datetime.now(account.token_generated_at.tzinfo) >= expiry_time
