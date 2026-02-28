"""
Order Poller — the heart of the trade copier system.
Background asyncio task that continuously polls the master's orders,
diffs against previous snapshot, and triggers replication.

Safety guards:
1. First poll = baseline only (no replication of old orders)
2. Timestamp guard (only copy orders placed AFTER copier started)
3. Network blip protection (don't reset snapshot on empty/error response)
4. DB-based dedup (already_copied_order_ids prevents double-copies on restart)
5. Graceful shutdown
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Set

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.models import CopyTradingPair, CopyTradeLog, ZerodhaAccount
from app.services.auto_login import auto_login_service
from app.services.order_differ import OrderDiffer
from app.services.trade_replicator import TradeReplicator
from app.services.zerodha_client import ZerodhaClient

logger = logging.getLogger(__name__)


class OrderPoller:
    """
    Manages polling loops for active copy-trading pairs.
    Each pair gets its own asyncio task.
    """

    def __init__(self):
        self._active_tasks: Dict[int, asyncio.Task] = {}   # pair_id → asyncio.Task
        self._stop_events: Dict[int, asyncio.Event] = {}   # pair_id → stop event

    @property
    def active_pair_ids(self) -> list:
        return list(self._active_tasks.keys())

    @property
    def active_count(self) -> int:
        return len(self._active_tasks)

    async def start_pair(self, pair_id: int):
        """Start polling for a specific pair"""
        if pair_id in self._active_tasks:
            logger.warning(f"Pair {pair_id} is already polling")
            return

        stop_event = asyncio.Event()
        self._stop_events[pair_id] = stop_event
        task = asyncio.create_task(self._polling_loop(pair_id, stop_event))
        self._active_tasks[pair_id] = task
        logger.info(f"▶ Started polling for pair {pair_id}")

    async def stop_pair(self, pair_id: int):
        """Stop polling for a specific pair"""
        if pair_id not in self._active_tasks:
            logger.warning(f"Pair {pair_id} is not polling")
            return

        self._stop_events[pair_id].set()
        task = self._active_tasks.pop(pair_id)
        self._stop_events.pop(pair_id)

        try:
            await asyncio.wait_for(task, timeout=10)
        except asyncio.TimeoutError:
            task.cancel()
        except asyncio.CancelledError:
            pass

        logger.info(f"■ Stopped polling for pair {pair_id}")

    async def stop_all(self):
        """Stop all active polling tasks"""
        pair_ids = list(self._active_tasks.keys())
        for pid in pair_ids:
            await self.stop_pair(pid)
        logger.info("■ All polling tasks stopped")

    async def _polling_loop(self, pair_id: int, stop_event: asyncio.Event):
        """
        Main polling loop for a copy-trading pair.

        Safety Flow:
        Poll #1 → Capture baseline snapshot, replicate NOTHING
        Poll #2+ → Diff against baseline, replicate only genuinely new orders
                    that were placed AFTER the copier started
        """
        previous_snapshot: Dict[str, Dict] = {}
        poll_interval = settings.POLL_INTERVAL_SECONDS
        differ = OrderDiffer()
        replicator = TradeReplicator()
        is_first_poll = True
        poll_started_at = datetime.now(timezone.utc)
        consecutive_errors = 0

        logger.info(f"Pair {pair_id}: polling loop started (interval={poll_interval}s)")
        logger.info(f"Pair {pair_id}: copier start time = {poll_started_at.isoformat()} UTC")
        logger.info(f"Pair {pair_id}: first poll will capture baseline only (no replication)")

        while not stop_event.is_set():
            try:
                async with AsyncSessionLocal() as db:
                    # ─── Load pair and accounts ───
                    pair = await db.get(CopyTradingPair, pair_id)
                    if not pair or not pair.is_active:
                        logger.warning(f"Pair {pair_id}: not found or inactive, stopping")
                        break

                    master = await db.get(ZerodhaAccount, pair.master_account_id)
                    child = await db.get(ZerodhaAccount, pair.child_account_id)

                    if not master or not child:
                        logger.error(f"Pair {pair_id}: master or child account missing")
                        break

                    # ─── Ensure tokens are valid ───
                    master_valid = await auto_login_service.ensure_valid_token(master)
                    child_valid = await auto_login_service.ensure_valid_token(child)

                    if not master_valid:
                        logger.error(f"Pair {pair_id}: master token refresh failed, retrying next cycle")
                        await asyncio.sleep(poll_interval)
                        continue

                    if not child_valid:
                        logger.error(f"Pair {pair_id}: child token refresh failed, retrying next cycle")
                        await asyncio.sleep(poll_interval)
                        continue

                    # Persist any token updates
                    db.add(master)
                    db.add(child)
                    await db.commit()

                    # ─── Create clients ───
                    master_client = ZerodhaClient(master.api_key, master.access_token)
                    child_client = ZerodhaClient(child.api_key, child.access_token)

                    # ─── Fetch master's orders ───
                    orders = await master_client.get_orders()

                    # ═══════════════════════════════════════════
                    # SAFETY #3: Network blip protection
                    # If the API returned nothing but we had orders before,
                    # it's likely a network error — don't reset the snapshot
                    # ═══════════════════════════════════════════
                    if not orders and previous_snapshot:
                        consecutive_errors += 1
                        if consecutive_errors <= 3:
                            logger.warning(
                                f"Pair {pair_id}: GET /orders returned empty but we had "
                                f"{len(previous_snapshot)} orders before — keeping previous snapshot "
                                f"(error #{consecutive_errors})"
                            )
                            # Don't update snapshot, don't process
                            await _wait_for_next_poll(stop_event, poll_interval)
                            continue
                        else:
                            # After 3 consecutive empty responses, accept it as real
                            logger.info(
                                f"Pair {pair_id}: {consecutive_errors} consecutive empty responses, "
                                f"accepting as real (orders cleared for the day)"
                            )

                    if orders:
                        consecutive_errors = 0  # Reset error counter on success

                    current_snapshot = differ.build_snapshot(orders)

                    # ═══════════════════════════════════════════
                    # SAFETY #1: First poll = baseline only
                    # Capture all existing orders but don't replicate any.
                    # This prevents copying old/cancelled orders from hours ago.
                    # ═══════════════════════════════════════════
                    if is_first_poll:
                        previous_snapshot = current_snapshot
                        is_first_poll = False
                        if current_snapshot:
                            logger.info(
                                f"Pair {pair_id}: ✅ Baseline captured — "
                                f"{len(current_snapshot)} existing orders snapshotted (NOT replicated)"
                            )
                            for oid, o in current_snapshot.items():
                                logger.info(
                                    f"  [baseline] {oid[:12]}.. | "
                                    f"{o.get('transaction_type', '?')} {o.get('quantity', '?')}x "
                                    f"{o.get('tradingsymbol', '?')} | "
                                    f"status={o.get('status', '?')}"
                                )
                        else:
                            logger.info(f"Pair {pair_id}: ✅ Baseline captured — no existing orders")

                        await _wait_for_next_poll(stop_event, poll_interval)
                        continue

                    # ─── Debug: Log when new orders appear ───
                    new_order_ids = set(current_snapshot.keys()) - set(previous_snapshot.keys())
                    if new_order_ids:
                        logger.info(f"Pair {pair_id}: {len(new_order_ids)} new order(s) since last poll")
                        for oid in new_order_ids:
                            o = current_snapshot[oid]
                            logger.info(
                                f"  → {oid[:12]}.. | "
                                f"{o.get('transaction_type', '?')} {o.get('quantity', '?')}x "
                                f"{o.get('tradingsymbol', '?')} | "
                                f"status={o.get('status', '?')} | "
                                f"filled={o.get('filled_quantity', 0)}"
                            )

                    # ─── Get already copied order IDs from DB ───
                    already_copied = await _get_copied_order_ids(db, pair_id)

                    # ─── Diff ───
                    newly_completed, modified, cancelled = differ.diff(
                        previous_snapshot, current_snapshot, already_copied
                    )

                    # ═══════════════════════════════════════════
                    # SAFETY #4: Timestamp guard
                    # Only replicate orders placed AFTER the copier started.
                    # Prevents copying historical orders if DB is cleared.
                    # ═══════════════════════════════════════════
                    if newly_completed:
                        filtered = []
                        for order in newly_completed:
                            order_time = _parse_order_time(order)
                            if order_time and order_time < poll_started_at:
                                logger.info(
                                    f"  [SKIPPED] {order.get('order_id', '?')[:12]}.. "
                                    f"({order.get('tradingsymbol')}) — placed before copier started "
                                    f"(order: {order_time.isoformat()}, copier: {poll_started_at.isoformat()})"
                                )
                            else:
                                filtered.append(order)
                        newly_completed = filtered

                    if newly_completed:
                        logger.info(f"Pair {pair_id}: 🔔 {len(newly_completed)} order(s) to replicate!")
                    if cancelled:
                        logger.info(f"Pair {pair_id}: ❌ {len(cancelled)} cancelled order(s)")

                    # ─── Replicate newly completed orders ───
                    for order in newly_completed:
                        logger.info(
                            f"Pair {pair_id}: Replicating "
                            f"{order.get('transaction_type')} {order.get('quantity')}x "
                            f"{order.get('tradingsymbol')}"
                        )
                        await replicator.replicate_order(db, pair, order, child_client)

                    # ─── Handle cancellations (if enabled) ───
                    if pair.copy_cancellations and cancelled:
                        for order in cancelled:
                            child_oid = await _find_child_order_id(
                                db, pair_id, order.get("order_id", "")
                            )
                            if child_oid:
                                await replicator.cancel_child_order(
                                    db, pair, order, child_client, child_oid
                                )

                    # ─── Update snapshot ───
                    previous_snapshot = current_snapshot

            except Exception as e:
                logger.error(f"Pair {pair_id}: polling error: {e}", exc_info=True)

            # ─── Wait for next poll ───
            should_stop = await _wait_for_next_poll(stop_event, poll_interval)
            if should_stop:
                break

        logger.info(f"Pair {pair_id}: polling loop exited")


# ═══════════════════════════════════════════════
# Helper functions
# ═══════════════════════════════════════════════

async def _wait_for_next_poll(stop_event: asyncio.Event, interval: float) -> bool:
    """Wait for poll interval or stop event. Returns True if should stop."""
    try:
        await asyncio.wait_for(stop_event.wait(), timeout=interval)
        return True  # stop_event was set
    except asyncio.TimeoutError:
        return False  # Normal timeout, poll again


async def _get_copied_order_ids(db: AsyncSession, pair_id: int) -> Set[str]:
    """Get all master order IDs that have already been copied for this pair"""
    result = await db.execute(
        select(CopyTradeLog.master_order_id).where(
            CopyTradeLog.pair_id == pair_id,
            CopyTradeLog.status.in_(["SUCCESS", "FAILED", "SKIPPED"]),
        )
    )
    return set(row[0] for row in result.fetchall())


async def _find_child_order_id(db: AsyncSession, pair_id: int, master_order_id: str) -> str:
    """Find the child order_id for a given master order"""
    result = await db.execute(
        select(CopyTradeLog.child_order_id).where(
            CopyTradeLog.pair_id == pair_id,
            CopyTradeLog.master_order_id == master_order_id,
            CopyTradeLog.status == "SUCCESS",
        )
    )
    row = result.first()
    return row[0] if row else None


def _parse_order_time(order: Dict) -> datetime:
    """Parse order_timestamp from Zerodha order dict, returns UTC datetime"""
    import pytz
    ts = order.get("order_timestamp")
    if ts is None:
        return None
    if isinstance(ts, datetime):
        if ts.tzinfo is None:
            # Assume IST (Zerodha always returns IST)
            ist = pytz.timezone("Asia/Kolkata")
            return ist.localize(ts).astimezone(pytz.UTC)
        return ts.astimezone(pytz.UTC)
    try:
        dt = datetime.fromisoformat(str(ts))
        if dt.tzinfo is None:
            ist = pytz.timezone("Asia/Kolkata")
            return ist.localize(dt).astimezone(pytz.UTC)
        return dt.astimezone(pytz.UTC)
    except (ValueError, TypeError):
        return None


# Singleton
order_poller = OrderPoller()
