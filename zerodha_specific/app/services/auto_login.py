"""
Automated Zerodha login service
Same raw httpx POST request approach as the main system's ZerodhaAutoAuth
Login → TOTP 2FA → request_token → access_token
"""
import asyncio
import httpx
import pyotp
import logging
from datetime import datetime, timedelta, time as dt_time
from typing import Dict, Any
from urllib.parse import urlparse, parse_qs

import pytz
from kiteconnect import KiteConnect

from app.core.config import settings
from app.core.encryption import encryption_service

logger = logging.getLogger(__name__)


class AutoLoginService:
    """
    Automated Zerodha login using raw HTTP requests (no browser/selenium).
    
    Flow:
    1. POST /api/login       (user_id + password) → request_id
    2. POST /api/twofa       (request_id + TOTP)  → session cookies
    3. GET  /connect/login    (api_key)            → redirect with request_token
    4. kite.generate_session  (request_token, api_secret) → access_token
    """

    def __init__(self):
        self.login_url = f"{settings.ZERODHA_LOGIN_BASE_URL}/api/login"
        self.twofa_url = f"{settings.ZERODHA_LOGIN_BASE_URL}/api/twofa"

    async def login(
        self,
        client_id: str,
        password: str,
        totp_secret: str,
        api_key: str,
        api_secret: str,
    ) -> Dict[str, Any]:
        """
        Perform complete automated login handshake.
        Returns {"success": True, "access_token": "...", "token_generated_at": datetime}
        or {"success": False, "error": "..."}
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://kite.zerodha.com/",
        }

        async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
            try:
                # ─── Step 1: Login ───
                logger.info(f"[AutoLogin] Step 1: Login for {client_id}...")
                resp = await client.post(self.login_url, data={
                    "user_id": client_id,
                    "password": password,
                })
                login_data = resp.json()

                if login_data.get("status") != "success":
                    error = login_data.get("message", "Login failed")
                    logger.error(f"[AutoLogin] Step 1 FAILED: {error}")
                    return {"success": False, "error": error}

                request_id = login_data["data"]["request_id"]
                logger.info(f"[AutoLogin] Step 1 SUCCESS: request_id obtained")

                # ─── Step 2: TOTP 2FA ───
                logger.info(f"[AutoLogin] Step 2: TOTP 2FA...")
                otp = pyotp.TOTP(totp_secret).now()
                resp = await client.post(self.twofa_url, data={
                    "user_id": client_id,
                    "request_id": request_id,
                    "twofa_value": otp,
                    "skip_session": "true",
                })
                twofa_data = resp.json()

                if twofa_data.get("status") != "success":
                    error = twofa_data.get("message", "2FA failed")
                    logger.error(f"[AutoLogin] Step 2 FAILED: {error}")
                    return {"success": False, "error": f"2FA/TOTP failed: {error}"}

                logger.info(f"[AutoLogin] Step 2 SUCCESS: 2FA passed")

                # ─── Step 3: Get request_token ───
                # IMPORTANT: Do NOT follow redirects here! The redirect URL points to
                # your Kite Connect app's redirect_url (e.g., http://127.0.0.1) which
                # may not have a server listening. We just need the Location header.
                logger.info(f"[AutoLogin] Step 3: Getting request_token...")
                connect_url = f"https://kite.zerodha.com/connect/login?v=3&api_key={api_key}"

                # Use a separate client with follow_redirects=False for Step 3
                async with httpx.AsyncClient(headers=headers, cookies=client.cookies, follow_redirects=False) as no_redirect_client:
                    resp = await no_redirect_client.get(connect_url)

                    # Zerodha may issue multiple 302 redirects before the final one with request_token
                    max_redirects = 5
                    for _ in range(max_redirects):
                        if resp.status_code in (301, 302, 303, 307, 308):
                            location = resp.headers.get("location", "")
                            if "request_token=" in location:
                                final_url = location
                                break
                            # Follow intermediate redirects (within kite.zerodha.com)
                            if location.startswith("/"):
                                location = f"https://kite.zerodha.com{location}"
                            if "kite.zerodha.com" in location or "kite.trade" in location:
                                resp = await no_redirect_client.get(location)
                            else:
                                # This is the redirect to our redirect_url — grab it without following
                                final_url = location
                                break
                        else:
                            # Not a redirect — check the final URL
                            final_url = str(resp.url)
                            break
                    else:
                        final_url = resp.headers.get("location", str(resp.url))

                if "request_token=" not in final_url:
                    logger.error(f"[AutoLogin] Step 3 FAILED: no request_token in URL: {final_url}")
                    return {"success": False, "error": "Failed to obtain request_token"}

                parsed = urlparse(final_url)
                params = parse_qs(parsed.query)
                request_token = params.get("request_token", [None])[0]

                if not request_token:
                    return {"success": False, "error": "Request token parsing failed"}

                logger.info(f"[AutoLogin] Step 3 SUCCESS: request_token obtained")

                # ─── Step 4: Generate session (access_token) ───
                logger.info(f"[AutoLogin] Step 4: Generating access_token...")
                kite = KiteConnect(api_key=api_key)
                session = await asyncio.to_thread(
                    kite.generate_session, request_token, api_secret
                )

                access_token = session.get("access_token")
                if not access_token:
                    return {"success": False, "error": "Session generation returned no access_token"}

                logger.info(f"[AutoLogin] ALL STEPS COMPLETE: Login successful!")
                return {
                    "success": True,
                    "access_token": access_token,
                    "token_generated_at": session.get("login_time") or datetime.now(pytz.UTC),
                }

            except Exception as e:
                logger.error(f"[AutoLogin] Exception: {str(e)}", exc_info=True)
                return {"success": False, "error": str(e)}

    def is_token_valid(self, token_generated_at: datetime) -> bool:
        """
        Check if token is still valid.
        Zerodha tokens expire daily at 7:30 AM IST.
        """
        if not token_generated_at:
            return False

        ist = pytz.timezone("Asia/Kolkata")
        utc = pytz.UTC

        if token_generated_at.tzinfo is None:
            token_generated_at = utc.localize(token_generated_at)

        token_time_ist = token_generated_at.astimezone(ist)
        current_time_ist = datetime.now(ist)

        today_730am_ist = ist.localize(
            datetime.combine(current_time_ist.date(), dt_time(7, 30, 0))
        )

        if current_time_ist >= today_730am_ist:
            cutoff = today_730am_ist
        else:
            cutoff = today_730am_ist - timedelta(days=1)

        is_expired = token_time_ist < cutoff
        logger.debug(
            f"Token check: generated={token_time_ist:%Y-%m-%d %H:%M %Z}, "
            f"cutoff={cutoff:%Y-%m-%d %H:%M %Z}, expired={is_expired}"
        )
        return not is_expired

    async def ensure_valid_token(self, account) -> bool:
        """
        Check token validity, re-login if expired.
        Updates the account object in-place with new token.
        Returns True if token is now valid.
        """
        if account.access_token and account.token_generated_at:
            if self.is_token_valid(account.token_generated_at):
                return True

        logger.info(f"Account {account.account_id}: Token expired or missing, re-logging in...")

        # Decrypt credentials
        password = encryption_service.decrypt(account.encrypted_password)
        totp_secret = encryption_service.decrypt(account.encrypted_totp_secret)

        result = await self.login(
            client_id=account.trading_login_id,
            password=password,
            totp_secret=totp_secret,
            api_key=account.api_key,
            api_secret=account.api_secret,
        )

        if result.get("success"):
            account.access_token = result["access_token"]
            account.token_generated_at = result["token_generated_at"]
            account.is_validated = True
            return True

        logger.error(f"Account {account.account_id}: Re-login failed: {result.get('error')}")
        return False


# Singleton
auto_login_service = AutoLoginService()
