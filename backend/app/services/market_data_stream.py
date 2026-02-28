"""
Real-time market data streaming service using WebSocket
"""
import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import websockets
from app.core.cache import get_cache, set_cache
from app.models.account import Account, BrokerName
from app.services.account_service import AccountService
from sqlalchemy.ext.asyncio import AsyncSession
import pyotp
from app.core.encryption import encryption_service

logger = logging.getLogger(__name__)


class MarketDataStream:
    """Real-time market data streaming for brokers"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.websocket_connections: Dict[int, Any] = {}
        self.subscribed_symbols: Set[str] = set()
        self.running = False
    
    async def start_streaming(self):
        """Start streaming market data for all enabled accounts"""
        self.running = True
        
        accounts = await AccountService.get_all_accounts(self.db, enabled_only=True)
        
        for account in accounts:
            if account.broker_name != BrokerName.ZERODHA.value:
                logger.info(
                    f"Skipping WebSocket for account {account.account_id} ({account.broker_name}) - "
                    f"only Zerodha WebSocket is used for market data"
                )
                continue
            
            from sqlalchemy import select
            result = await self.db.execute(
                select(Account).where(Account.account_id == account.account_id)
            )
            fresh_account = result.scalar_one_or_none()
            
            if not fresh_account:
                logger.warning(f"Account {account.account_id} not found in database")
                continue
            
            logger.info(f"Starting Zerodha WebSocket for account {fresh_account.account_id}")
            asyncio.create_task(self._stream_zerodha(fresh_account))
    
    async def _stream_zerodha(self, account: Account):
        """Stream real-time data from Zerodha WebSocket"""
        try:
            from kiteconnect import KiteTicker
            from app.services.login.zerodha_login_service import ZerodhaLoginService
            
            # CRITICAL: Ensure we have a valid access_token before starting WebSocket
            login_service = ZerodhaLoginService()
            
            # Check and refresh token if needed
            if not await login_service.ensure_valid_token(account):
                logger.error(
                    f" Cannot start Zerodha WebSocket for account {account.account_id}: "
                    f"no valid access_token. Auto-login failed."
                )
                return
            
            if not account.access_token:
                logger.error(
                    f" Cannot start Zerodha WebSocket for account {account.account_id}: "
                    f"access_token is None"
                )
                return
            
            logger.info(
                f" Starting Zerodha WebSocket for account {account.account_id} "
                f"(token generated at: {account.token_generated_at})"
            )
            
            logger.debug(f"API Key: {account.api_key}")
            logger.debug(f"Access Token (first 30 chars): {account.access_token[:30]}...")
            
            kite_ticker = KiteTicker(account.api_key, account.access_token)
            
            # Store tick data in Redis
            def on_ticks(ws, ticks):
                """
                Zerodha tick structure (MODE_FULL) typically includes:
                - instrument_token
                - last_price
                - ohlc: {open, high, low, close}
                - volume
                - change
                - depth (bid/ask book) if enabled
                """
                for tick in ticks:
                    try:
                        instrument_token = tick.get("instrument_token")
                        ltp = tick.get("last_price")
                        change = tick.get("change")
                        volume = tick.get("volume")
                        ohlc = tick.get("ohlc") or {}
                        depth = tick.get("depth") or {}

                        if instrument_token and ltp is not None:
                            # Canonical market data payload
                            tick_data = {
                                "ltp": ltp,
                                "change": change,
                                "volume": volume,
                                "open": ohlc.get("open"),
                                "high": ohlc.get("high"),
                                "low": ohlc.get("low"),
                                "close": ohlc.get("close"),
                                "depth": depth,
                                "timestamp": datetime.now().isoformat(),
                            }

                            # Primary key as per spec: market:ZERODHA:{instrument_token}
                            market_key = f"market:ZERODHA:{instrument_token}"

                            # Also optional generic LTP key for convenience
                            ltp_key = f"ltp:ZERODHA:{instrument_token}"

                            # Fire-and-forget async writes
                            asyncio.create_task(set_cache(market_key, tick_data, expire=5))
                            asyncio.create_task(set_cache(ltp_key, tick_data, expire=5))
                    except Exception as e:
                        logger.error(f"Error processing Zerodha tick: {e}")
            
            def on_connect(ws, response):
                logger.info(f" Zerodha WebSocket connected for account {account.account_id}")
                logger.debug(f"Connection response: {response}")
                # Subscribe to instruments
                try:
                    # Get instruments to subscribe
                    from kiteconnect import KiteConnect
                    kite = KiteConnect(api_key=account.api_key)
                    kite.set_access_token(account.access_token)
                    instruments = kite.instruments("NSE")
                    
                    # Get first 500 instrument tokens for subscription (limit to avoid overload)
                    tokens = [inst['instrument_token'] for inst in instruments[:500] if inst.get('instrument_token')]
                    if tokens:
                        ws.subscribe(tokens)
                        ws.set_mode(ws.MODE_FULL, tokens)  # Full mode for all data
                        logger.info(f"Subscribed to {len(tokens)} Zerodha instruments for real-time data")
                except Exception as e:
                    logger.error(f"Error subscribing to Zerodha instruments: {e}")
            
            def on_close(ws, code, reason):
                logger.warning(f"Zerodha WebSocket closed for account {account.account_id}: {reason}")
                logger.debug(f"Close code: {code}")
            
            def on_error(ws, code, reason):
                logger.error(f" Zerodha WebSocket error for account {account.account_id}")
                logger.error(f"Error code: {code}")
                logger.error(f"Error reason: {reason}")
            
            kite_ticker.on_ticks = on_ticks
            kite_ticker.on_connect = on_connect
            kite_ticker.on_close = on_close
            kite_ticker.on_error = on_error
            
            # Connect and keep running
            kite_ticker.connect(threaded=True)
            self.websocket_connections[account.account_id] = kite_ticker
            
        except Exception as e:
            logger.error(f"Error setting up Zerodha WebSocket for account {account.account_id}: {e}")
    
    async def _stream_fivepaisa(self, account: Account):
        """Stream real-time data from 5paisa WebSocket"""
        try:
            from py5paisa import FivePaisaClient
            
            mpin = encryption_service.decrypt(account.encrypted_password)
            totp_secret = encryption_service.decrypt(account.encrypted_totp_secret)
            totp = pyotp.TOTP(totp_secret)
            
            cred = {
                "APP_NAME": account.api_key or "",
                "APP_SOURCE": account.app_source or "10074",
                "USER_ID": account.trading_login_id,
                "PASSWORD": mpin,
                "USER_KEY": account.user_key or "",
                "ENCRYPTION_KEY": account.api_secret or "",
                "TOTP": totp.now()
            }
            
            client = FivePaisaClient(cred=cred)
            
            redirect_server = "C"
            if account.access_token and not account.access_token.startswith("5paisa_session_"):
                try:
                    import base64
                    import json as json_lib
                    
                    parts = account.access_token.split('.')
                    if len(parts) >= 2:
                        payload = parts[1]
                        padding = 4 - len(payload) % 4
                        if padding != 4:
                            payload += '=' * padding
                        
                        decoded_bytes = base64.urlsafe_b64decode(payload)
                        decoded = json_lib.loads(decoded_bytes)
                        redirect_server = decoded.get("RedirectServer", "C")
                        logger.info(f"Decoded RedirectServer from token: {redirect_server}")
                except Exception as decode_error:
                    logger.debug(f"Could not decode JWT token: {decode_error}, using default RedirectServer C")
                    redirect_server = "C"
            
            ws_url_map = {
                "C": "wss://openfeed.5paisa.com/feeds",
                "A": "wss://aopenfeed.5paisa.com/feeds",
                "B": "wss://bopenfeed.5paisa.com/feeds"
            }
            ws_url = ws_url_map.get(redirect_server, "wss://openfeed.5paisa.com/feeds")
            
            if not ws_url.startswith("wss://") and not ws_url.startswith("ws://"):
                ws_url = ws_url.replace("http://", "wss://").replace("https://", "wss://")
            
            logger.info(f"Connecting to 5paisa WebSocket: {ws_url}")
            
            if hasattr(client, 'connect_ws'):
                logger.info("Checking py5paisa's connect_ws method...")
                
                try:
                    if hasattr(client, 'ws_url'):
                        client_ws_url = client.ws_url
                        if client_ws_url and not client_ws_url.startswith("wss://") and not client_ws_url.startswith("ws://"):
                            logger.warning(f"py5paisa client has invalid WS URL: {client_ws_url}, using manual connection")
                        else:
                            logger.info(f"Using py5paisa's connect_ws with URL: {client_ws_url}")
                            def on_message(ws, message):
                                try:
                                    import json as json_lib
                                    data = json_lib.loads(message) if isinstance(message, str) else message
                                    loop = asyncio.get_event_loop()
                                    if loop.is_running():
                                        asyncio.create_task(self._process_fivepaisa_tick(data, account.account_id))
                                except Exception as e:
                                    logger.error(f"Error in WebSocket callback: {e}")
                            
                            client.connect_ws(on_message=on_message)
                            logger.info(" 5paisa WebSocket connected via py5paisa")
                            while self.running:
                                await asyncio.sleep(1)
                            return
                    else:
                        logger.info("Attempting py5paisa connect_ws (no URL validation possible)")
                        def on_message(ws, message):
                            try:
                                import json as json_lib
                                data = json_lib.loads(message) if isinstance(message, str) else message
                                loop = asyncio.get_event_loop()
                                if loop.is_running():
                                    asyncio.create_task(self._process_fivepaisa_tick(data, account.account_id))
                            except Exception as e:
                                logger.error(f"Error in WebSocket callback: {e}")
                        
                        try:
                            client.connect_ws(on_message=on_message)
                            logger.info(" 5paisa WebSocket connected via py5paisa")
                            while self.running:
                                await asyncio.sleep(1)
                            return
                        except Exception as ws_error:
                            logger.warning(f"py5paisa connect_ws failed: {ws_error}, falling back to manual connection")
                except Exception as check_error:
                    logger.warning(f"Error checking py5paisa WebSocket: {check_error}, using manual connection")
            
            if not ws_url.startswith("wss://") and not ws_url.startswith("ws://"):
                logger.error(f"Invalid WebSocket URL format: {ws_url}, fixing...")
                ws_url = ws_url.replace("http://", "wss://").replace("https://", "wss://")
            
            if not ws_url.startswith("wss://"):
                logger.error(f"WebSocket URL still invalid after fix: {ws_url}")
                return
            
            logger.info(f"Connecting to 5paisa WebSocket manually: {ws_url}")
            
            async with websockets.connect(ws_url) as websocket:
                self.websocket_connections[account.account_id] = websocket
                logger.info(f"5paisa WebSocket connected for account {account.account_id}")
                
                
                while self.running:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(message)
                        
                        await self._process_fivepaisa_tick(data, account.account_id)
                        
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        logger.error(f"Error processing 5paisa WebSocket message: {e}")
                        break
                        
        except Exception as e:
            logger.error(f"Error setting up 5paisa WebSocket for account {account.account_id}: {e}")
    
    async def _process_fivepaisa_tick(self, data: Dict[str, Any], account_id: int):
        """Process 5paisa tick data and store in Redis"""
        try:
            # Extract market data from 5paisa WebSocket message
            # Format depends on 5paisa's WebSocket protocol
            scrip_code = data.get("ScripCode") or data.get("scrip_code") or data.get("ScripCode")
            ltp = data.get("LastRate") or data.get("LTP") or data.get("last_price") or data.get("LastRate")
            change = data.get("Change") or data.get("change")
            volume = data.get("Volume") or data.get("volume")
            high = data.get("High") or data.get("high")
            low = data.get("Low") or data.get("low")
            open_price = data.get("Open") or data.get("open")
            close = data.get("Close") or data.get("close")
            
            if scrip_code and ltp is not None:
                # Canonical tick payload (align with Zerodha as much as possible)
                tick_data = {
                    "ltp": ltp,
                    "change": change,
                    "volume": volume,
                    "high": high,
                    "low": low,
                    "open": open_price,
                    "close": close,
                    "timestamp": datetime.now().isoformat(),
                }

                # Primary key as per spec: market:FIVEPAISA:{scrip_code}
                market_key = f"market:FIVEPAISA:{scrip_code}"

                # Optional generic LTP key
                ltp_key = f"ltp:FIVEPAISA:{scrip_code}"

                await set_cache(market_key, tick_data, expire=5)
                await set_cache(ltp_key, tick_data, expire=5)

                # Also store full raw tick data (for debugging / depth etc.)
                tick_key = f"tick:FIVEPAISA:{scrip_code}"
                await set_cache(tick_key, data, expire=5)
                
        except Exception as e:
            logger.error(f"Error processing 5paisa tick: {e}")
    
    async def stop_streaming(self):
        """Stop all WebSocket connections"""
        self.running = False
        for account_id, connection in self.websocket_connections.items():
            try:
                if hasattr(connection, 'close'):
                    connection.close()
                elif hasattr(connection, 'disconnect'):
                    connection.disconnect()
            except Exception as e:
                logger.error(f"Error closing WebSocket for account {account_id}: {e}")
