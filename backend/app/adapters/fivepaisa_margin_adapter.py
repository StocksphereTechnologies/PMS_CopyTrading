"""
5paisa margin adapter using py5paisa library
"""
import logging
import httpx
from typing import Dict, Any, Optional
from app.models.account import Account
from app.core.encryption import encryption_service
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class FivePaisaMarginAdapter:
    """Adapter for fetching margin data from 5paisa"""
    
    async def get_margins(self, account: Account) -> Optional[Dict[str, Any]]:
        """
        Fetch margin data from 5paisa using existing access token
        
        Args:
            account: Account model with 5paisa credentials
            
        Returns:
            Dictionary with margin data or None if failed
        """
        try:
            
            token = account.access_token
            if not token:
                logger.error(f"No access token for 5paisa account {account.account_id}")
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
            
            clean_token = deep_clean(token)
            print(f"DEBUG: 5paisa adapter (Direct API) account {account.account_id} token cleaned.", flush=True)

            # 5paisa Headers Configuration
            # used the official py5paisa Fingerprint to avoid "Invalid Vendor" errors
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {clean_token}",
                "5Paisa-API-Uid": "ka7SFqAU6SC" # Official Python SDK Vendor ID agent ne diya
            }
            
            
            # Replicating the exact GENERIC_PAYLOAD structure used by py5paisa
            payload = {
                "head": {
                    "key": account.user_key
                },
                "body": {
                    "ClientCode": account.trading_login_id
                }
            }

            url = "https://Openapi.5paisa.com/VendorsAPI/Service1.svc/V4/Margin"
            
            print(f"DEBUG: Executing direct 5paisa API call for account {account.account_id}...", flush=True)
            
            from app.core.http import HttpClient
            client = HttpClient.get_client()
            response = await client.post(url, json=payload, headers=headers, timeout=10.0)
                
            if response.status_code != 200:
                logger.error(f"5paisa API Error {response.status_code} for account {account.account_id}: {response.text}")
                return None
                
            resp_data = response.json()
            
            
            
            if resp_data.get("head", {}).get("status") != "0":
                error_msg = resp_data.get("head", {}).get("statusDescription", "Unknown error")
                logger.error(f"5paisa logical error for account {account.account_id}: {error_msg}")
                return None
                
            margin_list = resp_data.get("body", {}).get("EquityMargin", [])
            
            if not margin_list:
                logger.error(f"No margin data in response for account {account.account_id}")
                return None
            
            logger.info(f"Successfully fetched margins (Direct API) for account {account.account_id}")
            
            # Transform to unified format
            return self._transform_margins(margin_list[0], account)
            
        except Exception as e:
            logger.error(f"Error fetching direct 5paisa margins for account {account.account_id}: {e}", exc_info=True)
            return None
    
    def _transform_margins(self, raw_margin: Dict[str, Any], account: Account) -> Dict[str, Any]:
        """
        Transform 5paisa margin response to unified format
        
        Args:
            raw_margin: Raw margin data from 5paisa API
            account: Account model
            
        Returns:
            Transformed margin data
        """
        # 5paisa returns combined margin data, we'll put it in equity segment
        net_available = raw_margin.get("NetAvailableMargin", 0.0)
        utilized = raw_margin.get("MarginUtilized", 0.0)
        collateral = raw_margin.get("CollateralValueAfterHairCut", 0.0)
        adhoc = raw_margin.get("AdhocMargin", 0.0)
        
        return {
            "account_id": account.account_id,
            "broker_name": account.broker_name,
            "nickname": account.nickname,
            "trading_login_id": account.trading_login_id,
            "equity": {
                "enabled": True,
                "net": net_available,
                "available": {
                    "cash": net_available,
                    "opening_balance": raw_margin.get("Ledgerbalance", 0.0),
                    "live_balance": net_available,
                    "collateral": collateral,
                    "adhoc_margin": adhoc,
                    "intraday_payin": raw_margin.get("FundsPayIn", 0.0),
                },
                "utilised": {
                    "debits": utilized,
                    "exposure": 0.0,  # Not provided by 5paisa
                    "m2m_realised": raw_margin.get("TodaysLoss", 0.0),
                    "m2m_unrealised": 0.0,  # Not provided by 5paisa
                    "option_premium": 0.0,  # Not provided by 5paisa
                    "payout": raw_margin.get("FundsWithdrawal", 0.0),
                    "span": raw_margin.get("DerivativeMargin", 0.0),
                    "holding_sales": 0.0,  # Not provided by 5paisa
                    "turnover": 0.0,  # Not provided by 5paisa
                    "liquid_collateral": 0.0,  # Not provided by 5paisa
                    "stock_collateral": 0.0,  # Not provided by 5paisa
                    "delivery": 0.0,  # Not provided by 5paisa
                }
            },
            "commodity": None,  # 5paisa doesn't separate commodity
            "last_updated": datetime.now(timezone.utc)
        }
    
