"""
Unit tests for OrderDiffer — the core diffing logic.
Tests detection of new, filled, cancelled, and modified orders.
"""
import pytest
from app.services.order_differ import OrderDiffer


class TestOrderDiffer:
    """Test the order diffing engine"""

    def setup_method(self):
        self.differ = OrderDiffer()

    # ── Test: Brand new COMPLETE order ──

    def test_detect_new_complete_order(self):
        """New order_id that wasn't in previous snapshot → should detect"""
        previous = {}
        current = {
            "ORD001": {
                "order_id": "ORD001",
                "tradingsymbol": "NIFTY2521420500CE",
                "exchange": "NFO",
                "transaction_type": "BUY",
                "quantity": 75,
                "status": "COMPLETE",
            }
        }
        completed, modified, cancelled = self.differ.diff(previous, current, set())

        assert len(completed) == 1
        assert completed[0]["order_id"] == "ORD001"
        assert len(modified) == 0
        assert len(cancelled) == 0

    # ── Test: Order transitions from OPEN → COMPLETE ──

    def test_detect_order_fill(self):
        """Order was OPEN before, now COMPLETE → should detect"""
        previous = {
            "ORD001": {
                "order_id": "ORD001",
                "tradingsymbol": "RELIANCE",
                "status": "OPEN",
                "quantity": 10,
            }
        }
        current = {
            "ORD001": {
                "order_id": "ORD001",
                "tradingsymbol": "RELIANCE",
                "status": "COMPLETE",
                "quantity": 10,
            }
        }
        completed, modified, cancelled = self.differ.diff(previous, current, set())

        assert len(completed) == 1
        assert completed[0]["order_id"] == "ORD001"

    # ── Test: Already copied order should be skipped ──

    def test_skip_already_copied_order(self):
        """Order in already_copied set → should NOT detect"""
        previous = {}
        current = {
            "ORD001": {
                "order_id": "ORD001",
                "tradingsymbol": "INFY",
                "status": "COMPLETE",
                "quantity": 25,
            }
        }
        completed, _, _ = self.differ.diff(previous, current, {"ORD001"})

        assert len(completed) == 0  # Skipped!

    # ── Test: Already COMPLETE stays COMPLETE → no double detect ──

    def test_no_double_detection(self):
        """Same COMPLETE order in both snapshots → skip (already seen)"""
        order = {
            "order_id": "ORD001",
            "tradingsymbol": "INFY",
            "status": "COMPLETE",
            "quantity": 25,
        }
        previous = {"ORD001": order}
        current = {"ORD001": order}

        completed, _, _ = self.differ.diff(previous, current, set())

        assert len(completed) == 0  # Already was COMPLETE in previous

    # ── Test: Order cancelled ──

    def test_detect_cancellation(self):
        """Order was OPEN, now CANCELLED → should detect"""
        previous = {
            "ORD001": {
                "order_id": "ORD001",
                "tradingsymbol": "SBIN",
                "status": "OPEN",
                "quantity": 100,
            }
        }
        current = {
            "ORD001": {
                "order_id": "ORD001",
                "tradingsymbol": "SBIN",
                "status": "CANCELLED",
                "quantity": 100,
            }
        }
        _, _, cancelled = self.differ.diff(previous, current, set())

        assert len(cancelled) == 1
        assert cancelled[0]["order_id"] == "ORD001"

    # ── Test: Order modified (price change) ──

    def test_detect_modification(self):
        """Order price changed while still OPEN → should detect"""
        previous = {
            "ORD001": {
                "order_id": "ORD001",
                "tradingsymbol": "TATAMOTORS",
                "status": "OPEN",
                "quantity": 50,
                "price": 420.5,
                "trigger_price": 0,
            }
        }
        current = {
            "ORD001": {
                "order_id": "ORD001",
                "tradingsymbol": "TATAMOTORS",
                "status": "OPEN",
                "quantity": 50,
                "price": 425.0,  # Changed!
                "trigger_price": 0,
            }
        }
        _, modified, _ = self.differ.diff(previous, current, set())

        assert len(modified) == 1
        assert modified[0]["price"] == 425.0

    # ── Test: Pending order (not COMPLETE) → skip ──

    def test_skip_pending_order(self):
        """New order that is still OPEN → should NOT detect as completed"""
        previous = {}
        current = {
            "ORD001": {
                "order_id": "ORD001",
                "tradingsymbol": "HDFCBANK",
                "status": "OPEN",
                "quantity": 10,
            }
        }
        completed, _, _ = self.differ.diff(previous, current, set())

        assert len(completed) == 0

    # ── Test: Empty order lists ──

    def test_empty_lists(self):
        """Both snapshots empty → no changes"""
        completed, modified, cancelled = self.differ.diff({}, {}, set())
        assert len(completed) == 0
        assert len(modified) == 0
        assert len(cancelled) == 0

    # ── Test: build_snapshot utility ──

    def test_build_snapshot(self):
        """Test the snapshot builder"""
        orders = [
            {"order_id": "A", "status": "COMPLETE"},
            {"order_id": "B", "status": "OPEN"},
            {"order_id": "C", "status": "REJECTED"},
        ]
        snapshot = self.differ.build_snapshot(orders)

        assert len(snapshot) == 3
        assert "A" in snapshot
        assert "B" in snapshot
        assert snapshot["A"]["status"] == "COMPLETE"

    # ── Test: Multiple new orders at once ──

    def test_multiple_new_complete_orders(self):
        """Multiple new COMPLETE orders in one poll → detect all"""
        previous = {}
        current = {
            "O1": {"order_id": "O1", "tradingsymbol": "NIFTY", "status": "COMPLETE", "quantity": 75},
            "O2": {"order_id": "O2", "tradingsymbol": "BANKNIFTY", "status": "COMPLETE", "quantity": 25},
            "O3": {"order_id": "O3", "tradingsymbol": "RELIANCE", "status": "OPEN", "quantity": 10},  # Still open
        }
        completed, _, _ = self.differ.diff(previous, current, set())

        assert len(completed) == 2
        order_ids = {o["order_id"] for o in completed}
        assert order_ids == {"O1", "O2"}
