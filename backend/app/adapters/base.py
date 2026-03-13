"""Base broker interface"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from app.schemas.marketwatch import InstrumentData
from app.schemas.trade import TradeRequest


class BrokerInterface(ABC):
    """Base interface for broker adapters"""
    
    @abstractmethod
    async def get_instruments(self, exchange: Optional[str] = None) -> List[Dict]:
        """
        Fetch instruments from broker
        Returns list of instrument dictionaries
        """
        pass
    
    @abstractmethod
    async def get_ltp(self, symbol: str, exchange: str) -> Optional[float]:
        """
        Get last traded price for a symbol
        Returns LTP or None if not found
        """
        pass
    
    @abstractmethod
    async def place_order(self, order_request: TradeRequest) -> Dict:
        """
        Place order with broker
        Returns dict with order_id, status, etc.
        """
        pass
    
    @abstractmethod
    def normalize_symbol(self, symbol: str, exchange: str) -> str:
        """
        Normalize symbol format for this broker
        Returns normalized symbol string
        """
        pass

    @abstractmethod
    async def get_margins(self) -> Dict:
        """
        Fetch margin data from broker
        Returns dict with margin data
        """
        pass

    @abstractmethod
    async def get_positions(self) -> List[Dict]:
        """
        Fetch positions from broker
        Returns list of position dictionaries
        """
        pass

    @abstractmethod
    async def get_orders(self) -> List[Dict]:
        """
        Fetch orders from broker
        Returns list of order dictionaries
        """
        pass