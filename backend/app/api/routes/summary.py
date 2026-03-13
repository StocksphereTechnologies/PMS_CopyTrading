from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User

from app.services.summary_service import SummaryService
from app.schemas.summary import SummaryResponse

router = APIRouter(prefix="/summary", tags=["summary"])


@router.get("", response_model=SummaryResponse)
async def get_summary(

    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)

):

    return await SummaryService.get_summary_for_user(db, current_user.user_id)