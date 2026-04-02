from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.holdings_service import HoldingsService
from app.schemas.holding import HoldingListResponse

router = APIRouter(prefix="/holdings", tags=["holdings"])

@router.get("", response_model=HoldingListResponse)
async def get_holdings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    holdings = await HoldingsService.get_holdings_for_user(db, current_user.user_id)

    return {
        "holdings": holdings,
        "total": len(holdings)
    }