"""
Zerodha margin adapter using KiteConnect API
"""
import logging
from typing import Dict, Any, Optional
from kiteconnect import KiteConnect
from app.models.account import Account
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class ZerodhaMarginAdapter:
    """Adapter for fetching margin data from Zerodha"""
    
    async def get_margins(self, account: Account) -> Optional[Dict[str, Any]]:
        """
        Fetch margin data from Zerodha using existing access token
        
        Args:
            account: Account model with Zerodha credentials
            
        Returns:
            Dictionary with margin data or None if failed
        """
        try:
            if not account.access_token:
                logger.error(f"No access token for Zerodha account {account.account_id}")
                return None
            
            if not account.api_key:
                logger.error(f"No API key for Zerodha account {account.account_id}")
                return None
            
            # Defensive check: Ensure access_token is a clean string
            token = account.access_token
            if not token:
                logger.error(f"No access token for Zerodha account {account.account_id}")
                return None
            
            # Recursive cleaning for any level of bytes/string-repr wrapping
            def deep_clean(t):
                if not t: return t
                if isinstance(t, bytes):
                    return deep_clean(t.decode('utf-8'))
                if isinstance(t, str):
                    t = t.strip()
                    # Strip wrapping quotes if they exist
                    if len(t) >= 2 and ((t[0] == "'" and t[-1] == "'") or (t[0] == '"' and t[-1] == '"')):
                        return deep_clean(t[1:-1])
                    # Handle b' prefix
                    if len(t) > 3 and t.startswith("b") and t[1] in ("'", '"') and t.endswith(t[1]):
                        return deep_clean(t[2:-1])
                    return t
                return str(t)
            
            token = deep_clean(token)
            print(f"DEBUG: Zerodha adapter account {account.account_id} token cleaned. Repr: {repr(token)[:40]}...", flush=True)
            
            # Initialize KiteConnect with API key
            kite = KiteConnect(api_key=account.api_key)
            
            # Set the existing access token (don't login again!)
            kite.set_access_token(token)
            
            logger.info(f"Fetching margins for Zerodha account {account.account_id}")
            
            # Fetch margins for all segments - using to_thread since kiteconnect is synchronous
            import asyncio
            margins = await asyncio.to_thread(kite.margins)
            
            logger.info(f"Successfully fetched margins for Zerodha account {account.account_id}")
            
            # Transform to unified format
            return self._transform_margins(margins, account)
            
        except Exception as e:
            logger.error(f"Error fetching Zerodha margins for account {account.account_id}: {e}", exc_info=True)
            return None
    
    def _transform_margins(self, raw_margins: Dict[str, Any], account: Account) -> Dict[str, Any]:
        """
        Transform Zerodha margin response to unified format
        
        Args:
            raw_margins: Raw margin data from Zerodha API
            account: Account model
            
        Returns:
            Transformed margin data
        """
        equity = raw_margins.get("equity", {})
        commodity = raw_margins.get("commodity", {})
        
        return {
            "account_id": account.account_id,
            "broker_name": account.broker_name,
            "nickname": account.nickname,
            "trading_login_id": account.trading_login_id,
            "equity": {
                "enabled": equity.get("enabled", True),
                "net": equity.get("net", 0.0),
                "available": {
                    "cash": equity.get("available", {}).get("cash", 0.0),
                    "opening_balance": equity.get("available", {}).get("opening_balance", 0.0),
                    "live_balance": equity.get("available", {}).get("live_balance", 0.0),
                    "collateral": equity.get("available", {}).get("collateral", 0.0),
                    "adhoc_margin": equity.get("available", {}).get("adhoc_margin", 0.0),
                    "intraday_payin": equity.get("available", {}).get("intraday_payin", 0.0),
                },
                "utilised": {
                    "debits": equity.get("utilised", {}).get("debits", 0.0),
                    "exposure": equity.get("utilised", {}).get("exposure", 0.0),
                    "m2m_realised": equity.get("utilised", {}).get("m2m_realised", 0.0),
                    "m2m_unrealised": equity.get("utilised", {}).get("m2m_unrealised", 0.0),
                    "option_premium": equity.get("utilised", {}).get("option_premium", 0.0),
                    "payout": equity.get("utilised", {}).get("payout", 0.0),
                    "span": equity.get("utilised", {}).get("span", 0.0),
                    "holding_sales": equity.get("utilised", {}).get("holding_sales", 0.0),
                    "turnover": equity.get("utilised", {}).get("turnover", 0.0),
                    "liquid_collateral": equity.get("utilised", {}).get("liquid_collateral", 0.0),
                    "stock_collateral": equity.get("utilised", {}).get("stock_collateral", 0.0),
                    "delivery": equity.get("utilised", {}).get("delivery", 0.0),
                }
            },
            "commodity": {
                "enabled": commodity.get("enabled", True),
                "net": commodity.get("net", 0.0),
                "available": {
                    "cash": commodity.get("available", {}).get("cash", 0.0),
                    "opening_balance": commodity.get("available", {}).get("opening_balance", 0.0),
                    "live_balance": commodity.get("available", {}).get("live_balance", 0.0),
                    "collateral": commodity.get("available", {}).get("collateral", 0.0),
                    "adhoc_margin": commodity.get("available", {}).get("adhoc_margin", 0.0),
                    "intraday_payin": commodity.get("available", {}).get("intraday_payin", 0.0),
                },
                "utilised": {
                    "debits": commodity.get("utilised", {}).get("debits", 0.0),
                    "exposure": commodity.get("utilised", {}).get("exposure", 0.0),
                    "m2m_realised": commodity.get("utilised", {}).get("m2m_realised", 0.0),
                    "m2m_unrealised": commodity.get("utilised", {}).get("m2m_unrealised", 0.0),
                    "option_premium": commodity.get("utilised", {}).get("option_premium", 0.0),
                    "payout": commodity.get("utilised", {}).get("payout", 0.0),
                    "span": commodity.get("utilised", {}).get("span", 0.0),
                    "holding_sales": commodity.get("utilised", {}).get("holding_sales", 0.0),
                    "turnover": commodity.get("utilised", {}).get("turnover", 0.0),
                    "liquid_collateral": commodity.get("utilised", {}).get("liquid_collateral", 0.0),
                    "stock_collateral": commodity.get("utilised", {}).get("stock_collateral", 0.0),
                    "delivery": commodity.get("utilised", {}).get("delivery", 0.0),
                }
            } if commodity else None,
            "last_updated": datetime.now(timezone.utc)
        }
    
    def _transform_margins(self, raw_margins: Dict[str, Any], account: Account) -> Dict[str, Any]:
        """
        Transform Zerodha margin response to unified format
        
        Args:
            raw_margins: Raw margin data from Zerodha API
            account: Account model
            
        Returns:
            Transformed margin data
        """
        equity = raw_margins.get("equity", {})
        commodity = raw_margins.get("commodity", {})
        
        return {
            "account_id": account.account_id,
            "broker_name": account.broker_name,
            "nickname": account.nickname,
            "trading_login_id": account.trading_login_id,
            "equity": {
                "enabled": equity.get("enabled", True),
                "net": equity.get("net", 0.0),
                "available": {
                    "cash": equity.get("available", {}).get("cash", 0.0),
                    "opening_balance": equity.get("available", {}).get("opening_balance", 0.0),
                    "live_balance": equity.get("available", {}).get("live_balance", 0.0),
                    "collateral": equity.get("available", {}).get("collateral", 0.0),
                    "adhoc_margin": equity.get("available", {}).get("adhoc_margin", 0.0),
                    "intraday_payin": equity.get("available", {}).get("intraday_payin", 0.0),
                },
                "utilised": {
                    "debits": equity.get("utilised", {}).get("debits", 0.0),
                    "exposure": equity.get("utilised", {}).get("exposure", 0.0),
                    "m2m_realised": equity.get("utilised", {}).get("m2m_realised", 0.0),
                    "m2m_unrealised": equity.get("utilised", {}).get("m2m_unrealised", 0.0),
                    "option_premium": equity.get("utilised", {}).get("option_premium", 0.0),
                    "payout": equity.get("utilised", {}).get("payout", 0.0),
                    "span": equity.get("utilised", {}).get("span", 0.0),
                    "holding_sales": equity.get("utilised", {}).get("holding_sales", 0.0),
                    "turnover": equity.get("utilised", {}).get("turnover", 0.0),
                    "liquid_collateral": equity.get("utilised", {}).get("liquid_collateral", 0.0),
                    "stock_collateral": equity.get("utilised", {}).get("stock_collateral", 0.0),
                    "delivery": equity.get("utilised", {}).get("delivery", 0.0),
                }
            },
            "commodity": {
                "enabled": commodity.get("enabled", True),
                "net": commodity.get("net", 0.0),
                "available": {
                    "cash": commodity.get("available", {}).get("cash", 0.0),
                    "opening_balance": commodity.get("available", {}).get("opening_balance", 0.0),
                    "live_balance": commodity.get("available", {}).get("live_balance", 0.0),
                    "collateral": commodity.get("available", {}).get("collateral", 0.0),
                    "adhoc_margin": commodity.get("available", {}).get("adhoc_margin", 0.0),
                    "intraday_payin": commodity.get("available", {}).get("intraday_payin", 0.0),
                },
                "utilised": {
                    "debits": commodity.get("utilised", {}).get("debits", 0.0),
                    "exposure": commodity.get("utilised", {}).get("exposure", 0.0),
                    "m2m_realised": commodity.get("utilised", {}).get("m2m_realised", 0.0),
                    "m2m_unrealised": commodity.get("utilised", {}).get("m2m_unrealised", 0.0),
                    "option_premium": commodity.get("utilised", {}).get("option_premium", 0.0),
                    "payout": commodity.get("utilised", {}).get("payout", 0.0),
                    "span": commodity.get("utilised", {}).get("span", 0.0),
                    "holding_sales": commodity.get("utilised", {}).get("holding_sales", 0.0),
                    "turnover": commodity.get("utilised", {}).get("turnover", 0.0),
                    "liquid_collateral": commodity.get("utilised", {}).get("liquid_collateral", 0.0),
                    "stock_collateral": commodity.get("utilised", {}).get("stock_collateral", 0.0),
                    "delivery": commodity.get("utilised", {}).get("delivery", 0.0),
                }
            } if commodity else None,
            "last_updated": datetime.now(timezone.utc)
        }
    
