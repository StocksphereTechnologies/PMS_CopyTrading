"""
Unit tests for TradeReplicator — verifying order mapping and quantity multiplication.
Uses mock ZerodhaClient to avoid real API calls.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from app.services.trade_replicator import TradeReplicator


class TestTradeReplicator:
    """Test the trade replication mapping logic"""

    def _make_master_order(self, **overrides):
        """Helper to create a master order dict"""
        order = {
            "order_id": "MASTER_001",
            "tradingsymbol": "NIFTY2521420500CE",
            "exchange": "NFO",
            "transaction_type": "BUY",
            "quantity": 75,
            "filled_quantity": 75,
            "order_type": "LIMIT",
            "product": "NRML",
            "average_price": 245.50,
            "price": 246.00,
            "trigger_price": 0,
            "variety": "regular",
            "status": "COMPLETE",
            "order_timestamp": "2026-02-17 10:30:00",
        }
        order.update(overrides)
        return order

    def _make_pair(self, multiplier=1.0):
        """Helper to create a mock CopyTradingPair"""
        pair = MagicMock()
        pair.pair_id = 1
        pair.quantity_multiplier = multiplier
        pair.copy_modifications = True
        pair.copy_cancellations = True
        return pair

    @pytest.mark.asyncio
    async def test_basic_replication_market_order(self):
        """Master LIMIT filled → Child gets MARKET order with same qty"""
        pair = self._make_pair(multiplier=1.0)
        master_order = self._make_master_order()

        mock_client = AsyncMock()
        mock_client.place_order.return_value = {
            "order_id": "CHILD_001",
            "status": "SUCCESS",
        }

        mock_db = AsyncMock()

        log = await TradeReplicator.replicate_order(
            mock_db, pair, master_order, mock_client
        )

        # Verify place_order was called with correct params
        mock_client.place_order.assert_called_once()
        call_kwargs = mock_client.place_order.call_args
        assert call_kwargs.kwargs["tradingsymbol"] == "NIFTY2521420500CE"
        assert call_kwargs.kwargs["exchange"] == "NFO"
        assert call_kwargs.kwargs["transaction_type"] == "BUY"
        assert call_kwargs.kwargs["quantity"] == 75
        assert call_kwargs.kwargs["order_type"] == "MARKET"  # Always MARKET
        assert call_kwargs.kwargs["product"] == "NRML"

        # Verify log entry
        assert log.status == "SUCCESS"
        assert log.child_order_id == "CHILD_001"
        assert log.master_order_id == "MASTER_001"

    @pytest.mark.asyncio
    async def test_quantity_multiplier(self):
        """Multiplier 2.0 → child gets double quantity"""
        pair = self._make_pair(multiplier=2.0)
        master_order = self._make_master_order(quantity=75, filled_quantity=75)

        mock_client = AsyncMock()
        mock_client.place_order.return_value = {"order_id": "C1", "status": "SUCCESS"}
        mock_db = AsyncMock()

        log = await TradeReplicator.replicate_order(
            mock_db, pair, master_order, mock_client
        )

        call_kwargs = mock_client.place_order.call_args
        assert call_kwargs.kwargs["quantity"] == 150  # 75 × 2.0

    @pytest.mark.asyncio
    async def test_fractional_multiplier_floors(self):
        """Multiplier 0.5 → floors to integer (75 × 0.5 = 37)"""
        pair = self._make_pair(multiplier=0.5)
        master_order = self._make_master_order(quantity=75, filled_quantity=75)

        mock_client = AsyncMock()
        mock_client.place_order.return_value = {"order_id": "C1", "status": "SUCCESS"}
        mock_db = AsyncMock()

        log = await TradeReplicator.replicate_order(
            mock_db, pair, master_order, mock_client
        )

        call_kwargs = mock_client.place_order.call_args
        assert call_kwargs.kwargs["quantity"] == 37  # floor(75 × 0.5)

    @pytest.mark.asyncio
    async def test_zero_quantity_skipped(self):
        """Very small multiplier makes qty 0 → should be SKIPPED"""
        pair = self._make_pair(multiplier=0.001)
        master_order = self._make_master_order(quantity=1, filled_quantity=1)

        mock_client = AsyncMock()
        mock_db = AsyncMock()

        log = await TradeReplicator.replicate_order(
            mock_db, pair, master_order, mock_client
        )

        assert log.status == "SKIPPED"
        assert "0 after multiplier" in log.error_reason
        mock_client.place_order.assert_not_called()  # No order placed

    @pytest.mark.asyncio
    async def test_failed_order(self):
        """Child order placement fails → status should be FAILED"""
        pair = self._make_pair(multiplier=1.0)
        master_order = self._make_master_order()

        mock_client = AsyncMock()
        mock_client.place_order.return_value = {
            "order_id": None,
            "status": "FAILED",
            "error": "Insufficient margin",
        }
        mock_db = AsyncMock()

        log = await TradeReplicator.replicate_order(
            mock_db, pair, master_order, mock_client
        )

        assert log.status == "FAILED"
        assert "Insufficient margin" in log.error_reason

    @pytest.mark.asyncio
    async def test_exception_during_placement(self):
        """Exception during order placement → should be caught and logged as FAILED"""
        pair = self._make_pair(multiplier=1.0)
        master_order = self._make_master_order()

        mock_client = AsyncMock()
        mock_client.place_order.side_effect = Exception("Connection timeout")
        mock_db = AsyncMock()

        log = await TradeReplicator.replicate_order(
            mock_db, pair, master_order, mock_client
        )

        assert log.status == "FAILED"
        assert "Connection timeout" in log.error_reason

    @pytest.mark.asyncio
    async def test_sell_order_replication(self):
        """SELL order → child also gets SELL"""
        pair = self._make_pair(multiplier=1.0)
        master_order = self._make_master_order(transaction_type="SELL")

        mock_client = AsyncMock()
        mock_client.place_order.return_value = {"order_id": "C1", "status": "SUCCESS"}
        mock_db = AsyncMock()

        await TradeReplicator.replicate_order(
            mock_db, pair, master_order, mock_client
        )

        call_kwargs = mock_client.place_order.call_args
        assert call_kwargs.kwargs["transaction_type"] == "SELL"
