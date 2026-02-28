"""
Zerodha authentication endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime
from app.api.dependencies import get_database
from app.services.account_service import AccountService
from app.models.account import BrokerName
from kiteconnect import KiteConnect
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/zerodha", tags=["zerodha"])


class RequestTokenRequest(BaseModel):
    """Request token schema"""
    request_token: str


@router.post("/accounts/{account_id}/request-token")
async def save_zerodha_access_token(
    account_id: int,
    request: RequestTokenRequest,
    db: AsyncSession = Depends(get_database),
):
    """
    Manually set Zerodha access_token by providing request_token
    
    Use this if automated browser login doesn't work.
    
    Steps:
    1. Open: https://kite.trade/connect/login?api_key=YOUR_API_KEY&v=3
    2. Login with your credentials
    3. Copy request_token from redirect URL
    4. Call this endpoint with the request_token
    """
    account = await AccountService.get_account(db, account_id)
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account.broker_name != BrokerName.ZERODHA.value:
        raise HTTPException(status_code=400, detail="Account is not a Zerodha account")
    
    if not account.api_key or not account.api_secret:
        raise HTTPException(
            status_code=400,
            detail="API key or secret not configured for this account"
        )
    
    try:
        kite = KiteConnect(api_key=account.api_key)
        
        import asyncio
        loop = asyncio.get_event_loop()
        session_data = await loop.run_in_executor(
            None,
            lambda: kite.generate_session(request.request_token, api_secret=account.api_secret)
        )
        
        access_token = session_data.get("access_token")
        
        if not access_token:
            raise HTTPException(
                status_code=400,
                detail="Failed to generate access_token from request_token"
            )
        
        
        account.access_token = access_token
        account.token_generated_at = datetime.now()
        
        db.add(account)
        await db.commit()
        await db.refresh(account)
        
        logger.info(f" Successfully saved access_token for Zerodha account {account_id}")
        
        return {
            "success": True,
            "message": "Access token saved successfully",
            "token_generated_at": account.token_generated_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating access_token: {e}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to generate access_token: {str(e)}"
        )
