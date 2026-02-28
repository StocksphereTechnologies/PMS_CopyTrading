import asyncio
import logging
from datetime import datetime, timedelta, time as dt_time
from typing import Dict, Any, Optional
import pytz

from app.models.account import Account
from app.services.login.base_login_service import BaseLoginService
# from app.services.login.zerodha_browser_login import ZerodhaBrowserLogin
from app.core.encryption import encryption_service
from app.core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

from app.services.login.zerodha_auto_auth import ZerodhaAutoAuth

class ZerodhaLoginService(BaseLoginService):
    """Automated login service for Zerodha using Kite Connect (Headless)"""
    
    def __init__(self):
        self.auto_auth = ZerodhaAutoAuth()
    
    async def login(self, account: Account) -> Dict[str, Any]:
        """Perform login using headless request automation"""
        try:
            # Decrypt credentials
            password = encryption_service.decrypt(account.encrypted_password)
            totp_secret = encryption_service.decrypt(account.encrypted_totp_secret)
            
            print(f"DEBUG: [Zerodha] Starting automated login for account {account.account_id} ({account.trading_login_id})...", flush=True)
            return await self.auto_auth.get_access_token(
                account_id=account.account_id,
                client_id=account.trading_login_id,
                password=password,
                totp_secret=totp_secret,
                api_key=account.api_key,
                api_secret=account.api_secret
            )
        except Exception as e:
            logger.error(f"Zerodha login service failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def is_token_valid(self, account: Account) -> bool:
        """
        Check if the current access token is valid
        
        Zerodha tokens expire daily at 7:30 AM IST
        """
        if not account.access_token or not account.token_generated_at:
            logger.debug(f"Account {account.account_id}: No token or timestamp found")
            return False
        
        ist = pytz.timezone('Asia/Kolkata')
        gen_ist = account.token_generated_at.astimezone(ist)
        now_ist = datetime.now(ist)
        
        print(f"DEBUG: [Zerodha] Validating token for {account.account_id}. Generated: {gen_ist.strftime('%Y-%m-%d %H:%M:%S')} | Now: {now_ist.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)

        if self._is_token_expired(account.token_generated_at):
            print(f"DEBUG: [Zerodha] Token for account {account.account_id} EXPIRED (past 7:30 AM IST).", flush=True)
            logger.info(f"Account {account.account_id}: Token expired (past 7:30 AM IST)")
            return False
        
        print(f"DEBUG: [Zerodha] Token for account {account.account_id} is VALID.", flush=True)
        logger.info(f"Account {account.account_id}: Token is valid (generated after 7:30 AM IST)")
        return True
    
    def _is_token_expired(self, token_generated_at: datetime) -> bool:
        """
        Check if token has expired based on 7:30 AM IST cutoff
        
        Per Zerodha documentation: Tokens expire at 7:30 AM IST daily
        """
        ist = pytz.timezone('Asia/Kolkata')
        utc = pytz.UTC
        
        if token_generated_at.tzinfo is None:
            token_generated_at = utc.localize(token_generated_at)
        
        token_time_ist = token_generated_at.astimezone(ist)
        current_time_ist = datetime.now(ist)
        
        today_730am_ist = ist.localize(
            datetime.combine(current_time_ist.date(), dt_time(7, 30, 0))
        )
        
        if current_time_ist >= today_730am_ist:
            cutoff_time = today_730am_ist
        else:
            cutoff_time = today_730am_ist - timedelta(days=1)
        
        is_expired = token_time_ist < cutoff_time
        
        logger.debug(
            f"Token check: generated at {token_time_ist.strftime('%Y-%m-%d %H:%M:%S %Z')}, "
            f"cutoff at {cutoff_time.strftime('%Y-%m-%d %H:%M:%S %Z')}, "
            f"expired: {is_expired}"
        )
        
        return is_expired
    
    async def ensure_valid_token(self, account: Account) -> bool:
        """
        Ensure the account has a valid access token
        """
        if not await self.is_token_valid(account):
            logger.info(f"Account {account.account_id}: Token invalid or expired, refreshing...")
            return await self._refresh_token(account)
        return True
    
    async def _refresh_token(self, account: Account) -> bool:
        """Refresh the access token"""
        result = await self.login(account)
        
        if result.get("success") and result.get("access_token"):
            # Update account with new token
            async with AsyncSessionLocal() as session:
                # Fetch the account 
                db_account = await session.get(Account, account.account_id)
                if db_account:
                    db_account.access_token = result["access_token"]
                    db_account.token_generated_at = result["token_generated_at"]
                    db_account.is_validated = True
                    session.add(db_account)
                    await session.commit()
                    
                    account.access_token = result["access_token"]
                    account.token_generated_at = result["token_generated_at"]
                    account.is_validated = True
                    
                    logger.info(f"Successfully refreshed token for account {account.account_id}")
                    return True
        
        logger.error(f"Failed to refresh token for account {account.account_id}: {result.get('error', 'Unknown error')}")
        return False

    def get_login_url(self, account: Account) -> str:
        """Get official Kite Connect login URL for manual fallback"""
        from kiteconnect import KiteConnect
        kite = KiteConnect(api_key=account.api_key)
        # Construct login URL with state=account_id for identification in callback
        return f"{kite.login_url()}&state={account.account_id}"

    async def handle_callback(self, request_token: str, account_id: str) -> Dict[str, Any]:
        """Handle official Kite callback and generate session"""
        from app.core.database import AsyncSessionLocal
        from kiteconnect import KiteConnect
        
        async with AsyncSessionLocal() as db:
            account = await db.get(Account, int(account_id))
            if not account:
                return {"success": False, "error": "Account not found"}
            
            kite = KiteConnect(api_key=account.api_key)
            try:
                # generate_session is synchronous for now
                session = await asyncio.to_thread(kite.generate_session, request_token, account.api_secret)
                
                account.access_token = session["access_token"]
                account.token_generated_at = session.get("login_time") or datetime.now()
                account.is_validated = True
                
                db.add(account)
                await db.commit()
                
                return {"success": True, "account_id": account.account_id}
            except Exception as e:
                logger.error(f"Kite callback failed: {str(e)}")
                return {"success": False, "error": str(e)}
