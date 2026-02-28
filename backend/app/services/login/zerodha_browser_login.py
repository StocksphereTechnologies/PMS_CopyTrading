import logging
import asyncio
import hashlib
import time
from datetime import datetime
from typing import Dict, Any
from urllib.parse import urlparse, parse_qs

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException, TimeoutException
import pyotp
import requests

from app.models.account import Account
from app.core.encryption import encryption_service

logger = logging.getLogger(__name__)

# selenium automation automating stuff to get access token and request token from zerodha also saving screenshots and logs for debugging
class ZerodhaBrowserLogin:
    """Handles browser-based login for Zerodha using Selenium automation"""
    
    def __init__(self):
        self.base_url = "https://api.kite.trade"
    
    async def login(self, account: Account) -> Dict[str, Any]:
        """
        Perform login using Selenium automation
        
        Args:
            account: Account model with encrypted credentials
            
        Returns:
            Dictionary with success status, access_token, and token_generated_at
        """
        try:
            
            password = encryption_service.decrypt(account.encrypted_password)
            totp_secret = encryption_service.decrypt(account.encrypted_totp_secret)
            
            logger.info(f"Starting automated Zerodha login for account {account.account_id}")
            
            request_token = await asyncio.to_thread(
                self._automated_login,
                account.trading_login_id,
                password,
                totp_secret,
                account.api_key
            )
            
            if not request_token:
                error_msg = "Failed to get request token from Zerodha"
                logger.error(error_msg)
                return {
                    "success": False,
                    "access_token": None,
                    "token_generated_at": None,
                    "error": error_msg
                }
            
            logger.info(f"Request token obtained for account {account.account_id}: {request_token[:20]}...")
            
            
            session_data = await asyncio.to_thread(
                self._generate_session,
                request_token,
                account.api_key,
                account.api_secret
            )
            
            if not session_data or 'access_token' not in session_data:
                error_msg = "Failed to generate access token"
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
                "access_token": session_data['access_token'],
                "token_generated_at": datetime.utcnow(),
                "error": None
            }
        
        except Exception as e:
            error_msg = f"Zerodha login failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "access_token": None,
                "token_generated_at": None,
                "error": error_msg
            }
    
    def _automated_login(self, user_id: str, password: str, totp_secret: str, api_key: str) -> str:
        """
        Perform automated login using Selenium
        
        Returns:
            request_token if successful, None otherwise
        """
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        driver = None
        captured_url = None
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(f"https://kite.zerodha.com/connect/login?api_key={api_key}&v=3")
            
            logger.info("Browser launched, loading login page...")
            
            wait = WebDriverWait(driver, 20)
            
            
            user_id_field = wait.until(
                EC.presence_of_element_located((By.ID, "userid"))
            )
            user_id_field.clear()
            user_id_field.send_keys(user_id)
            logger.debug(f"User ID entered: {user_id}")
            
            
            password_field = wait.until(
                EC.presence_of_element_located((By.ID, "password"))
            )
            password_field.clear()
            password_field.send_keys(password)
            logger.debug("Password entered")
            
            
            login_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )
            login_button.click()
            logger.debug("Login button clicked")
            
            
            logger.debug("Waiting for TOTP page...")
            
            
            time.sleep(3)
            
            
            try:
                page_source = driver.page_source
                with open("totp_page_source.html", "w", encoding="utf-8") as f:
                    f.write(page_source)
                logger.info("Page source saved to totp_page_source.html")
                
                # Find all input elements
                inputs = driver.find_elements(By.TAG_NAME, "input")
                logger.info(f"Found {len(inputs)} input elements on page")
                for idx, inp in enumerate(inputs):
                    try:
                        logger.info(f"Input {idx}: type={inp.get_attribute('type')}, "
                                  f"id={inp.get_attribute('id')}, "
                                  f"class={inp.get_attribute('class')}, "
                                  f"placeholder={inp.get_attribute('placeholder')}")
                    except:
                        pass
            except Exception as e:
                logger.error(f"Error logging page source: {e}")
            
            
            try:
                driver.save_screenshot("totp_page.png")
                logger.debug("Screenshot saved: totp_page.png")
            except:
                pass
            
            totp_field = None
            totp_selectors = [
                (By.ID, "totp"),
                (By.XPATH, "//input[@type='tel']"),
                (By.XPATH, "//input[@type='text']"),
                (By.XPATH, "//input[@placeholder]"),
                (By.XPATH, "//input[contains(@placeholder, 'TOTP')]"),
                (By.XPATH, "//input[contains(@placeholder, 'code')]"),
                (By.XPATH, "//input[contains(@class, 'totp')]"),
                (By.XPATH, "//input[contains(@class, 'otp')]"),
                (By.CSS_SELECTOR, "input[inputmode='numeric']"),
                (By.CSS_SELECTOR, "input[autocomplete='one-time-code']"),
                (By.CSS_SELECTOR, "input[type='tel']"),
                (By.CSS_SELECTOR, "input[type='text']"),
                (By.XPATH, "//form//input"),  
            ]
            
            
            for selector_type, selector_value in totp_selectors:
                try:
                    
                    wait_totp = WebDriverWait(driver, 10)
                    totp_field = wait_totp.until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    logger.debug(f"TOTP field found using: {selector_type}={selector_value}")
                    break
                except Exception as e:
                    logger.debug(f"Selector {selector_type}={selector_value} failed: {e}")
                    continue
            
            if not totp_field:
                
                try:
                    driver.save_screenshot("totp_not_found.png")
                    logger.error("Screenshot saved: totp_not_found.png")
                    logger.error(f"Current URL: {driver.current_url}")
                    logger.error(f"Page title: {driver.title}")
                except:
                    pass
                raise Exception("Could not find TOTP input field with any known selector")
            
            
            totp_code = pyotp.TOTP(totp_secret).now()
            logger.debug(f"TOTP generated: {totp_code}")
            
            totp_field.clear()
            time.sleep(0.5)
            totp_field.send_keys(totp_code)
            time.sleep(0.5)
            logger.debug("TOTP entered")
            
            
            continue_button = None
            button_selectors = [
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//button[contains(text(), 'Continue')]"),
                (By.CSS_SELECTOR, "button[type='submit']")
            ]
            
            for selector_type, selector_value in button_selectors:
                try:
                    continue_button = wait.until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    logger.debug("Continue button found")
                    break
                except:
                    continue
            
            
            logger.debug("Submitting TOTP...")
            try:
                if continue_button:
                    continue_button.click()
                    logger.debug("Continue button clicked")
                else:
                    totp_field.send_keys(Keys.RETURN)
                    logger.debug("Submitted via Enter key")
            except Exception as click_error:
                logger.debug(f"Click error (may be normal): {click_error}")
            
            
            logger.debug("Waiting for redirect...")
            max_attempts = 10
            for attempt in range(max_attempts):
                try:
                    time.sleep(0.5)  
                    current_url = driver.current_url
                    
                    if 'request_token' in current_url or 'status=success' in current_url:
                        captured_url = current_url
                        logger.info(f"URL captured: {captured_url[:80]}...")
                        break
                except WebDriverException as e:
                    
                    if captured_url:
                        logger.debug(f"Browser closed but URL was captured: {e}")
                        break
                    logger.debug(f"Attempt {attempt + 1}/{max_attempts}: {e}")
                except Exception as e:
                    logger.debug(f"Error getting URL (attempt {attempt + 1}): {e}")
            
            
            if not captured_url:
                try:
                    captured_url = driver.current_url
                    logger.info(f"Final URL capture: {captured_url[:80]}...")
                except:
                    logger.error("Could not capture URL - browser closed too quickly")
            
        except Exception as e:
            logger.error(f"Error during automated login: {str(e)}", exc_info=True)
            
            
            if driver and not captured_url:
                try:
                    captured_url = driver.current_url
                    logger.info(f"URL captured on error: {captured_url[:80]}...")
                except:
                    pass
            
            
            if driver:
                try:
                    driver.save_screenshot("zerodha_error.png")
                    logger.info("Screenshot saved as 'zerodha_error.png'")
                except:
                    pass
        
        finally:
            
            if driver:
                try:
                    driver.quit()
                    logger.debug("Browser closed")
                except:
                    pass
        
        
        if captured_url:
            try:
                parsed_url = urlparse(captured_url)
                params = parse_qs(parsed_url.query)
                
                if 'request_token' in params:
                    request_token = params['request_token'][0]
                    logger.info(f"Request token extracted: {request_token[:20]}...")
                    return request_token
                else:
                    logger.error(f"No request_token in URL: {captured_url}")
            except Exception as e:
                logger.error(f"Error parsing URL: {e}")
        else:
            logger.error("No URL was captured")
        
        return None
    
    def _generate_session(self, request_token: str, api_key: str, api_secret: str) -> Dict[str, Any]:
        """
        Generate access token using request token
        
        Args:
            request_token: Request token from login
            api_key: Zerodha API key
            api_secret: Zerodha API secret
            
        Returns:
            Session data with access_token
        """
        logger.info(f"Generating access token from request_token: {request_token[:20]}...")
        
        # generate checksum/access token using api_key, request_token and api_secret
        checksum = hashlib.sha256(
            f"{api_key}{request_token}{api_secret}".encode()
        ).hexdigest()
        
        logger.debug(f"Checksum generated: {checksum[:20]}...")
        
        
        url = f"{self.base_url}/session/token"
        data = {
            'api_key': api_key,
            'request_token': request_token,
            'checksum': checksum
        }
        
        logger.debug(f"Calling Zerodha API: {url}")
        response = requests.post(url, data=data)
        result = response.json()
        
        logger.debug(f"API Response status: {response.status_code}")
        logger.debug(f"API Response: {result}")
        
        if response.status_code == 200 and 'data' in result:
            logger.info(" Access token generation successful!")
            logger.info(f"Access token: {result['data'].get('access_token', '')[:30]}...")
            return result['data']
        else:
            logger.error(f" Access token generation failed!")
            logger.error(f"Status: {response.status_code}")
            logger.error(f"Response: {result}")
            return None