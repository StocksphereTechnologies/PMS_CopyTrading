"""
ULTIMATE FIX: Marketwatch API endpoints (Using AsyncSessionLocal)
"""
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from typing import Optional, List
from datetime import datetime
import asyncio
import logging

# Import the service and database session maker directly
from app.services.marketwatch_service import MarketwatchService
from app.core.database import AsyncSessionLocal
from app.schemas.marketwatch import MarketwatchResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/marketwatch",
    tags=["marketwatch"]
)

@router.get("/search", response_model=MarketwatchResponse)
async def search_symbols(
    q: str = Query(..., description="E.g. NIFTY26400"),
    exchange: Optional[str] = Query(None, description="NSE, BSE, or NFO"),
):
    """
    Search symbols. Uses internal session to avoid 'Depends' issues.
    """
    async with AsyncSessionLocal() as db:
        service = MarketwatchService(db)
        instruments = await service.search_symbols(q, exchange)
        return MarketwatchResponse(
            instruments=instruments,
            total=len(instruments),
            timestamp=datetime.utcnow().isoformat()
        )

@router.post("/ltp")
async def fetch_ltp(body: dict):
    """
    Fetch live LTP for watchlist instruments.
    Body: {"instruments": [{"scrip_code": 1594, "exchange": "NSE", "symbol": "RELIANCE"}, ...]}
    """
    async with AsyncSessionLocal() as db:
        service = MarketwatchService(db)
        results = await service.fetch_ltp_for_watchlist(body.get("instruments", []))
        return {"data": results, "timestamp": datetime.utcnow().isoformat()}

@router.websocket("/ws")
async def websocket_marketwatch(websocket: WebSocket):
    """
    CRITICAL FIX: NO DEPENDENCIES (Depends) in this function.
    This prevents the 403 Forbidden error caused by missing Auth headers.
    """
    await websocket.accept()
    logger.info("WebSocket: Connection Accepted")
    
    # Create the DB session manually inside the task
    async with AsyncSessionLocal() as db:
        service = MarketwatchService(db)
        subscribed_symbols = set()

        async def ticker_loop():
            try:
                while True:
                    if subscribed_symbols:
                        instruments = await service.get_instruments(
                            symbols=list(subscribed_symbols)
                        )
                        if instruments:
                            await websocket.send_json({
                                "type": "tick",
                                "data": [inst.model_dump() for inst in instruments],
                                "timestamp": datetime.utcnow().isoformat()
                            })
                    await asyncio.sleep(1)
            except Exception as e:
                logger.debug(f"Ticker loop stopped: {e}")

        ticker_task = asyncio.create_task(ticker_loop())

        try:
            while True:
                data = await websocket.receive_json()
                action = data.get("action")
                symbols = data.get("symbols", [])

                if action == "subscribe":
                    subscribed_symbols.update(symbols)
                elif action == "unsubscribe":
                    for s in symbols:
                        subscribed_symbols.discard(s)

        except WebSocketDisconnect:
            logger.info("WebSocket: Disconnected")
        except Exception as e:
            logger.error(f"WebSocket: Communication error: {e}")
        finally:
            ticker_task.cancel()
            try:
                await websocket.close()
            except:
                pass

# """Marketwatch API routes"""
# from fastapi import APIRouter, Depends, Query
# from sqlalchemy.orm import Session
# from typing import Optional, List
# from app.core.config import settings
# from app.schemas.marketwatch import MarketwatchResponse
# from app.services.marketwatch_service import MarketwatchService
# from app.core.database import get_db
# from fastapi import WebSocket, WebSocketDisconnect

# router = APIRouter(prefix="/marketwatch", tags=["marketwatch"])


# @router.get("", response_model=MarketwatchResponse)
# async def get_marketwatch(
#     symbols: Optional[List[str]] = Query(None, description="List of symbols to fetch"),
#     exchange: Optional[str] = Query(None, description="Exchange filter (NSE, BSE, MCX)"),
#     db: Session = Depends(get_db)
# ):
#     """
#     Get marketwatch data
    
#     - If symbols provided: fetch LTP for those symbols
#     - If no symbols: fetch all available instruments
#     """
#     service = MarketwatchService(db)
#     items = await service.get_instruments(exchange=exchange)
    
#     return MarketwatchResponse(
#         instruments=items,
#         total=len(items),
#         timestamp=str(__import__('datetime').datetime.now())
#     )


# @router.websocket("/ws")
# async def marketwatch_ws(websocket: WebSocket):
#     await websocket.accept()

#     try:
#         while True:
#             data = await websocket.receive_json()

#             if data["action"] == "subscribe":
#                 symbols = data.get("symbols", [])
                
#                 # Dummy response (replace with real broker data)
#                 await websocket.send_json({
#                     "type": "tick",
#                     "data": [
#                         {
#                             "symbol": sym,
#                             "last_price": 100,
#                             "change_percent": 0.5
#                         }
#                         for sym in symbols
#                     ]
#                 })

#     except WebSocketDisconnect:
#         print("Client disconnected")

# @router.get("/search")
# async def search_marketwatch(
#     q: str,
#     db: Session = Depends(get_db)
# ):
#     service = MarketwatchService(db)
#     results = await service.search_instruments(q)

#     return {
#         "instruments": results
#     }