"""
Automated authentication for Zerodha
Simulates the browser login flow to obtain a request_token without manual intervention (add acc creds, then click validate, raw fast http post request will get you accesstoken easy! )
"""
import httpx
import pyotp
import logging
import re
from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from kiteconnect import KiteConnect

logger = logging.getLogger(__name__)

class ZerodhaAutoAuth:
    """
    Login -> 2FA (TOTP) -> Request Token -> Access Token
    """
    
    def __init__(self):
        self.base_url = "https://kite.zerodha.com"
        self.login_url = f"{self.base_url}/api/login"
        self.twofa_url = f"{self.base_url}/api/twofa"
        
    async def get_access_token(self, account_id: int, client_id: str, password: str, totp_secret: str, api_key: str, api_secret: str) -> Dict[str, Any]:
        """
        Performs the complete automated login handshake.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://kite.zerodha.com/",
        }
        
        async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
            try:
                print(f"DEBUG: [Zerodha AutoAuth] Step 1: Starting login for {client_id}...", flush=True)
                
                login_payload = {
                    "user_id": client_id,
                    "password": password
                }
                
                resp = await client.post(self.login_url, data=login_payload)
                login_data = resp.json()
                
                if login_data.get("status") != "success":
                    error = login_data.get("message", "Login failed")
                    logger.error(f"Account {account_id}: Login initial step failed: {error}")
                    return {"success": False, "error": error}
                
                request_id = login_data["data"]["request_id"]
                print(f"DEBUG: [Zerodha AutoAuth] Step 1 Success: Login initial step successful, request_id obtained.", flush=True)
                logger.info(f"Account {account_id}: Login step 1 success, request_id obtained")
                
                
                print(f"DEBUG: [Zerodha AutoAuth] Step 2: Performing 2FA (TOTP)...", flush=True)
                otp = pyotp.TOTP(totp_secret).now()
                twofa_payload = {
                    "user_id": client_id,
                    "request_id": request_id,
                    "twofa_value": otp,
                    "skip_session": "true"
                }
                
                resp = await client.post(self.twofa_url, data=twofa_payload)
                twofa_data = resp.json()
                
                if twofa_data.get("status") != "success":
                    error = twofa_data.get("message", "2FA failed")
                    logger.error(f"Account {account_id}: 2FA step failed: {error}")
                    return {"success": False, "error": f"2FA/TOTP failed: {error}"}
                
                print(f"DEBUG: [Zerodha AutoAuth] Step 2 Success: 2FA successful, proceeding to obtain request_token.", flush=True)
                logger.info(f"Account {account_id}: 2FA success, proceeding to obtain request_token")
                
                # After 2FA Zerodha redirects to the finish URL which contains the request_token Since we are using Kite Connect flow, we need to hit the connect URL first to get the proper redirect okay?!
                
                connect_url = f"https://kite.zerodha.com/connect/login?v=3&api_key={api_key}"
                resp = await client.get(connect_url)
                
                final_url = str(resp.url)
                logger.info(f"Account {account_id}: Final redirect URL obtained")
                
                if "request_token=" not in final_url:
                    logger.error(f"Account {account_id}: request_token not found in redirect URL: {final_url}")
                    return {"success": False, "error": "Failed to obtain request_token"}
                
                # Extracting request_token from the URL
                parsed_url = urlparse(final_url)
                query_params = parse_qs(parsed_url.query)
                request_token = query_params.get("request_token", [None])[0]
                
                if not request_token:
                    logger.error(f"Account {account_id}: Could not parse request_token from URL")
                    return {"success": False, "error": "Request token parsing failed"}
                
                print(f"DEBUG: [Zerodha AutoAuth] Step 3: request_token extracted successfully.", flush=True)
                logger.info(f"Account {account_id}: Request token obtained successfully")
                
                
                print(f"DEBUG: [Zerodha AutoAuth] Final Step: Generating session access_token...", flush=True)
                kite = KiteConnect(api_key=api_key)
                # generate_session is synchronous in kiteconnect library so we run it in a thread to avoid blocking the event loop this makes it more faster 
                import asyncio
                session = await asyncio.to_thread(kite.generate_session, request_token, api_secret)
                
                access_token = session.get("access_token")
                
                if not access_token:
                    logger.error(f"Account {account_id}: generate_session did not return access_token")
                    return {"success": False, "error": "Kite session generation failed"}
                
                print(f"DEBUG: [Zerodha AutoAuth] ALL STEPS COMPLETE: Automated login successful!", flush=True)
                logger.info(f"Account {account_id}: Automated login successful!")
                return {
                    "success": True,
                    "access_token": access_token,
                    "token_generated_at": session.get("login_time") or datetime.now()
                }
                
            except Exception as e:
                logger.error(f"Account {account_id}: Automated login exception: {str(e)}", exc_info=True)
                return {"success": False, "error": str(e)}

    @staticmethod
    def get_auto_auth():
        return ZerodhaAutoAuth()