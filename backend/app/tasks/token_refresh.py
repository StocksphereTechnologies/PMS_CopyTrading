"""Background task to refresh Zerodha access tokens"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.account import Account
# from app.services.login.zerodha_login_service import ZerodhaLoginService
from app.services.login.zerodha_login_service import ZerodhaLoginService
from app.core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

class TokenRefreshTask:
    """Task to refresh access tokens for Zerodha accounts"""
    
    def __init__(self, check_interval_hours: int = 1):
        self.check_interval = check_interval_hours * 3600
        self.is_running = False
        self.login_service = ZerodhaLoginService()
    
    async def refresh_token(self, account: Account, db: AsyncSession) -> bool:
        """Refresh access token for a single account"""
        try:
            # Skip if not enabled or not Zerodha
            if not account.is_enabled or account.broker_name != "ZERODHA":
                return False
                
            logger.info(f"Refreshing token for account {account.account_id}")
            
            # Use login service to get new token
            result = await self.login_service.login(account)
            
            if result["success"] and result["access_token"]:
                
                account.access_token = result["access_token"]
                account.token_generated_at = datetime.utcnow()
                
                
                db.add(account)
                await db.commit()
                
                logger.info(f"Successfully refreshed token for account {account.account_id}")
                return True
            else:
                logger.error(f"Failed to refresh token for account {account.account_id}: {result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"Error refreshing token for account {account.account_id}: {str(e)}", exc_info=True)
            return False
    
    async def run_refresh(self):
        """Run token refresh for all Zerodha accounts"""
        if self.is_running:
            logger.warning("Token refresh is already running")
            return
            
        self.is_running = True
        logger.info("Starting token refresh task")
        
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Account)
                    .where(Account.broker_name == "ZERODHA")
                    .where(Account.is_enabled == True)
                )
                accounts = result.scalars().all()
                
                for account in accounts:
                    await self.refresh_token(account, db)
                    
        except Exception as e:
            logger.error(f"Error in token refresh task: {str(e)}", exc_info=True)
        finally:
            self.is_running = False
    
    async def start(self):
        """Start the token refresh scheduler"""
        logger.info("Starting token refresh scheduler")
        
        while True:
            try:
                await self.run_refresh()
            except Exception as e:
                logger.error(f"Error in token refresh scheduler: {str(e)}", exc_info=True)
            
            
            await asyncio.sleep(self.check_interval)

# Global instance
token_refresh_task = TokenRefreshTask()