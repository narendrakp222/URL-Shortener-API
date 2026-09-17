from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.schemas.url import URLAnalyticsResponse
from app.services.url_service import URLService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/{short_code}",
    response_model=URLAnalyticsResponse,
    summary="Get Advanced Analytics",
    description="Returns total clicks, clicks today, last 7 days, and last 30 days breakdown."
)
@router.get(
    "/api/v1/analytics/{short_code}",
    response_model=URLAnalyticsResponse,
    include_in_schema=False
)
async def get_advanced_analytics(
    short_code: str,
    db: AsyncSession = Depends(get_db)
):
    analytics = await URLService.get_advanced_analytics(db=db, short_code=short_code)
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short URL code '{short_code}' was not found."
        )

    return URLAnalyticsResponse(**analytics)
