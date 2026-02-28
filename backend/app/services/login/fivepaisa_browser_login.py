# selenium automation automating stuff to get access token and request token from 5paisa also saving screenshots and logs for debugging (i am facing timeout issue in this script )
import logging
import asyncio
import time
from datetime import datetime
from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qs

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
import pyotp
import httpx

from app.models.account import Account
from app.core.encryption import encryption_service

logger = logging.getLogger(__name__)


class FivePaisaBrowserLogin:
    """Handles fully automated browser-based OAuth login for 5paisa using Selenium"""
    
    def __init__(self):
        self.oauth_url = "https://Openapi.5paisa.com/WebVendorLogin/VLogin/Index"
        self.access_token_url = "https://Openapi.5paisa.com/VendorsAPI/Service1.svc/GetAccessToken"
        self.callback_url = "http://localhost:8000/callback"
    
    async def login(self, account: Account) -> Dict[str, Any]:
        """
        Perform fully automated OAuth login using Selenium
        
        Args:
            account: Account model with encrypted credentials
            
        Returns:
            Dictionary with success status, access_token, and token_generated_at
        """
        try:
            password = encryption_service.decrypt(account.encrypted_password)
            totp_secret = encryption_service.decrypt(account.encrypted_totp_secret)
            
            logger.info(f"Starting automated 5paisa OAuth login for account {account.account_id}")
            
            request_token = await asyncio.to_thread(
                self._automated_oauth_login,
                account.trading_login_id,
                password,
                totp_secret,
                account.api_key
            )
            
            if not request_token:
                error_msg = "Failed to get request token from 5paisa OAuth"
                logger.error(error_msg)
                return {
                    "success": False,
                    "access_token": None,
                    "token_generated_at": None,
                    "error": error_msg
                }
            
            logger.info(f"Request token obtained: {request_token[:30]}...")
            
            access_token_data = await self._exchange_for_access_token(
                request_token,
                account.api_key,
                account.api_secret,
                account.trading_login_id
            )
            
            if not access_token_data or 'access_token' not in access_token_data:
                error_msg = "Failed to exchange request token for access token"
                logger.error(error_msg)
                return {
                    "success": False,
                    "access_token": None,
                    "token_generated_at": None,
                    "error": error_msg
                }
            
            logger.info(f"Access token generated for account {account.account_id}")
            
            return {
                "success": True,
                "access_token": access_token_data['access_token'],
                "client_code": access_token_data.get('client_code'),
                "token_generated_at": datetime.utcnow(),
                "error": None
            }
        
        except Exception as e:
            error_msg = f"5paisa OAuth login failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "access_token": None,
                "token_generated_at": None,
                "error": error_msg
            }
    
    def _automated_oauth_login(
        self,
        client_code: str,
        pin: str,
        totp_secret: str,
        api_key: str
    ) -> Optional[str]:
        """
        Automate the OAuth login flow using Selenium
        
        Returns:
            RequestToken if successful, None otherwise
        """
        driver = None
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            oauth_url = f"{self.oauth_url}?VendorKey={api_key}&ResponseURL={self.callback_url}"
            logger.info(f"Navigating to OAuth URL: {oauth_url}")
            driver.get(oauth_url)
            
            wait = WebDriverWait(driver, 30)
            
            logger.info("Waiting for login form to load...")
            time.sleep(3)
            
            client_code_field = wait.until(
                EC.presence_of_element_located((By.ID, "txtUserID"))
            )
            logger.info("Client code field found")
            client_code_field.clear()
            client_code_field.send_keys(client_code)
            time.sleep(1)
            
            pin_field = driver.find_element(By.ID, "txtPassword")
            logger.info("PIN field found")
            pin_field.clear()
            pin_field.send_keys(pin)
            time.sleep(1)
            
            totp = pyotp.TOTP(totp_secret).now()
            logger.info(f"Generated TOTP: {totp}")
            
            totp_field = driver.find_element(By.ID, "txtDOB")
            logger.info("TOTP field found")
            totp_field.clear()
            totp_field.send_keys(totp)
            time.sleep(1)
            
            login_button = driver.find_element(By.ID, "btnLogin")
            logger.info("Clicking login button...")
            login_button.click()
            
            logger.info("Waiting for redirect to callback URL...")
            wait.until(lambda d: self.callback_url in d.current_url)
            
            current_url = driver.current_url
            logger.info(f"Redirected to: {current_url}")
            
            parsed_url = urlparse(current_url)
            query_params = parse_qs(parsed_url.query)
            
            request_token = query_params.get('RequestToken', [None])[0]
            
            if request_token:
                logger.info("Request token extracted successfully")
                return request_token
            else:
                logger.error("Request token not found in callback URL")
                return None
        
        except TimeoutException as e:
            logger.error(f"Timeout during OAuth login: {str(e)}")
            if driver:
                logger.error(f"Current URL: {driver.current_url}")
                logger.error(f"Page source: {driver.page_source[:500]}")
            return None
        
        except Exception as e:
            logger.error(f"Error during automated OAuth login: {str(e)}", exc_info=True)
            if driver:
                logger.error(f"Current URL: {driver.current_url}")
            return None
        
        finally:
            if driver:
                driver.quit()
    
    async def _exchange_for_access_token(
        self,
        request_token: str,
        api_key: str,
        encryption_key: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Exchange RequestToken for AccessToken using 5paisa API
        
        Returns:
            Dictionary with access_token and client_code if successful
        """
        try:
            payload = {
                "head": {
                    "Key": api_key
                },
                "body": {
                    "RequestToken": request_token,
                    "EncryKey": encryption_key,
                    "UserId": user_id
                }
            }
            
            logger.info(f"Exchanging request token for access token...")
            logger.info(f"Payload: {payload}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.access_token_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
            
            logger.info(f"Access token response status: {response.status_code}")
            logger.info(f"Access token response: {response.text}")
            
            if response.status_code != 200:
                logger.error(f"Failed to get access token: {response.status_code}")
                return None
            
            data = response.json()
            
            if data.get('body', {}).get('Message') == 'Success':
                return {
                    'access_token': data['body']['AccessToken'],
                    'client_code': data['body']['ClientCode']
                }
            else:
                error_msg = data.get('body', {}).get('Message', 'Unknown error')
                logger.error(f"Access token exchange failed: {error_msg}")
                return None
        
        except Exception as e:
            logger.error(f"Error exchanging request token: {str(e)}", exc_info=True)
            return None
