"""
Trades API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from app.api.dependencies import get_database
from app.core.auth import get_current_user 
from app.models.user import User  
from app.schemas.trade import TradeRequest, TradeResponse, TradeListResponse
from app.services.trade_orchestrator import TradeOrchestrator
from app.models.trade import Trade

router = APIRouter(prefix="/trades", tags=["trades"])


@router.post("", response_model=TradeResponse, status_code=status.HTTP_201_CREATED)
async def place_trade(
    trade_request: TradeRequest,
    current_user: User = Depends(get_current_user),  
    db: AsyncSession = Depends(get_database)
):
    """
    Place a trade across all enabled accounts
    
    The trade will be executed simultaneously in all enabled accounts.
    
    Example request:
    ```json
    {
        "symbol": "RELIANCE",
        "exchange": "NSE",
        "side": "BUY",
        "quantity": 10,
        "order_type": "LIMIT",
        "price": 2500.0
    }
    ```
    
    Example response:
    ```json
    {
        "trade_id": 123,
        "symbol": "RELIANCE",
        "exchange": "NSE",
        "side": "BUY",
        "quantity": 10,
        "order_type": "LIMIT",
        "price": 2500.0,
        "created_at": "2024-01-01T10:00:00Z",
        "details": [
            {
                "account_id": 1,
                "broker": "ZERODHA",
                "order_id": "order123",
                "status": "SUCCESS",
                "executed_price": 2500.0,
                "executed_quantity": 10,
                "error_reason": null
            },
            {
                "account_id": 2,
                "broker": "FIVEPAISA",
                "order_id": "order456",
                "status": "SUCCESS",
                "executed_price": 2500.0,
                "executed_quantity": 10,
                "error_reason": null
            }
        ]
    }
    ```
    """
    try:
        orchestrator = TradeOrchestrator(db)
        trade = await orchestrator.execute_trade(trade_request, current_user)  
        
        result = await db.execute(
            select(Trade)
            .options(selectinload(Trade.executions))
            .where(Trade.trade_id == trade.trade_id)
        )
        trade = result.scalar_one()
        
        return trade
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to execute trade: {str(e)}"
        )


@router.get("/{trade_id}", response_model=TradeResponse)
async def get_trade(
    trade_id: int,
    current_user: User = Depends(get_current_user),  
    db: AsyncSession = Depends(get_database)
):
    """
    Get trade details by trade_id
    
    Returns the trade with all execution details for each account.
    """
    result = await db.execute(
        select(Trade)
        .options(selectinload(Trade.executions))
        .where(Trade.trade_id == trade_id)
    )
    trade = result.scalar_one_or_none()
    
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trade {trade_id} not found"
        )
    
    # Validate ownership
    if trade.owner_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trade {trade_id} not found"
        )
    
    return trade


@router.get("", response_model=TradeListResponse)
async def get_trades(
    current_user: User = Depends(get_current_user),  
    limit: int = 100, #limiting trades idk why chat gpt said to do this 
    offset: int = 0,
    db: AsyncSession = Depends(get_database)
):
    """
    Get list of trades
    
    Query parameters:
    - limit: Maximum number of trades to return (default: 100)
    - offset: Number of trades to skip (default: 0)
    """
    
    result = await db.execute(
        select(Trade)
        .options(selectinload(Trade.executions))
        .where(Trade.owner_id == current_user.user_id)  
        .order_by(Trade.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    trades = list(result.scalars().all())
    
    
    count_result = await db.execute(
        select(Trade).where(Trade.owner_id == current_user.user_id)
    )
    total = len(list(count_result.scalars().all()))
    
    return TradeListResponse(
        trades=[TradeResponse.model_validate(trade) for trade in trades],
        total=total
    )
