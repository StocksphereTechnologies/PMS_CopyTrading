"""
Simple TOTP-based login service for 5paisa
"""
import logging
from typing import Dict, Any
from datetime import datetime, timedelta, timezone
from app.models.account import Account
from app.services.login.base_login_service import BaseLoginService
from app.services.login.fivepaisa_simple_login import FivePaisaSimpleLogin

logger = logging.getLogger(__name__)


class FivePaisaLoginService(BaseLoginService):
    """Simple TOTP-based login service for 5paisa"""
    
    def __init__(self):
        self.simple_login = FivePaisaSimpleLogin()
    
    async def login(self, account: Account) -> Dict[str, Any]:
        """
        Perform simple TOTP-based login for 5paisa
        
        Flow:
        1. Initialize FivePaisaClient with credentials
        2. Generate TOTP code
        3. Call get_totp_session() - handles everything automatically
        4. Get access token
        5. Return AccessToken
        
        Args:
            account: Account model with 5paisa credentials
            
        Returns:
            Dictionary with access_token and metadata
        """
        try:
            logger.info(f"Starting simple TOTP login for 5paisa account {account.account_id}")
            
            result = await self.simple_login.login(account)
            
            if not result['success']:
                logger.error(f"TOTP login failed: {result.get('error')}")
                return result
            
            logger.info(f"TOTP login successful for account {account.account_id}")
            
            return {
                "success": True,
                "access_token": result['access_token'],
                "client_code": result.get('client_code'),
                "token_generated_at": result['token_generated_at'],
                "error": None
            }
        
        except Exception as e:
            error_msg = f"5paisa OAuth login failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "access_token": None,
                "token_generated_at": None,
                "error": error_msg
            }
    
    async def is_token_valid(self, account: Account) -> bool:
        """
        Check if current access token is valid
        
        Args:
            account: Account model
            
        Returns:
            True if token is valid, False otherwise
        """
        if not account.access_token or not account.token_generated_at:
            return False
        
        token_age = datetime.now(timezone.utc) - account.token_generated_at
        
        return token_age <= timedelta(hours=16)
    
    async def ensure_valid_token(self, account: Account) -> bool:
        """
        Ensure account has a valid access token
        
        5paisa access tokens expire at 11:59 PM daily
        
        Args:
            account: Account model
            
        Returns:
            True if token is valid or successfully refreshed
        """
        try:
            if not account.access_token or not account.token_generated_at:
                logger.info(f"No token found for account {account.account_id}, logging in...")
                result = await self.login(account)
                if result['success']:
                    account.access_token = result['access_token']
                    account.token_generated_at = result['token_generated_at']
                    logger.info(f"Token saved for account {account.account_id}")
                return result['success']
            
            # 5paisa sessions expire daily at midnight IST. 
            # We must refresh if the token was generated on a different day.
            ist = timezone(timedelta(hours=5, minutes=30))
            now_ist = datetime.now(ist)
            generated_at_ist = account.token_generated_at.astimezone(ist)
            
            is_expired = False
            print(f"DEBUG: Validating 5paisa token for {account.account_id}. Generated: {generated_at_ist.strftime('%Y-%m-%d %H:%M:%S')} | Now: {now_ist.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
            
            if now_ist.date() > generated_at_ist.date():
                print(f"DEBUG: Token for account {account.account_id} is from a previous day (IST). FORCE REFRESH.", flush=True)
                is_expired = True
            elif (now_ist - generated_at_ist) > timedelta(hours=16):
                print(f"DEBUG: Token for account {account.account_id} is too old (>16h). FORCE REFRESH.", flush=True)
                is_expired = True
            
            if is_expired:
                result = await self.login(account)
                if result['success']:
                    account.access_token = result['access_token']
                    account.token_generated_at = result['token_generated_at']
                    logger.info(f"Token refreshed for account {account.account_id}")
                return result['success']
            
            logger.info(f"Token is valid for account {account.account_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error ensuring valid token: {str(e)}", exc_info=True)
            return False
