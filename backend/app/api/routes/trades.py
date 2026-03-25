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
    Place a trade across multiple accounts
    """
    try:
        orchestrator = TradeOrchestrator(db)
        trade = await orchestrator.execute_trade(trade_request, current_user)  
        
        # Load executions for response
        result = await db.execute(
            select(Trade)
            .options(selectinload(Trade.executions))
            .where(Trade.trade_id == trade.trade_id)
        )
        trade = result.scalar_one()
        
        return trade
    except Exception as e:
        import traceback
        traceback.print_exc()
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
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_database)
):
    """
    Get list of trades
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
    
    # Count total for pagination
    from sqlalchemy import func
    count_result = await db.execute(
        select(func.count(Trade.trade_id)).where(Trade.owner_id == current_user.user_id)
    )
    total = count_result.scalar() or 0
    
    return TradeListResponse(
        trades=trades,
        total=total
    )