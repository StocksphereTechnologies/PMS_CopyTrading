"""
Position service for fetching and consolidating positions across multiple brokers
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account, BrokerName
from app.services.account_service import AccountService
from app.adapters.fivepaisa_position_adapter import FivePaisaPositionAdapter
from app.schemas.position import Position

logger = logging.getLogger(__name__)

class PositionService:
    """Service for fetching and consolidating position data"""
    
    @staticmethod
    async def get_positions_for_user(
        db: AsyncSession, 
        user_id: int, 
        open_only: bool = True
    ) -> List[Position]:
        """
        Fetch positions for all enabled accounts of a user in parallel
        
        Args:
            db: Database session
            user_id: User identifier
            open_only: If True, returns only positions where netqty != 0
            
        Returns:
            Flat list of unified Position objects
        """
        try:
            # Get all enabled accounts
            accounts = await AccountService.get_user_accounts(db, user_id, enabled_only=True)
            
            if not accounts:
                logger.info(f"No enabled accounts found for user {user_id}")
                return []
            
            logger.info(f"Fetching positions for {len(accounts)} accounts for user {user_id} in parallel")
            
            # Limit concurrency to 10
            semaphore = asyncio.Semaphore(10)
            
            async def fetch_with_semaphore(acc: Account) -> List[Position]:
                async with semaphore:
                    return await PositionService.get_positions_for_account(acc)
            
            # Create parallel tasks
            tasks = [fetch_with_semaphore(acc) for acc in accounts]
            
            # Execute all
            results = await asyncio.gather(*tasks)
            
            # Flatten results (results is a list of lists)
            all_positions = []
            for position_list in results:
                all_positions.extend(position_list)
                
            # Filter open only if requested
            if open_only:
                original_count = len(all_positions)
                all_positions = [p for p in all_positions if p.netqty != 0]
                logger.debug(f"Filtered {original_count - len(all_positions)} closed positions")
            
            logger.info(f"Successfully Consolidated {len(all_positions)} positions across {len(accounts)} accounts")
            return all_positions
            
        except Exception as e:
            logger.error(f"Error in PositionService.get_positions_for_user: {e}", exc_info=True)
            return []

    @staticmethod
    async def get_positions_for_account(account: Account) -> List[Position]:
        """Fetch positions for a single account based on broker"""
        try:
            if account.broker_name == BrokerName.ZERODHA.value:
                from app.adapters.zerodha_adapter import ZerodhaAdapter
                adapter = ZerodhaAdapter(account=account)
                return await adapter.get_positions()
            elif account.broker_name == BrokerName.FIVEPAISA.value:
                adapter = FivePaisaPositionAdapter()
                return await adapter.get_positions(account)
            else:
                logger.warning(f"Unsupported broker {account.broker_name} for account {account.account_id}")
                return []
        except Exception as e:
            logger.error(f"Error fetching positions for account {account.account_id}: {e}")
            return []
