"""Position API routes"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.position import Position, PositionListResponse
from app.services.position_service import PositionService

router = APIRouter(prefix="/positions", tags=["positions"])

@router.get("", response_model=PositionListResponse)
async def get_positions(
    open_only: bool = Query(True, description="If true, return only positions with net quantity != 0"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get consolidated positions for all user's enabled accounts.
    
    By default, only returns active/open positions (quantity != 0).
    Set open_only=false to see all data including closed trades.
    """
    positions = await PositionService.get_positions_for_user(
        db, 
        current_user.user_id, 
        open_only=open_only
    )
    
    return PositionListResponse(
        positions=positions,
        total_positions=len(positions),
        active_positions=len([p for p in positions if p.netqty != 0])
    )
