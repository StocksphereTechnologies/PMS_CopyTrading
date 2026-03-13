"""Account API routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.account import AccountCreate, AccountResponse, AccountUpdate
from app.schemas.margin import AccountMargin, MarginListResponse
from app.schemas.order import OrderListResponse
from app.services.account_service import AccountService
from app.services.margin_service import MarginService
from app.services.order_service import OrderService

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.get("/margins", response_model=MarginListResponse)
async def get_margins(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get margin data for all user's enabled accounts"""
    margins = await MarginService.get_margins_for_user(db, current_user.user_id)
    return {
        "margins": margins,
        "total_accounts": len(margins)
    }

@router.get("/orders", response_model=OrderListResponse)
async def get_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    orders = await OrderService.get_orders_for_user(db, current_user.user_id)
    return {
        "orders": orders,
        "total_orders": len(orders)
    }

@router.get("/{account_id}/zerodha/login-url")
async def get_zerodha_login_url(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get manual authorization URL for Zerodha"""
    account = await AccountService.get_account(db, account_id)
    if not account or account.owner_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    try:
        url = await AccountService.get_zerodha_login_url(db, account_id)
        return {"login_url": url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/zerodha/callback")
async def zerodha_callback(
    request_token: str,
    state: str,
    db: AsyncSession = Depends(get_db)
):
    """Callback for Zerodha official OAuth login"""
    result = await AccountService.handle_zerodha_callback(request_token, state)
    if result.get("success"):
        # Return a simple HTML page that closes itself
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content="""
            <html>
                <body>
                    <h1>Authorization Successful!</h1>
                    <p>You can close this window now.</p>
                    <script>
                        setTimeout(() => window.close(), 2000);
                    </script>
                </body>
            </html>
        """)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Authorization failed")
        )


@router.post("/validate")
async def validate_account(
    account_data: AccountCreate,
    current_user: User = Depends(get_current_user)
):
    """Validate broker credentials without saving"""
    result = await AccountService.validate_account_credentials(account_data)
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Validation failed")
        )
    
    return {
        "valid": True,
        "message": "Credentials validated successfully!",
        "broker": account_data.broker_name
    }


from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks

@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    account_data: AccountCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new trading account"""
    try:
        account = await AccountService.create_account(db, account_data, current_user)
        # Trigger background login validation
        background_tasks.add_task(AccountService.perform_background_login, account.account_id)
        return account
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=List[AccountResponse])
async def get_accounts(
    enabled_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all trading accounts for current user"""
    accounts = await AccountService.get_user_accounts(
        db, 
        user_id=current_user.user_id, 
        enabled_only=enabled_only
    )
    return accounts


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific account by ID (must own it)"""
    account = await AccountService.get_account(db, account_id)
    if not account or account.owner_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with id {account_id} not found"
        )
    return account


@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    account_data: AccountUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an account (must own it)"""
    # Verify ownership
    existing = await AccountService.get_account(db, account_id)
    if not existing or existing.owner_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with id {account_id} not found"
        )
    
    account = await AccountService.update_account(db, account_id, account_data)
    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an account (must own it)"""
    # Verify ownership
    existing = await AccountService.get_account(db, account_id)
    if not existing or existing.owner_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with id {account_id} not found"
        )
    
    success = await AccountService.delete_account(db, account_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with id {account_id} not found"
        )
