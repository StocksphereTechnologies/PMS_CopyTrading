"""
Account service for managing trading accounts with automated login
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from sqlalchemy import select
from typing import List, Optional, Dict, Any
from app.models.account import Account, BrokerName
from app.schemas.account import AccountCreate, AccountUpdate
from app.core.encryption import encryption_service
from app.services.login.zerodha_login_service import ZerodhaLoginService
from app.services.login.fivepaisa_login_service import FivePaisaLoginService
import logging
import asyncio

logger = logging.getLogger(__name__)


class AccountService:
    """Service for account management with automated login"""
    
    @staticmethod
    def _clean_token(token: Any) -> Optional[str]:
        """
        Defensively clean access token.
        it handles (for 5paisa JWTs mostly):
        Bytes object -> decode to str
        String starting with b' or b" -> strip the b and quotes
        String wrapped in quotes -> strip quotes
        None or empty -> return None
        """
        if not token:
            return None
            
        def deep_clean(t):
            if not t:
                return t
            if isinstance(t, bytes):
                try:
                    return deep_clean(t.decode('utf-8'))
                except:
                    return str(t)
            if isinstance(t, str):
                t = t.strip()
                # Strip wrapping quotes if they exist (sometimes tokens are saved with extra quotes)
                if len(t) >= 2 and ((t[0] == "'" and t[-1] == "'") or (t[0] == '"' and t[-1] == '"')):
                    return deep_clean(t[1:-1])
                # Handle literal string representation of bytestring: b'token' or b"token"
                if len(t) > 3 and t.startswith("b") and t[1] in ("'", '"') and t.endswith(t[1]):
                    return deep_clean(t[2:-1])
                return t
            return str(t)

        return deep_clean(token)
    
    @staticmethod
    async def perform_background_login(account_id: int):
        """
        Background task to perform login for a specific account.
        Creates its own database session to avoid scope issues.
        """
        async with AsyncSessionLocal() as db:
            account = await AccountService.get_account(db, account_id)
            if account:
                logger.info(f"Starting background login for account {account_id}")
                await AccountService._auto_login_account(db, account)
            else:
                logger.error(f"Background login failed: Account {account_id} not found")

    @staticmethod
    async def create_account(db: AsyncSession, account_data: AccountCreate, current_user) -> Account:
        """
        Create a new trading account with encrypted credentials
        
        Args:
            db: Database session
            account_data: Account creation data
            current_user: Current authenticated user
            
        Returns:
            Created account
            
        Raises:
            ValueError: If account with same trading_login_id already exists for this user+broker
        """
        # Duplicate check: prevent re-adding the same trading account
        existing = await db.execute(
            select(Account).where(
                Account.owner_id == current_user.user_id,
                Account.trading_login_id == account_data.trading_login_id,
                Account.broker_name == account_data.broker_name.value
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(
                f"Account with trading ID '{account_data.trading_login_id}' "
                f"for broker '{account_data.broker_name.value}' already exists"
            )
        
        if account_data.broker_name == BrokerName.ZERODHA:
            encrypted_password = encryption_service.encrypt(account_data.trading_password)
            encrypted_totp = encryption_service.encrypt(account_data.totp_secret_key)
            encrypted_login_password = None
            user_id = None
        elif account_data.broker_name == BrokerName.FIVEPAISA:
            encrypted_password = encryption_service.encrypt(account_data.mpin)  # MPIN
            encrypted_totp = encryption_service.encrypt(account_data.totp_secret_key)
            #  Encrypt login_password (different from MPIN)
            encrypted_login_password = encryption_service.encrypt(account_data.login_password) if account_data.login_password else None
            user_id = account_data.user_id  # USER_ID (different from client_code)
        else:
            raise ValueError(f"Unsupported broker: {account_data.broker_name}")
        
        account = Account(
            broker_name=account_data.broker_name.value,
            owner_id=current_user.user_id,  #owner_id 
            nickname=account_data.nickname,
            trading_login_id=account_data.trading_login_id,
            encrypted_password=encrypted_password,
            encrypted_totp_secret=encrypted_totp,
            #  5paisa-specific fields
            user_id=user_id,
            encrypted_login_password=encrypted_login_password,
            # API credentials
            api_key=account_data.api_key,
            api_secret=account_data.api_secret,
            user_key=account_data.user_key if account_data.broker_name == BrokerName.FIVEPAISA else None,
            app_source=account_data.app_source if account_data.broker_name == BrokerName.FIVEPAISA else None,
            is_enabled=account_data.is_enabled
        )
        
        # SAVE TO DATABASE DIRECTLY
        # We skip mandatory internal validation here because:
        # The frontend already validates before enabling the Save button.
        # TOTP codes are one-time use re-validating here often fails with "OTP used" (doesnt make any sense tbh)
        # The background worker will pick this up and perform the first real login soon.
        
        db.add(account)
        await db.commit()
        await db.refresh(account)
        
        logger.info(f"Created account {account.account_id} for broker {account.broker_name} (pending background validation)")
        return account
    
    @staticmethod
    async def _validate_credentials(account: Account) -> dict:
        """
        Validate account credentials by attempting login
        
        Args:
            account: Account with credentials to validate
            
        Returns:
            Dict with success status and access_token if successful
        """
        try:
            if account.broker_name == BrokerName.ZERODHA.value:
                login_service = ZerodhaLoginService()
            elif account.broker_name == BrokerName.FIVEPAISA.value:
                login_service = FivePaisaLoginService()
            else:
                return {"success": False, "error": f"Unsupported broker: {account.broker_name}"}
            
            result = await login_service.login(account)
            return result
        except Exception as e:
            logger.error(f"Credential validation exception: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def validate_account_credentials(account_data: AccountCreate) -> dict:
        """
        Validate account credentials without saving to database
        
        This is a public method that can be called from the API endpoint
        to test credentials before saving.
        
        Args:
            account_data: Account creation data with credentials
            
        Returns:
            Dict with success status and error message if failed
        """
        from app.core.encryption import encryption_service
        
        
        if account_data.broker_name == BrokerName.ZERODHA:
            encrypted_password = encryption_service.encrypt(account_data.trading_password)
            encrypted_totp = encryption_service.encrypt(account_data.totp_secret_key)
            encrypted_login_password = None
            user_id = None
        elif account_data.broker_name == BrokerName.FIVEPAISA:
            encrypted_password = encryption_service.encrypt(account_data.mpin)
            encrypted_totp = encryption_service.encrypt(account_data.totp_secret_key)
            encrypted_login_password = encryption_service.encrypt(account_data.login_password) if account_data.login_password else None
            user_id = account_data.user_id
        else:
            return {"success": False, "error": f"Unsupported broker: {account_data.broker_name}"}
        
        # Create temporary{NOT to save to DB}
        temp_account = Account(
            broker_name=account_data.broker_name.value,
            nickname=account_data.nickname or "Temp",
            trading_login_id=account_data.trading_login_id,
            encrypted_password=encrypted_password,
            encrypted_totp_secret=encrypted_totp,
            user_id=user_id,
            encrypted_login_password=encrypted_login_password,
            api_key=account_data.api_key,
            api_secret=account_data.api_secret,
            user_key=account_data.user_key if account_data.broker_name == BrokerName.FIVEPAISA else None,
            app_source=account_data.app_source if account_data.broker_name == BrokerName.FIVEPAISA else None,
            is_enabled=True
        )
        
        
        return await AccountService._validate_credentials(temp_account)
    
    @staticmethod
    async def initialize_all_sessions() -> None:
        """
        Proactive startup task to initialize sessions for all enabled accounts.
        Ensures that tokens are valid and ready before user requests data.
        Uses parallel processing for scalability.
        """
        try:
            from app.core.database import AsyncSessionLocal
            
            async with AsyncSessionLocal() as db:
                # Fetch all enabled accounts
                result = await db.execute(
                    select(Account).where(Account.is_enabled == True)
                )
                accounts = result.scalars().all()
                
                if not accounts:
                    logger.info("No enabled accounts to initialize.")
                    return
                
                logger.info(f"Initializing {len(accounts)} enabled accounts in parallel.")
                
                # worker for parallel execution
                async def initialize_single_account(account_id: int):
                    # Create a new session per task to avoid concurrency issues with a single session object
                    async with AsyncSessionLocal() as session:
                        try:
                            result = await session.execute(select(Account).where(Account.account_id == account_id))
                            db_account = result.scalar_one_or_none()
                            
                            if not db_account:
                                return
                            
                            logger.info(f"Initializing account {account_id} ({db_account.broker_name})")
                            
                            # validating the token
                            if db_account.broker_name == BrokerName.ZERODHA.value:
                                service = ZerodhaLoginService()
                                await service.ensure_valid_token(db_account)
                            elif db_account.broker_name == BrokerName.FIVEPAISA.value:
                                service = FivePaisaLoginService()
                                await service.ensure_valid_token(db_account)
                            
                            
                            original_token = db_account.access_token
                            cleaned_token = AccountService._clean_token(original_token)
                            
                            if cleaned_token != original_token:
                                db_account.access_token = cleaned_token
                            
                            session.add(db_account)
                            await session.commit()
                            logger.info(f"Account {account_id} initialized successfully.")
                            
                        except Exception as e:
                            logger.error(f"Failed to initialize account {account_id}: {str(e)}")
                            await session.rollback()

                # Run all in parallel with a semaphore to avoid overwhelming APIs
                sem = asyncio.Semaphore(10)
                async def sem_worker(acc_id):
                    async with sem:
                        await initialize_single_account(acc_id)

                await asyncio.gather(*(sem_worker(acc.account_id) for acc in accounts))
                logger.info("Session initialization cycle complete.")
                
        except Exception as e:
            logger.error(f"Error in initialize_all_sessions: {e}", exc_info=True)

    @staticmethod
    async def _auto_login_account(db: AsyncSession, account: Account) -> bool:
        """
        Perform automated login for an account
        
        Args:
            db: Database session
            account: Account to login
            
        Returns:
            True if login successful
        """
        try:
            if account.broker_name == BrokerName.ZERODHA.value:
                login_service = ZerodhaLoginService()
            elif account.broker_name == BrokerName.FIVEPAISA.value:
                login_service = FivePaisaLoginService()
            else:
                logger.error(f"Unsupported broker for auto-login: {account.broker_name}")
                return False
            
            logger.info(f"Attempting auto-login for account {account.account_id} ({account.broker_name})")
            result = await login_service.login(account)
            
            if result.get("success") and result.get("access_token"):
                
                account.access_token = AccountService._clean_token(result["access_token"])
                account.token_generated_at = result.get("token_generated_at")
                account.is_validated = True
                db.add(account)
                await db.commit()
                logger.info(
                    f"Auto-login successful for account {account.account_id} "
                    f"(token generated at: {account.token_generated_at})"
                )
                return True
            else:
                error_msg = result.get('error', 'Unknown error')
                logger.error(
                    f"Auto-login failed for account {account.account_id} ({account.broker_name}): {error_msg}"
                )
                return False
        except Exception as e:
            logger.error(
                f"Auto-login exception for account {account.account_id} ({account.broker_name}): {e}",
                exc_info=True
            )
            return False
    
    @staticmethod
    async def get_account(db: AsyncSession, account_id: int) -> Optional[Account]:
        """
        Get account by ID
        
        Args:
            db: Database session
            account_id: Account ID
            
        Returns:
            Account or None
        """
        result = await db.execute(select(Account).where(Account.account_id == account_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all_accounts(db: AsyncSession, enabled_only: bool = False) -> List[Account]:
        """
        Get all accounts
        
        Args:
            db: Database session
            enabled_only: If True, return only enabled accounts
            
        Returns:
            List of accounts
        """
        query = select(Account)
        if enabled_only:
            query = query.where(Account.is_enabled == True)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_user_accounts(db: AsyncSession, user_id: int, enabled_only: bool = False) -> List[Account]:
        """
        Get all accounts for a specific user
        
        Args:
            db: Database session
            user_id: User ID to filter by
            enabled_only: If True, return only enabled accounts
            
        Returns:
            List of accounts owned by the user
        """
        query = select(Account).where(Account.owner_id == user_id)
        if enabled_only:
            query = query.where(Account.is_enabled == True)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_account(
        db: AsyncSession,
        account_id: int,
        account_data: AccountUpdate
    ) -> Optional[Account]:
        """
        Update an account
        
        Args:
            db: Database session
            account_id: Account ID
            account_data: Update data
            
        Returns:
            Updated account or None
        """
        account = await AccountService.get_account(db, account_id)
        if not account:
            return None
        
        # Update fields
        if account_data.trading_login_id is not None:
            account.trading_login_id = account_data.trading_login_id
        if account_data.trading_password is not None:
            account.encrypted_password = encryption_service.encrypt(account_data.trading_password)
        if account_data.mpin is not None:
            account.encrypted_password = encryption_service.encrypt(account_data.mpin)
        if account_data.totp_secret_key is not None:
            account.encrypted_totp_secret = encryption_service.encrypt(account_data.totp_secret_key)
        if account_data.api_key is not None:
            account.api_key = account_data.api_key
        if account_data.api_secret is not None:
            account.api_secret = account_data.api_secret
        if account_data.user_key is not None:
            account.user_key = account_data.user_key
        if account_data.app_source is not None:
            account.app_source = account_data.app_source
        if account_data.nickname is not None:
            account.nickname = account_data.nickname
        if account_data.is_enabled is not None:
            account.is_enabled = account_data.is_enabled
        
        await db.commit()
        await db.refresh(account)
        
        # iif credentials changed and account is enabled, check them by relogin bruh
        if account.is_enabled and (
            account_data.trading_password or account_data.mpin or 
            account_data.totp_secret_key
        ):
            await AccountService._auto_login_account(db, account)
        
        logger.info(f"Updated account {account_id}")
        return account
    
    @staticmethod
    async def validate_and_login_all_enabled(db: AsyncSession) -> Dict[int, bool]:
        """
        Validate and auto-login all enabled accounts (called on startup)
        Only logs in if token is missing or expired
        
        Args:
            db: Database session
            
        Returns:
            Dictionary mapping account_id to login success status
        """
        accounts = await AccountService.get_all_accounts(db, enabled_only=True)
        results = {}
        
        for account in accounts:
            
            needs_login = False
            
            if account.broker_name == BrokerName.ZERODHA.value:
                login_service = ZerodhaLoginService()
                
                is_valid = await login_service.is_token_valid(account)
                if is_valid:
                    logger.info(
                        f"Account {account.account_id} ({account.broker_name}): "
                        f"Valid token found, skipping login"
                    )
                    results[account.account_id] = True
                    continue
                else:
                    logger.info(
                        f"Account {account.account_id} ({account.broker_name}): "
                        f"Token invalid or expired, performing login"
                    )
                    needs_login = True
            elif account.broker_name == BrokerName.FIVEPAISA.value:
                
                if account.access_token and account.token_generated_at:
                    logger.info(
                        f"Account {account.account_id} ({account.broker_name}): "
                        f"Token found, skipping login"
                    )
                    results[account.account_id] = True
                    continue
                else:
                    needs_login = True
            else:
                logger.warning(f"Unknown broker for account {account.account_id}: {account.broker_name}")
                results[account.account_id] = False
                continue
            
            
            if needs_login:
                success = await AccountService._auto_login_account(db, account)
                results[account.account_id] = success
        
        logger.info(f"Validated {len(accounts)} accounts, {sum(results.values())} successful")
        return results
    
    @staticmethod
    async def delete_account(db: AsyncSession, account_id: int) -> bool:
        """
        Delete an account
        
        Args:
            db: Database session
            account_id: Account ID
            
        Returns:
            True if deleted, False if not found
        """
        account = await AccountService.get_account(db, account_id)
        if not account:
            return False
        
        await db.delete(account)
        await db.commit()
        
        logger.info(f"Deleted account {account_id}")
        return True

    @staticmethod
    async def get_zerodha_login_url(db: AsyncSession, account_id: int) -> str:
        """Get official login URL for Zerodha account"""
        account = await AccountService.get_account(db, account_id)
        if not account or account.broker_name != BrokerName.ZERODHA.value:
            raise ValueError("Invalid account for Zerodha login")
        service = ZerodhaLoginService()
        return service.get_login_url(account)

    # this is the callback function for zerodha login (will work on it when i have to implement orders and market data(marketwatch))
    @staticmethod
    async def handle_zerodha_callback(request_token: str, account_id: str) -> Dict[str, Any]:
        """Handle Kite callback and generate access token"""
        service = ZerodhaLoginService()
        return await service.handle_callback(request_token, account_id)
