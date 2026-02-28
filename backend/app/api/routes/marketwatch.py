"""Marketwatch API routes"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.config import settings
from app.schemas.marketwatch import MarketwatchResponse
from app.services.marketwatch_service import MarketwatchService

router = APIRouter(prefix="/marketwatch", tags=["marketwatch"])


@router.get("", response_model=MarketwatchResponse)
async def get_marketwatch(
    symbols: Optional[List[str]] = Query(None, description="List of symbols to fetch"),
    exchange: Optional[str] = Query(None, description="Exchange filter (NSE, BSE, MCX)"),
    db: Session = Depends(get_db)
):
    """
    Get marketwatch data
    
    - If symbols provided: fetch LTP for those symbols
    - If no symbols: fetch all available instruments
    """
    service = MarketwatchService(db)
    items = await service.get_instruments(exchange=exchange)
    
    return MarketwatchResponse(
        instruments=items,
        total=len(items),
        timestamp=str(__import__('datetime').datetime.now())
    )


