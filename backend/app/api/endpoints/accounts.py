"""
Accounts API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.api.dependencies import get_database
from app.core.auth import get_current_user  
from app.models.user import User  
from app.schemas.account import AccountCreate, AccountUpdate, AccountResponse, AccountListResponse
from app.services.account_service import AccountService
from app.models.account import Account

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/validate", status_code=status.HTTP_200_OK)
async def validate_account_credentials(
    account_data: AccountCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Validate account credentials without saving to database
    
    This endpoint allows users to test their broker credentials before
    committing them to the database. Useful for frontend "Validate" buttons.
    
    Returns:
        {
            "valid": true/false,
            "message": "Success message or error details",
            "broker": "ZERODHA" or "FIVEPAISA"
        }
    """
    try:
        
        validation_result = await AccountService.validate_account_credentials(account_data)
        
        if validation_result["success"]:
            return {
                "valid": True,
                "message": "Credentials validated successfully! You can now save this account.",
                "broker": account_data.broker_name.value
            }
        else:
            return {
                "valid": False,
                "message": f"Validation failed: {validation_result.get('error', 'Unknown error')}",
                "broker": account_data.broker_name.value
            }
    except Exception as e:
        return {
            "valid": False,
            "message": f"Validation error: {str(e)}",
            "broker": account_data.broker_name.value
        }


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    account_data: AccountCreate,
    current_user: User = Depends(get_current_user),  
    db: AsyncSession = Depends(get_database)
):
    """
    Create a new trading account with automated login
    
    Example request for Zerodha:
    ```json
    {
        "broker_name": "ZERODHA",
        "trading_login_id": "AB1234",
        "trading_password": "your_password",
        "totp_secret_key": "JBSWY3DPEHPK3PXP",
        "api_key": "your_kite_api_key",
        "api_secret": "your_kite_api_secret",
        "nickname": "My Zerodha Account",
        "is_enabled": true
    }
    ```
    
    Example request for 5paisa:
    ```json
    {
        "broker_name": "FIVEPAISA",
        "trading_login_id": "12345678",
        "mpin": "123456",
        "totp_secret_key": "JBSWY3DPEHPK3PXP",
        "user_key": "your_user_key",
        "app_source": "10074",
        "api_key": "your_app_name",
        "api_secret": "your_encryption_key",
        "nickname": "My 5paisa Account",
        "is_enabled": true
    }
    ```
    """
    try:
        if account_data.broker_name.value == "ZERODHA":
            if not account_data.trading_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="trading_password is required for Zerodha"
                )
            if not account_data.api_key or not account_data.api_secret:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="api_key and api_secret are required for Zerodha"
                )
        elif account_data.broker_name.value == "FIVEPAISA":
            if not account_data.mpin:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="mpin is required for 5paisa"
                )
            if not account_data.user_key or not account_data.app_source:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="user_key and app_source are required for 5paisa"
                )
        
        account = await AccountService.create_account(db, account_data, current_user)  
        return account
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create account: {str(e)}"
        )



@router.get("", response_model=AccountListResponse)
async def get_accounts(
    current_user: User = Depends(get_current_user),  
    enabled_only: bool = False,
    db: AsyncSession = Depends(get_database)
):
    """
    Get all trading accounts for the current user
    
    Query parameters:
    - enabled_only: If true, return only enabled accounts
    """
    
    accounts = await AccountService.get_user_accounts(db, current_user.user_id, enabled_only=enabled_only)
    return AccountListResponse(
        accounts=[AccountResponse.model_validate(acc) for acc in accounts],
        total=len(accounts)
    )



@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    current_user: User = Depends(get_current_user),  
    db: AsyncSession = Depends(get_database)
):
    """
    Get account by ID (only if owned by current user)
    """
    account = await AccountService.get_account(db, account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account {account_id} not found"
        )
    
    #  Validate ownership
    if account.owner_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,  
            detail=f"Account {account_id} not found"
        )
    
    return account



@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    account_data: AccountUpdate,
    current_user: User = Depends(get_current_user),  
    db: AsyncSession = Depends(get_database)
):
    """
    Update an account (only if owned by current user)
    
    Example request:
    ```json
    {
        "is_enabled": false,
        "access_token": "new_access_token"
    }
    ```
    """
    
    existing_account = await AccountService.get_account(db, account_id)
    if not existing_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account {account_id} not found"
        )
    
    if existing_account.owner_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account {account_id} not found"
        )
    
    account = await AccountService.update_account(db, account_id, account_data)
    return account



@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: int,
    current_user: User = Depends(get_current_user),  
    db: AsyncSession = Depends(get_database)
):
    """
    Delete an account (only if owned by current user)
    """
    
    existing_account = await AccountService.get_account(db, account_id)
    if not existing_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account {account_id} not found"
        )
    
    if existing_account.owner_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account {account_id} not found"
        )
    
    deleted = await AccountService.delete_account(db, account_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account {account_id} not found"
        )
