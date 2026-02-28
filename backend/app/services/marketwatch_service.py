"""
Marketwatch service for fetching and managing market data
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from app.models.account import Account, BrokerName
from app.services.account_service import AccountService
from app.adapters.zerodha_adapter import ZerodhaAdapter
from app.adapters.fivepaisa_adapter import FivePaisaAdapter
from app.core.cache import get_cache_value
from app.schemas.marketwatch import InstrumentData
import logging

logger = logging.getLogger(__name__)


class MarketwatchService:
    """Service for marketwatch functionality"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._adapters_cache: Dict[int, Any] = {}

    async def _get_adapter(self, account: Account):
        """Get or create broker adapter for account"""
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

    async def get_instruments(self, exchange: Optional[str] = None) -> List[InstrumentData]:
        """
        Fetch instruments from all enabled accounts and enrich them
        with latest real-time market data from Redis.

        NOTE:
        - This method MUST NOT call broker price APIs.
        - Prices come ONLY from Redis, which is fed by broker WebSockets
          (see `MarketDataStream` service).
        """
        accounts = await AccountService.get_all_accounts(self.db, enabled_only=True)

        if not accounts:
            logger.warning("No enabled accounts found")
            return []

        instruments: List[InstrumentData] = []

        for account in accounts:
            try:
                logger.info(
                    f"Fetching instruments from {account.broker_name} "
                    f"(account {account.account_id})"
                )

                adapter = await self._get_adapter(account)
                broker_instruments = await adapter.get_instruments(exchange)

                logger.info(
                    f"Received {len(broker_instruments) if broker_instruments else 0} "
                    f"instruments from {account.broker_name}"
                )

                if not broker_instruments:
                    continue

                for instrument in broker_instruments:
                    try:
                        normalized = await self._normalize_instrument(
                            instrument,
                            account.broker_name
                        )

                        await self._attach_realtime_tick(normalized, account.broker_name)

                        instruments.append(normalized)
                    except Exception as e:
                        logger.debug(f"Skipping instrument: {e}")
                        continue

            except Exception as e:
                logger.error(
                    f"Error fetching instruments from {account.broker_name}",
                    exc_info=True
                )
                continue

        logger.info(f"Total instruments returned: {len(instruments)}")
        return instruments

    async def _normalize_instrument(
        self,
        instrument: Dict[str, Any],
        broker_name: str
    ) -> InstrumentData:
        """Normalize broker-specific instrument format"""

        if broker_name == BrokerName.ZERODHA.value:
            return InstrumentData(
                symbol=instrument.get("tradingsymbol"),
                exchange=instrument.get("exchange"),
                instrument_token=str(instrument.get("instrument_token")),
                name=instrument.get("name"),
                last_price=None,
                change=None,
                change_percent=None,
                volume=None,
                high=None,
                low=None,
                open=None,
                close=None,
            )

        elif broker_name == BrokerName.FIVEPAISA.value:
            return InstrumentData(
                symbol=instrument.get("Name"),
                exchange=self._map_exchange_code(instrument.get("Exchange")),
                scrip_code=instrument.get("ScripCode"),
                name=instrument.get("Name"),
                last_price=None,
                change=None,
                change_percent=None,
                volume=None,
                high=None,
                low=None,
                open=None,
                close=None,
            )

        else:
            raise ValueError(f"Unsupported broker: {broker_name}")

    def _map_exchange_code(self, code: Optional[str]) -> str:
        """Map 5paisa exchange codes to standard format"""
        mapping = {"N": "NSE", "B": "BSE"}
        return mapping.get(code, code or "")

    async def _attach_realtime_tick(self, inst: InstrumentData, broker_name: str) -> None:
        """
        Attach latest real-time tick from Redis to an InstrumentData object.

        Keys used (populated by MarketDataStream):
        - Zerodha:  market:ZERODHA:{instrument_token}
        - 5paisa:   market:FIVEPAISA:{scrip_code}
        """
        try:
            if broker_name == BrokerName.ZERODHA.value and inst.instrument_token:
                cache_key = f"market:ZERODHA:{inst.instrument_token}"
            elif broker_name == BrokerName.FIVEPAISA.value and inst.scrip_code:
                cache_key = f"market:FIVEPAISA:{inst.scrip_code}"
            else:
                return

            tick = await get_cache_value(cache_key)
            if not tick or not isinstance(tick, dict):
                return

            inst.last_price = tick.get("ltp")
            inst.change = tick.get("change")
            inst.change_percent = tick.get("change_percent") or tick.get("pchange") or None
            inst.volume = tick.get("volume")
            inst.high = tick.get("high")
            inst.low = tick.get("low")
            inst.open = tick.get("open")
            inst.close = tick.get("close")
        except Exception as e:
            logger.debug(f"Error attaching realtime tick: {e}")

    async def get_ltp(self, symbol: str, exchange: str) -> Optional[float]:
        """
        Get LTP **only** from Redis (no direct broker calls).

        Strategy:
        - Find matching instruments for given symbol+exchange
          using static instrument directory (via get_instruments).
        - For each matching instrument, read its market:* key from Redis.
        - Return first non-null LTP found.
        """
        instruments = await self.get_instruments(exchange)

        candidates = [
            inst
            for inst in instruments
            if inst.symbol == symbol and inst.exchange == exchange
        ]

        for inst in candidates:
            tick = None
            if inst.instrument_token:
                tick = await get_cache_value(f"market:ZERODHA:{inst.instrument_token}")
            elif inst.scrip_code:
                tick = await get_cache_value(f"market:FIVEPAISA:{inst.scrip_code}")

            if tick and isinstance(tick, dict) and tick.get("ltp") is not None:
                return float(tick["ltp"])

        return None

    async def normalize_symbol(self, symbol: str, exchange: str) -> Dict[str, Any]:
        """Normalize symbol across brokers (used for trade execution)"""
        accounts = await AccountService.get_all_accounts(self.db, enabled_only=True)
        result: Dict[str, Any] = {}

        for account in accounts:
            try:
                adapter = await self._get_adapter(account)
                result[account.broker_name] = await adapter.normalize_symbol(
                    symbol, exchange
                )
            except Exception as e:
                logger.error(
                    f"Normalize symbol failed for {account.broker_name}: {e}"
                )
                continue

        return result
