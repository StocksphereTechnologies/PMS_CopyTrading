"""
Trade Replicator — maps a master's completed order to a child order and executes it.
Logs every action to CopyTradeLog.
"""
import logging
import math
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import CopyTradingPair, CopyTradeLog
from app.services.zerodha_client import ZerodhaClient

logger = logging.getLogger(__name__)


class TradeReplicator:
    """Replicates a master order onto the child account"""

    @staticmethod
    async def replicate_order(
        db: AsyncSession,
        pair: CopyTradingPair,
        master_order: Dict[str, Any],
        child_client: ZerodhaClient,
    ) -> CopyTradeLog:
        """
        Take a master's COMPLETE order and place the same trade on the child.
        
        Key decisions:
        - Always places MARKET order on child (master already filled, we want instant fill)
        - Applies quantity_multiplier from the pair settings
        - Copies: tradingsymbol, exchange, transaction_type, product
        - Logs result to CopyTradeLog
        
        Args:
            db: Database session
            pair: The copy trading pair config
            master_order: The master's order dict from GET /orders
            child_client: ZerodhaClient initialized with child's credentials
            
        Returns:
            CopyTradeLog entry
        """
        master_order_id = master_order.get("order_id", "unknown")
        tradingsymbol = master_order.get("tradingsymbol", "")
        exchange = master_order.get("exchange", "NSE")
        transaction_type = master_order.get("transaction_type", "BUY")
        # Use filled_quantity for COMPLETE orders, but for REJECTED/other statuses
        # filled_quantity is 0 — fall back to the requested quantity
        filled_qty = int(master_order.get("filled_quantity") or 0)
        requested_qty = int(master_order.get("quantity") or 0)
        master_qty = filled_qty if filled_qty > 0 else requested_qty
        product = master_order.get("product", "NRML")
        average_price = float(master_order.get("average_price", 0))
        variety = master_order.get("variety", "regular")
        order_type = master_order.get("order_type", "MARKET")
        trigger_price = float(master_order.get("trigger_price", 0))

        # Calculate child quantity using multiplier
        child_qty = math.floor(master_qty * pair.quantity_multiplier)
        if child_qty <= 0:
            logger.warning(f"Skipping order {master_order_id}: child qty is 0 after multiplier")
            log = CopyTradeLog(
                pair_id=pair.pair_id,
                master_order_id=master_order_id,
                tradingsymbol=tradingsymbol,
                exchange=exchange,
                transaction_type=transaction_type,
                quantity=0,
                order_type=order_type,
                product=product,
                price=average_price,
                trigger_price=trigger_price,
                status="SKIPPED",
                error_reason="Child quantity is 0 after multiplier",
                master_order_time=_parse_order_time(master_order),
            )
            db.add(log)
            await db.commit()
            return log

        # Create log entry (PENDING)
        log = CopyTradeLog(
            pair_id=pair.pair_id,
            master_order_id=master_order_id,
            tradingsymbol=tradingsymbol,
            exchange=exchange,
            transaction_type=transaction_type,
            quantity=child_qty,
            order_type="MARKET",  # Always MARKET on child
            product=product,
            price=average_price,
            trigger_price=trigger_price,
            status="PENDING",
            master_order_time=_parse_order_time(master_order),
        )

        try:
            # Determine child order_type and price:
            # - For AMO orders: Zerodha doesn't allow MARKET, so copy master's order_type & price
            # - For regular orders: use MARKET for instant fill (production behavior)
            if variety == "amo":
                child_order_type = order_type  # Copy master's type (LIMIT, SL, etc.)
                child_price = float(master_order.get("price") or average_price or 0)
            else:
                child_order_type = "MARKET"
                child_price = 0  # MARKET orders don't need price

            logger.info(
                f"Replicating: {transaction_type} {child_qty}x {tradingsymbol} "
                f"(master: {master_qty}x, multiplier: {pair.quantity_multiplier}, "
                f"variety: {variety}, type: {child_order_type})"
            )

            # Place order on child
            result = await child_client.place_order(
                tradingsymbol=tradingsymbol,
                exchange=exchange,
                transaction_type=transaction_type,
                quantity=child_qty,
                order_type=child_order_type,
                product=product,
                price=child_price,
                trigger_price=trigger_price,
                validity="DAY",
                variety=variety,
                tag="copier",
            )

            if result.get("status") == "SUCCESS":
                log.child_order_id = result.get("order_id")
                log.status = "SUCCESS"
                log.child_order_time = datetime.now(timezone.utc)
                logger.info(f"✅ Order replicated: {master_order_id} → {log.child_order_id}")
            else:
                log.status = "FAILED"
                log.error_reason = result.get("error", "Unknown error")
                logger.error(f"❌ Replication failed for {master_order_id}: {log.error_reason}")

        except Exception as e:
            log.status = "FAILED"
            log.error_reason = str(e)
            logger.error(f"❌ Replication exception for {master_order_id}: {e}")

        db.add(log)
        await db.commit()
        return log

    @staticmethod
    async def cancel_child_order(
        db: AsyncSession,
        pair: CopyTradingPair,
        master_order: Dict[str, Any],
        child_client: ZerodhaClient,
        child_order_id: str,
    ) -> bool:
        """Cancel a child order when the master order gets cancelled"""
        try:
            variety = master_order.get("variety", "regular")
            result = await child_client.cancel_order(child_order_id, variety)
            if result.get("status") == "SUCCESS":
                logger.info(f"✅ Child order {child_order_id} cancelled (master cancelled)")
                return True
            else:
                logger.error(f"❌ Failed to cancel child order {child_order_id}: {result.get('error')}")
                return False
        except Exception as e:
            logger.error(f"❌ Cancel exception: {e}")
            return False


def _parse_order_time(order: Dict) -> Optional[datetime]:
    """Parse order_timestamp from Zerodha order dict"""
    ts = order.get("order_timestamp")
    if ts is None:
        return None
    if isinstance(ts, datetime):
        return ts
    try:
        return datetime.fromisoformat(str(ts))
    except (ValueError, TypeError):
        return None
