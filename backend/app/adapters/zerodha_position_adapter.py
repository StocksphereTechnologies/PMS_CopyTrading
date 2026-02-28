"""
Zerodha position adapter using KiteConnect API
"""
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from kiteconnect import KiteConnect
from app.models.account import Account
from app.schemas.position import Position

logger = logging.getLogger(__name__)

class ZerodhaPositionAdapter:
    """Adapter for fetching position data from Zerodha"""
    
    async def get_positions(self, account: Account) -> List[Position]:
        """
        Fetch positions from Zerodha using KiteConnect
        
        Args:
            account: Account model with Zerodha credentials
            
        Returns:
            List of Position schemas
        """
        try:
            if not account.access_token or not account.api_key:
                logger.error(f"Missing credentials for Zerodha account {account.account_id}")
                return []
            
            # Defensive cleaning (same as margin adapter)
            token = account.access_token
            if isinstance(token, bytes):
                token = token.decode('utf-8')
            token = token.strip().replace("'", "").replace('"', "")
            if token.startswith("b") and len(token) > 2:
                 token = token[1:]

            # Initialize KiteConnect
            kite = KiteConnect(api_key=account.api_key)
            kite.set_access_token(token)
            
            # Fetch positions (synchronous call wrapped in thread)
            raw_data = await asyncio.to_thread(kite.positions)
            print(f"DEBUG: Zerodha account {account.account_id} raw response keys: {list(raw_data.keys())}", flush=True)
            
            # Zerodha returns {"day": [], "net": []}
            net_positions = raw_data.get("net", [])
            print(f"DEBUG: Zerodha account {account.account_id} net positions count: {len(net_positions)}", flush=True)
            
            if not net_positions:
                return []
            
            logger.info(f"Successfully fetched {len(net_positions)} net positions from Zerodha for account {account.account_id}")
            
            # Map to unified schema
            return [self._map_position(pos, account) for pos in net_positions]
            
        except Exception as e:
            logger.error(f"Error in ZerodhaPositionAdapter for account {account.account_id}: {e}", exc_info=True)
            return []

    def _map_position(self, p: Dict[str, Any], account: Account) -> Position:
        """Map Zerodha raw position to unified Position schema"""
        
        net_qty = int(p.get("quantity", 0))
        buy_qty = int(p.get("buy_quantity", 0))
        sell_qty = int(p.get("sell_quantity", 0))
        
        # Calculate direction
        direction = "NEUTRAL"
        if net_qty > 0:
            direction = "LONG"
        elif net_qty < 0:
            direction = "SHORT"

        return Position(
            id=str(p.get("instrument_token", "")),
            symbol=p.get("tradingsymbol", ""),
            m2m=float(p.get("m2m", 0.0)),
            pnl=float(p.get("pnl", 0.0)),
            atpnl=float(p.get("pnl", 0.0)),
            realpl=float(p.get("realised", 0.0)),
            unrealpl=float(p.get("unrealised", 0.0)),
            netqty=net_qty,
            ltp=float(p.get("last_price", 0.0)),
            buyqty=buy_qty,
            sellqty=sell_qty,
            buyval=float(p.get("buy_value", 0.0)),
            sellval=float(p.get("sell_value", 0.0)),
            netval=float(p.get("buy_value", 0.0)) - float(p.get("sell_value", 0.0)),
            bavg=float(p.get("buy_price", 0.0)),
            savg=float(p.get("sell_price", 0.0)),
            state=p.get("product", ""), # NRML, MIS etc
            direction=direction,
            type=p.get("product", ""),
            category=p.get("exchange", ""),
            broker="Zerodha",
            overqty=int(p.get("overnight_quantity", 0)),
            multiplier=float(p.get("multiplier", 1.0)),
            exch=p.get("exchange", ""),
            brexch=p.get("exchange", ""),
            brsymbol=p.get("tradingsymbol", ""),
            day="NET",
            platform="Kite",
            accid=account.trading_login_id,
            account_id=account.account_id,
            last_updated=datetime.now(timezone.utc)
        )
