"""
5paisa position adapter using direct API calls
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.models.account import Account
from app.core.http import HttpClient
from app.schemas.position import Position

logger = logging.getLogger(__name__)

class FivePaisaPositionAdapter:
    """Adapter for fetching position data from 5paisa"""
    
    async def get_positions(self, account: Account) -> List[Position]:
        """
        Fetch positions from 5paisa using direct API call
        
        Args:
            account: Account model with 5paisa credentials
            
        Returns:
            List of Position schemas
        """
        try:
            token = account.access_token
            if not token:
                logger.error(f"No access token for 5paisa account {account.account_id}")
                return []

            # Headers Configuration
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
                "5Paisa-API-Uid": "ka7SFqAU6SC"
            }

            # Payload Configuration
            payload = {
                "head": {
                    "key": account.user_key
                },
                "body": {
                    "ClientCode": account.trading_login_id
                }
            }

            url = "https://Openapi.5paisa.com/VendorsAPI/Service1.svc/V2/NetPositionNetWise"
            
            print(f"DEBUG: Executing direct 5paisa Positions API call for account {account.account_id}...", flush=True)
            
            client = HttpClient.get_client()
            response = await client.post(url, json=payload, headers=headers, timeout=10.0)
            
            if response.status_code != 200:
                logger.error(f"5paisa Positions API Error {response.status_code} for account {account.account_id}: {response.text}")
                return []
                
            resp_data = response.json()
            raw_positions = resp_data.get("body", {}).get("NetPositionDetail", [])
            print(f"DEBUG: 5paisa account {account.account_id} raw positions count: {len(raw_positions)}", flush=True)
            
            if not raw_positions:
                return []
            
            logger.info(f"Successfully fetched {len(raw_positions)} raw positions from 5paisa for account {account.account_id}")
            
            # Map to unified schema
            return [self._map_position(pos, account) for pos in raw_positions]
            
        except Exception as e:
            logger.error(f"Error in FivePaisaPositionAdapter for account {account.account_id}: {e}", exc_info=True)
            return []

    def _map_position(self, p: Dict[str, Any], account: Account) -> Position:
        """Map 5paisa raw position to unified Position schema"""
        
        net_qty = int(p.get("NetQty", 0))
        buy_qty = int(p.get("BuyQty", 0))
        sell_qty = int(p.get("SellQty", 0))
        
        buy_val = float(p.get("BuyValue", 0.0))
        sell_val = float(p.get("SellValue", 0.0))
        
        # Calculate direction
        direction = "NEUTRAL"
        if net_qty > 0:
            direction = "LONG"
        elif net_qty < 0:
            direction = "SHORT"

        return Position(
            id=str(p.get("ScripCode", "")),
            symbol=p.get("ScripName", ""),
            m2m=float(p.get("MTOM", 0.0)),
            pnl=float(p.get("BookedPL", 0.0)),
            atpnl=float(p.get("MTOM", 0.0)), # Mapping MTOM to AT PnL as placeholder
            realpl=float(p.get("BookedPL", 0.0)),
            unrealpl=0.0, # 5paisa netwise simplified
            netqty=net_qty,
            ltp=float(p.get("LTP", 0.0)),
            buyqty=buy_qty,
            sellqty=sell_qty,
            buyval=buy_val,
            sellval=sell_val,
            netval=buy_val - sell_val,
            bavg=float(p.get("BuyAvgRate", 0.0)),
            savg=float(p.get("SellAvgRate", 0.0)),
            state=p.get("PositionType", ""),
            direction=direction,
            type=p.get("ProductType", ""),
            category=p.get("Exchange", ""),
            broker="5Paisa",
            overqty=int(p.get("DeliveryQty", 0)),
            multiplier=float(p.get("Multiplier", 1.0)),
            exch=p.get("Exchange", ""),
            brexch=p.get("Exchange", ""),
            brsymbol=p.get("ScripName", ""),
            day="NET",
            platform="WEB",
            accid=account.trading_login_id,
            account_id=account.account_id,
            last_updated=datetime.now(timezone.utc)
        )
