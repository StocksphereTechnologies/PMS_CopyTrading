"""
Simple TOTP-based login for 5paisa using py5paisa library
No Selenium, no OAuth complexity - just TOTP!
"""
import logging
from typing import Dict, Any
from datetime import datetime, timezone
from py5paisa import FivePaisaClient
import pyotp

from app.models.account import Account
from app.core.encryption import encryption_service

logger = logging.getLogger(__name__)


class FivePaisaSimpleLogin:
    """Simple TOTP-based login for 5paisa - no browser automation needed!"""
    
    async def login(self, account: Account) -> Dict[str, Any]:
        """
        Perform simple TOTP-based login using py5paisa library
        
        Args:
            account: Account model with encrypted credentials
            
        Returns:
            Dictionary with success status, access_token, and token_generated_at
        """
        try:
            logger.info(f"Starting simple TOTP login for 5paisa account {account.account_id}")
            
            # Decrypt credentials
            # MPIN = encrypted_password (used in get_totp_session as 'pin')
            # PASSWORD = encrypted_login_password (used in FivePaisaClient as 'PASSWORD')
            mpin = encryption_service.decrypt(account.encrypted_password)
            login_password = encryption_service.decrypt(account.encrypted_login_password) if account.encrypted_login_password else mpin
            totp_secret = encryption_service.decrypt(account.encrypted_totp_secret)
            
            # Get USER_ID (different from client_code/trading_login_id)
            user_id = account.user_id if account.user_id else account.trading_login_id
            
            # Build credentials for FivePaisaClient
            # Correct 5paisa mapping:
            # APP_NAME -> api_key
            # APP_SOURCE -> app_source  
            # USER_ID -> user_id (NOT trading_login_id)
            # PASSWORD -> encrypted_login_password (NOT encrypted_password)
            # USER_KEY -> user_key
            # ENCRYPTION_KEY -> api_secret
            cred = {
                "APP_NAME": account.api_key or "",
                "APP_SOURCE": account.app_source or "10074",
                "USER_ID": user_id,
                "PASSWORD": login_password,
                "USER_KEY": account.user_key or "",
                "ENCRYPTION_KEY": account.api_secret or ""
            }
            
            logger.info(f"Credentials: APP_SOURCE={cred['APP_SOURCE']}, USER_ID={cred['USER_ID'][:5]}...")
            
            
            client = FivePaisaClient(cred=cred)
            logger.info("FivePaisaClient initialized")
            
            
            totp = pyotp.TOTP(totp_secret).now()
            logger.info(f"Generated TOTP: {totp}")
            
            # Login using TOTP session
            # client_code = trading_login_id (Client Code, NOT USER_ID)
            # pin = mpin (MPIN from encrypted_password, NOT PASSWORD)
            client.get_totp_session(
                client_code=account.trading_login_id,  # Client Code
                totp=totp,
                pin=mpin  # MPIN
            )
            logger.info("TOTP session established successfully")
            
            # Access token is automatically set on the client object after get_totp_session()
            access_token = client.Jwt_token  # or client.access_token
            
            # Ensure access_token is a string, not a bytes object
            if isinstance(access_token, bytes):
                access_token = access_token.decode('utf-8')
            
            if not access_token:
                error_msg = "Failed to get access token after TOTP login"
                logger.error(error_msg)
                return {
                    "success": False,
                    "access_token": None,
                    "token_generated_at": None,
                    "error": error_msg
                }
            
            logger.info(f"Access token obtained: {access_token[:30] if access_token else 'None'}...")
            
            return {
                "success": True,
                "access_token": access_token,
                "client_code": account.trading_login_id,
                "token_generated_at": datetime.now(timezone.utc),
                "error": None
            }
        
        except Exception as e:
            error_msg = f"5paisa simple login failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "access_token": None,
                "token_generated_at": None,
                "error": error_msg
            }
