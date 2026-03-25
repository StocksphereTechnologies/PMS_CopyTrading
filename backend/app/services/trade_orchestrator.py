"""
Trade orchestrator for executing trades across multiple accounts
"""
import asyncio
import uuid
import time
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Tuple
from app.models.account import Account, BrokerName
from app.models.trade import Trade, TradeExecution, OrderStatus
from app.services.account_service import AccountService
from app.adapters.zerodha_adapter import ZerodhaAdapter
from app.adapters.fivepaisa_adapter import FivePaisaAdapter
from app.schemas.trade import TradeRequest
import logging
from datetime import datetime
from app.models.group import GroupAccount

logger = logging.getLogger(__name__)


class TradeOrchestrator:
    """Orchestrator for executing trades across multiple accounts with minimal latency"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._adapters_cache: Dict[int, Any] = {}
    
    async def _get_adapter(self, account: Account):
        """
        Get or create broker adapter for account (with auto-login support)
        
        Args:
            account: Account model
            
        Returns:
            Broker adapter instance
        """
        if account.account_id in self._adapters_cache:
            return self._adapters_cache[account.account_id]
        
        if account.broker_name == BrokerName.ZERODHA.value:
            adapter = ZerodhaAdapter(account=account, db=self.db)
        elif account.broker_name == BrokerName.FIVEPAISA.value:
            adapter = FivePaisaAdapter(account=account, db=self.db)
        else:
            raise ValueError(f"Unsupported broker: {account.broker_name}")
        
        self._adapters_cache[account.account_id] = adapter
        return adapter
    
    async def execute_trade(self, trade_request: TradeRequest, current_user) -> Trade:
        """
        Execute trade across all enabled accounts owned by the current user
        
        Args:
            trade_request: Trade request details
            current_user: Current authenticated user
            
        Returns:
            Trade model with execution results
        """
        start_time = time.time()
        
        # Create main trade record
        trade = Trade(
            owner_id=current_user.user_id,
            symbol=trade_request.symbol,
            exchange=trade_request.exchange,
            side=trade_request.side,
            quantity=trade_request.quantity,
            order_type=trade_request.order_type,
            price=trade_request.price,
            trigger_price=trade_request.trigger_price,
            product=trade_request.product,
            target=trade_request.Target,
            stoploss=trade_request.Stoploss,
            trailing_stoploss=trade_request.trailing_stoploss,
            variety=trade_request.variety,
            validity=trade_request.validity,
            tag=trade_request.tag,
            is_amo=trade_request.amo,
            split_type=trade_request.split,
            split_qty=trade_request.splitQty,
            multiplier_active=trade_request.multiplier,
            group_acc_active=trade_request.groupAcc
        )
        
        self.db.add(trade)
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(trade)
        
        logger.info(f"Created trade {trade.trade_id} for {trade_request.symbol}")

        # =====================================================================
        # ACCOUNT SELECTION LOGIC — 3 paths:
        #   1. accounts_with_qty → diffQty mode (per-account quantities)
        #   2. account_ids       → normal selection (with group resolution)
        #   3. fallback          → ALL enabled accounts
        # =====================================================================

        qty_map = {}

        if trade_request.accounts_with_qty:
            # ── PATH 1: diffQty ON — accounts_with_qty provided ──
            account_ids = []

            for item in trade_request.accounts_with_qty:

                # CASE 1: GROUP
                if item.get("group_id"):
                    result = await self.db.execute(
                        select(GroupAccount.account_id).where(
                            GroupAccount.group_id == item["group_id"]
                        )
                    )
                    group_accounts = result.scalars().all()
            
                    for acc_id in group_accounts:
                        account_ids.append(acc_id)
                        qty_map[acc_id] = item["quantity"]
            
                # CASE 2: ACCOUNT
                elif item.get("account_id"):
                    acc_id = item["account_id"]
                    account_ids.append(acc_id)
                    qty_map[acc_id] = item["quantity"]
            
            # REMOVE DUPLICATES
            account_ids = list(set(account_ids))

            # FETCH ACTUAL ACCOUNT OBJECTS
            result = await self.db.execute(
                select(Account).where(
                    and_(
                        Account.owner_id == current_user.user_id,
                        Account.account_id.in_(account_ids),
                        Account.is_enabled == True
                    )
                )
            )
            accounts = result.scalars().all()

        elif trade_request.account_ids:
            # ── PATH 2: Normal mode — specific account_ids selected ──
            account_ids = list(trade_request.account_ids)

            # When groupAcc is ON, account_ids actually contains GROUP IDs
            # We need to resolve them to actual account IDs via GroupAccount
            if trade_request.groupAcc:
                group_ids = account_ids
                account_ids = []
                for gid in group_ids:
                    result = await self.db.execute(
                        select(GroupAccount.account_id).where(
                            GroupAccount.group_id == gid
                        )
                    )
                    group_accounts = result.scalars().all()
                    account_ids.extend(group_accounts)
                # Remove duplicates (account may be in multiple groups)
                account_ids = list(set(account_ids))
                logger.info(f"Resolved {len(group_ids)} groups to {len(account_ids)} account IDs")

            result = await self.db.execute(
                select(Account).where(
                    and_(
                        Account.owner_id == current_user.user_id,
                        Account.account_id.in_(account_ids),
                        Account.is_enabled == True
                    )
                )
            )
            accounts = result.scalars().all()

        else:
            # ── PATH 3: Fallback — no selection, use ALL enabled accounts ──
            accounts = await AccountService.get_user_accounts(
                self.db,
                current_user.user_id,
                enabled_only=True
            )

        # COMMON VALIDATION
        if not accounts:
            logger.warning(
                f"Trade {trade.trade_id}: No valid/enabled accounts found for execution"
            )
            return trade
        
        # 🚀 PRELOAD 5PAISA INSTRUMENTS (ADD HERE)
        preload_tasks = []
        
        for account in accounts:
            if account.broker_name == BrokerName.FIVEPAISA.value:
                adapter = await self._get_adapter(account)
                preload_tasks.append(adapter.get_instruments(trade_request.exchange))
        
        if preload_tasks:
            logger.info("🚀 Preloading 5paisa instruments...")
            await asyncio.gather(*preload_tasks, return_exceptions=True)
        
        # 1 Pre-initialize all adapters in parallel
        logger.debug(f"Pre-initializing {len(accounts)} adapters...")
        adapter_tasks = [self._get_adapter(account) for account in accounts]
        adapters = await asyncio.gather(*adapter_tasks, return_exceptions=True)
        
        # 2 Execute all orders simultaneously
        execution_tasks = []
        execution_metadata = [] # Store (account, adapter, order_params, original_qty)
        
        for i, account in enumerate(accounts):
            if isinstance(adapters[i], Exception): continue
            
            adapter = adapters[i]
            
            # 1. Multiplier Logic
            if qty_map:
                if account.account_id not in qty_map:
                    logger.warning(f"Skipping account {account.account_id} (no qty provided)")
                    continue
                qty = qty_map[account.account_id]
            else:
                qty = trade_request.quantity
            if trade_request.multiplier and account.multiplier > 0:
                qty = int(qty * account.multiplier)
                logger.debug(f"Applied multiplier {account.multiplier} for account {account.account_id}: {trade_request.quantity} -> {qty}")
            
            # 2. Split Order Logic
            legs = []
            if trade_request.split == "QTY" and trade_request.splitQty and trade_request.splitQty > 0:
                # Split based on user defined quantity
                full_qty = qty
                while full_qty > 0:
                    leg_qty = min(full_qty, trade_request.splitQty)
                    legs.append(leg_qty)
                    full_qty -= leg_qty
            elif trade_request.split == "AUTO":
                # Split based on freeze limits (e.g. 1800 for NIFTY)
                freeze_limit = account.split_freeze_limit or 900 # Default if not set
                full_qty = qty
                while full_qty > 0:
                    leg_qty = min(full_qty, freeze_limit)
                    legs.append(leg_qty)
                    full_qty -= leg_qty
            else:
                legs = [qty]

            # 3. Create execution tasks for each leg
            for leg_qty in legs:
                # Prepare leg-specific order request
                leg_params = await self._prepare_order_request(adapter, account, trade_request, leg_qty)
                
                execution_tasks.append(
                    self._execute_single_order(trade, account, adapter, leg_params)
                )
                execution_metadata.append({
                    "account": account,
                    "qty": leg_qty
                })
        
        # Execute all orders in parallel and measure timing 
        logger.info(f" Executing {len(execution_tasks)} orders simultaneously...")
        execution_start = time.time()
        execution_results = await asyncio.gather(*execution_tasks, return_exceptions=True)
        execution_end = time.time()
        
        total_execution_time_ms = (execution_end - execution_start) * 1000
        logger.info(f" All orders executed in {total_execution_time_ms:.2f}ms")
        
        # Process results and create execution records
        for i, result in enumerate(execution_results):
            meta = execution_metadata[i]
            account = meta["account"]
            leg_qty = meta["qty"]
            
            if isinstance(result, Exception):
                execution = TradeExecution(
                    trade_id=trade.trade_id,
                    account_id=account.account_id,
                    broker=account.broker_name,
                    status=OrderStatus.FAILED,
                    error_reason=str(result),
                    executed_quantity=leg_qty
                )
            else:
                execution = TradeExecution(
                    trade_id=trade.trade_id,
                    account_id=account.account_id,
                    broker=account.broker_name,
                    order_id=str(result.get("order_id")) if result.get("order_id") else None,
                    status=OrderStatus.SUCCESS if result.get("status") == "SUCCESS" else OrderStatus.FAILED,
                    executed_price=result.get("executed_price"),
                    executed_quantity=result.get("executed_quantity") or leg_qty,
                    error_reason=result.get("error")
                )
            
            self.db.add(execution)
        
        await self.db.commit()
        await self.db.refresh(trade)
        
        total_time = (time.time() - start_time) * 1000
        logger.info(f" Completed trade {trade.trade_id} in {total_time:.2f}ms total ({total_execution_time_ms:.2f}ms execution)")
        
        return trade
    
    async def _prepare_order_request(
        self,
        adapter: Any,
        account: Account,
        trade_request: TradeRequest,
        quantity: int
    ) -> Dict[str, Any]:
        """
        Prepare order request for a specific broker
        
        Args:
            adapter: Broker adapter
            account: Account model
            trade_request: Trade request
            
        Returns:
            Prepared order request dictionary
        """        
        
        # Common parameters
        order_params = {
            "symbol": trade_request.symbol,
            "tradingsymbol": trade_request.symbol,
            "scrip_code": getattr(trade_request, "scrip_code", None),            
            "exchange": trade_request.exchange,
            "transaction_type": trade_request.side.value if hasattr(trade_request.side, 'value') else trade_request.side,
            "quantity": quantity,
            "order_type": trade_request.order_type.value if hasattr(trade_request.order_type, 'value') else trade_request.order_type,
            "product": trade_request.product,
            "price": trade_request.price or 0,
            "trigger_price": trade_request.trigger_price or 0,
            "disclosed_quantity": trade_request.disclosed_quantity or 0,
            
            # Advanced fields
            "variety": trade_request.variety or "regular",
            "validity": trade_request.validity or "DAY",
            "target": trade_request.Target or 0,
            "stoploss": trade_request.Stoploss or 0,
            "trailing_stoploss": trade_request.trailing_stoploss or 0,
            "is_amo": trade_request.amo or False,
            "tag": trade_request.tag
        }
        
        return order_params
        
    async def _execute_single_order(
        self,
        trade: Trade,
        account: Account,
        adapter: Any,
        order_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a single order and measure timing
        
        Args:
            trade: Trade model
            account: Account model
            adapter: Broker adapter
            order_request: Prepared order request
            
        Returns:
            Execution result dictionary
        """
        try:
            start_time = time.time()
            result = await adapter.place_order(order_request)
            
            execution_time_ms = (time.time() - start_time) * 1000
            logger.info(f" {account.broker_name} order executed in {execution_time_ms:.2f}ms")
            
            # If successful, try to get executed price [may need to query order status]
            if result.get("status") == "SUCCESS":
                # For now we will use requested price as executed price
                # In production, we will query the order status from broker to get the actual executed price okaaay?
                result["executed_price"] = trade.price
                result["executed_quantity"] = order_request.get("quantity")
                result["execution_time_ms"] = execution_time_ms
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing order for account {account.account_id}: {e}")
            return {
                "order_id": None,
                "status": "FAILED",
                "broker": account.broker_name,
                "error": str(e)
            }