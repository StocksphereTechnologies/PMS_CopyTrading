"""
Broker interface - common interface for all broker adapters
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from app.schemas.marketwatch import InstrumentData


class BrokerInterface(ABC):
    """Abstract base class for broker adapters"""
    
    @abstractmethod
    async def get_instruments(self, exchange: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch instruments from broker
        
        Args:
            exchange: Optional exchange filter (NSE, BSE, etc.)
            
        Returns:
            List of instrument dictionaries
        """
        pass
    
    @abstractmethod
    async def get_ltp(self, symbol: str, exchange: str) -> Optional[float]:
        """
        Get Last Traded Price for a symbol
        
        Args:
            symbol: Trading symbol
            exchange: Exchange name
            
        Returns:
            Last traded price or None
        """
        pass
    
    @abstractmethod
    async def place_order(self, order_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Place an order
        
        Args:
            order_request: Order details dictionary
            
        Returns:
            Order response with order_id and status
        """
        pass
    
    @abstractmethod
    async def normalize_symbol(self, symbol: str, exchange: str) -> Dict[str, Any]:
        """
        Normalize symbol to broker-specific format
        
        Args:
            symbol: Standard symbol
            exchange: Exchange name
            
        Returns:
            Dictionary with broker-specific symbol details
        """
        pass
