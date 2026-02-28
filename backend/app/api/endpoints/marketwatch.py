# NOT WORKING WEBSOCKET ISSUES 
"""
Marketwatch API endpoints
"""
from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
import asyncio
import logging

from app.api.dependencies import get_database
from app.schemas.marketwatch import MarketwatchResponse
from app.services.marketwatch_service import MarketwatchService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/marketwatch", tags=["marketwatch"])


@router.get("", response_model=MarketwatchResponse)
async def get_marketwatch(
    exchange: Optional[str] = Query(None, description="Filter by exchange (NSE, BSE, etc.)"),
    db: AsyncSession = Depends(get_database)
):
    """
    Get marketwatch instruments (symbol discovery only)
    """
    service = MarketwatchService(db)
    instruments = await service.get_instruments(exchange)

    return MarketwatchResponse(
        instruments=instruments,
        total=len(instruments),
        timestamp=datetime.utcnow().isoformat()
    )


@router.get("/ltp/{symbol}")
async def get_ltp(
    symbol: str,
    exchange: str = Query(..., description="Exchange name (NSE, BSE, etc.)"),
    db: AsyncSession = Depends(get_database)
):
    """
    Get Last Traded Price (LTP) for a symbol
    """
    service = MarketwatchService(db)
    ltp = await service.get_ltp(symbol, exchange)

    if ltp is None:
        return {
            "symbol": symbol,
            "exchange": exchange,
            "ltp": None,
            "error": "LTP not available"
        }

    return {
        "symbol": symbol,
        "exchange": exchange,
        "ltp": ltp
    }


@router.get("/normalize/{symbol}")
async def normalize_symbol(
    symbol: str,
    exchange: str = Query(..., description="Exchange name (NSE, BSE, etc.)"),
    db: AsyncSession = Depends(get_database)
):
    """
    Normalize symbol across brokers
    """
    service = MarketwatchService(db)
    normalized = await service.normalize_symbol(symbol, exchange)

    return {
        "symbol": symbol,
        "exchange": exchange,
        "broker_data": normalized
    }


@router.websocket("/ws")
async def websocket_marketwatch(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_database)
):
    """
    WebSocket endpoint for real-time marketwatch updates
    """
    await websocket.accept()
    logger.info("Marketwatch WebSocket connected")

    service = MarketwatchService(db)

    try:
        while True:
            instruments = await service.get_instruments()

            await websocket.send_json({
                "type": "marketwatch",
                "data": [inst.model_dump() for inst in instruments],
                "timestamp": datetime.utcnow().isoformat()
            })

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        logger.info("Marketwatch WebSocket disconnected")

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()


# """
# Marketwatch API endpoints




#     """
#     Get marketwatch data (instruments with LTP and change)
    
#     Query parameters:
#     - exchange: Optional exchange filter
    
#     Example response:
#     ```json
#     {
#         "instruments": [
#             {
#                 "symbol": "RELIANCE",
#                 "exchange": "NSE",
#                 "instrument_token": "738561",
#                 "last_price": 2500.0,
#                 "change": 25.0,
#                 "change_percent": 1.01,
#                 "volume": 1000000,
#                 "high": 2510.0,
#                 "low": 2480.0,
#                 "open": 2490.0,
#                 "close": 2475.0
#             }
#         ],
#         "total": 1,
#         "timestamp": "2024-01-01T10:00:00Z"
#     }
#     ```
    


#     """
#     Get Last Traded Price for a symbol
    
#     Path parameters:
#     - symbol: Trading symbol
    
#     Query parameters:
#     - exchange: Exchange name
    
    


#     """
#     Normalize symbol across brokers
    
#     Returns broker-specific symbol details for all enabled accounts.
    


#     """
#     WebSocket endpoint for real-time marketwatch updates
    
#     Connects and streams live market data updates.
    
        
            
            
            
