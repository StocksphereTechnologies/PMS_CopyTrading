"""
Margin service for fetching margin data from multiple brokers
"""
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from app.models.account import Account, BrokerName
from app.services.account_service import AccountService
from app.adapters.fivepaisa_margin_adapter import FivePaisaMarginAdapter

logger = logging.getLogger(__name__)


class MarginService:
    """Service for fetching margin data from multiple broker accounts"""
    
    @staticmethod
    async def get_margins_for_user(db: AsyncSession, user_id: int) -> List[Dict[str, Any]]:
        """
        Fetch margin data for all enabled accounts belonging to a user
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of margin data dictionaries
        """
        try:
            # Get all enabled accounts for the user
            accounts = await AccountService.get_user_accounts(db, user_id, enabled_only=True)
            
            if not accounts:
                logger.info(f"No enabled accounts found for user {user_id}")
                return []
            
            logger.info(f"Fetching margins for {len(accounts)} accounts for user {user_id} in parallel")
            
            import asyncio
            # Limit concurrency to 10 at a time to be safe with broker rate limits
            semaphore = asyncio.Semaphore(10)
            
            async def fetch_with_semaphore(acc):
                async with semaphore:
                    return await MarginService.get_margin_for_account(db, acc)
            
            # Create tasks for all accounts
            tasks = [fetch_with_semaphore(account) for account in accounts]
            
            # Execute all tasks in parallel
            results = await asyncio.gather(*tasks)
            
            # Filter out None results
            margins = [r for r in results if r is not None]
            
            logger.info(f"Successfully fetched margins for {len(margins)}/{len(accounts)} accounts")
            return margins
            
        except Exception as e:
            logger.error(f"Error fetching margins for user {user_id}: {e}", exc_info=True)
            return []
    
    @staticmethod
    async def get_margin_for_account(db: AsyncSession, account: Account) -> Dict[str, Any]:
        """
        Fetch margin data for a single account.
        Attempts re-login if token is missing or expired.
        """
        try:
            # --- Token validation & auto re-login ---
            needs_login = False
            
            if not account.access_token:
                logger.info(f"Account {account.account_id}: no access token, will attempt login")
                needs_login = True
            elif account.broker_name == BrokerName.FIVEPAISA.value and account.token_generated_at:
                # 5paisa tokens expire at midnight IST daily
                ist = timezone(timedelta(hours=5, minutes=30))
                now_ist = datetime.now(ist)
                generated_ist = account.token_generated_at.astimezone(ist)
                if now_ist.date() > generated_ist.date():
                    logger.info(f"Account {account.account_id}: token from previous day, will refresh")
                    needs_login = True
            
            if needs_login:
                login_result = await MarginService._attempt_relogin(db, account)
                if not login_result:
                    # Login failed — return a structured error instead of None
                    return {
                        "account_id": account.account_id,
                        "broker_name": account.broker_name,
                        "nickname": account.nickname,
                        "trading_login_id": account.trading_login_id,
                        "status": "session_invalid",
                        "error": "Login failed — session could not be established (market may be closed on weekends)",
                        "equity": None,
                        "commodity": None,
                        "last_updated": datetime.now(timezone.utc)
                    }
            
            # Fetch margin based on broker
            if account.broker_name == BrokerName.ZERODHA.value:
                return await MarginService._fetch_zerodha_margin(account)
            elif account.broker_name == BrokerName.FIVEPAISA.value:
                return await MarginService._fetch_fivepaisa_margin(account)
            else:
                logger.error(f"Unsupported broker: {account.broker_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching margin for account {account.account_id}: {e}", exc_info=True)
            return None
    
    @staticmethod
    async def _attempt_relogin(db: AsyncSession, account: Account) -> bool:
        """
        Attempt to re-login an account and persist the new token.
        Returns True on success, False on failure.
        """
        try:
            if account.broker_name == BrokerName.FIVEPAISA.value:
                from app.services.login.fivepaisa_login_service import FivePaisaLoginService
                login_service = FivePaisaLoginService()
            elif account.broker_name == BrokerName.ZERODHA.value:
                from app.services.login.zerodha_login_service import ZerodhaLoginService
                login_service = ZerodhaLoginService()
            else:
                return False
            
            logger.info(f"Attempting re-login for account {account.account_id} ({account.broker_name})")
            result = await login_service.login(account)
            
            if result.get("success") and result.get("access_token"):
                # Persist the new token
                account.access_token = AccountService._clean_token(result["access_token"])
                account.token_generated_at = result.get("token_generated_at")
                account.is_validated = True
                db.add(account)
                await db.commit()
                logger.info(f"Re-login successful for account {account.account_id}")
                return True
            else:
                error = result.get("error", "Unknown error")
                logger.warning(f"Re-login failed for account {account.account_id}: {error}")
                return False
        except Exception as e:
            logger.error(f"Re-login exception for account {account.account_id}: {e}", exc_info=True)
            return False
    
    @staticmethod
    async def _fetch_zerodha_margin(account: Account) -> Dict[str, Any]:
        """
        Fetch margin data from Zerodha
        
        Args:
            account: Account model
            
        Returns:
            Margin data dictionary
        """
        from app.adapters.zerodha_adapter import ZerodhaAdapter
        adapter = ZerodhaAdapter(account=account)
        return await adapter.get_margins()
    
    @staticmethod
    async def _fetch_fivepaisa_margin(account: Account) -> Dict[str, Any]:
        """
        Fetch margin data from 5paisa
        
        Args:
            account: Account model
            
        Returns:
            Margin data dictionary
        """
        adapter = FivePaisaMarginAdapter()
        return await adapter.get_margins(account)
