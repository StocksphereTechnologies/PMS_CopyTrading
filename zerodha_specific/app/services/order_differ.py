"""
Order Differ — detects new/modified/cancelled orders by comparing snapshots.
Stateless: takes two order lists and returns the differences.
"""
import logging
from typing import Dict, List, Tuple, Set

from app.core.config import settings

logger = logging.getLogger(__name__)


class OrderDiffer:
    """
    Compares two snapshots of Zerodha orders to detect changes.
    
    Snapshot format: {order_id: order_dict, ...}
    
    Modes:
    - Production (COPY_ALL_STATUSES=False): Only copies COMPLETE orders
    - Test mode  (COPY_ALL_STATUSES=True):  Copies ANY new order immediately,
      regardless of status, so you can verify the flow works
    """

    # Statuses that mean "order has been filled"
    COMPLETE_STATUSES = {"COMPLETE"}
    # Statuses that mean "order is still open/pending"
    OPEN_STATUSES = {
        "OPEN", "TRIGGER PENDING", "VALIDATION PENDING",
        "PUT ORDER REQ RECEIVED", "OPEN PENDING",
        "AMO REQ RECEIVED",
    }
    # Statuses that mean "order is dead"
    DEAD_STATUSES = {"CANCELLED", "REJECTED"}

    @staticmethod
    def build_snapshot(orders: List[Dict]) -> Dict[str, Dict]:
        """Convert order list to {order_id: order_dict} snapshot"""
        snapshot = {}
        for order in orders:
            oid = order.get("order_id")
            if oid:
                snapshot[oid] = order
        return snapshot

    @staticmethod
    def diff(
        previous: Dict[str, Dict],
        current: Dict[str, Dict],
        already_copied_order_ids: Set[str],
    ) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """
        Compare previous and current order snapshots.
        
        Returns:
            Tuple of (newly_completed, modified_orders, newly_cancelled)
        """
        newly_completed = []
        modified_orders = []
        newly_cancelled = []

        test_mode = settings.COPY_ALL_STATUSES

        for order_id, order in current.items():
            status = (order.get("status") or "").upper()

            # ═══════════════════════════════════════════
            # TEST MODE: Copy ANY new order immediately
            # ═══════════════════════════════════════════
            if test_mode:
                if order_id in already_copied_order_ids:
                    continue

                prev = previous.get(order_id)
                if prev is None:
                    # Brand new order — copy it regardless of status
                    newly_completed.append(order)
                    logger.info(
                        f"🔔 [TEST] New order detected: {order_id} "
                        f"({order.get('tradingsymbol')}) status={status}"
                    )
                continue  # Skip all other checks in test mode

            # ═══════════════════════════════════════════
            # PRODUCTION MODE: Only copy COMPLETE orders
            # ═══════════════════════════════════════════

            # ─── New COMPLETE order ───
            if status in OrderDiffer.COMPLETE_STATUSES:
                if order_id in already_copied_order_ids:
                    continue

                prev = previous.get(order_id)
                if prev is None:
                    newly_completed.append(order)
                    logger.info(f"NEW COMPLETE order: {order_id} ({order.get('tradingsymbol')})")
                elif (prev.get("status") or "").upper() not in OrderDiffer.COMPLETE_STATUSES:
                    newly_completed.append(order)
                    logger.info(
                        f"Order FILLED: {order_id} ({order.get('tradingsymbol')}) "
                        f"{prev.get('status')} → COMPLETE"
                    )

            # ─── Cancelled order ───
            elif status == "CANCELLED":
                prev = previous.get(order_id)
                if prev is not None and (prev.get("status") or "").upper() != "CANCELLED":
                    newly_cancelled.append(order)
                    logger.info(f"Order CANCELLED: {order_id} ({order.get('tradingsymbol')})")

            # ─── Modified open order ───
            elif status in OrderDiffer.OPEN_STATUSES:
                prev = previous.get(order_id)
                if prev is not None and (prev.get("status") or "").upper() in OrderDiffer.OPEN_STATUSES:
                    if (
                        prev.get("quantity") != order.get("quantity")
                        or prev.get("price") != order.get("price")
                        or prev.get("trigger_price") != order.get("trigger_price")
                    ):
                        modified_orders.append(order)
                        logger.info(f"Order MODIFIED: {order_id} ({order.get('tradingsymbol')})")

        return newly_completed, modified_orders, newly_cancelled
