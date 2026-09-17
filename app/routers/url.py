from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.schemas.url import URLCreate, URLResponse, URLShortenResponse, URLStatsResponse
from app.services.url_service import URLService
from app.core.config import settings

router = APIRouter(tags=["URLs"])


def build_short_url(request: Request, short_code: str) -> str:
    """
    Constructs the full short URL using configured BASE_URL or request base URL.
    """
    base = settings.BASE_URL.rstrip("/") if settings.BASE_URL else str(request.base_url).rstrip("/")
    return f"{base}/{short_code}"


@router.post(
    "/shorten",
    response_model=URLShortenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Short URL",
    description="Submits a long URL and generates a unique short code and short URL."
)
@router.post(
    "/api/v1/shorten",
    response_model=URLShortenResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False
)
async def create_short_url(
    url_in: URLCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    url_obj = await URLService.create_short_url(db=db, url_in=url_in)
    short_url = build_short_url(request, url_obj.short_code)

    return URLShortenResponse(
        short_url=short_url,
        short_code=url_obj.short_code,
        original_url=url_obj.original_url,
        click_count=url_obj.click_count,
        created_at=url_obj.created_at
    )


@router.get(
    "/urls",
    response_model=List[URLResponse],
    summary="List Short URLs",
    description="Retrieves a paginated list of created short URLs."
)
@router.get(
    "/api/v1/urls",
    response_model=List[URLResponse],
    include_in_schema=False
)
async def list_urls(
    request: Request,
    skip: int = Query(0, ge=0, description="Offset to skip"),
    limit: int = Query(100, ge=1, le=500, description="Max items to return"),
    db: AsyncSession = Depends(get_db)
):
    urls = await URLService.list_urls(db=db, skip=skip, limit=limit)
    response_list = []
    for u in urls:
        response_list.append(
            URLResponse(
                id=u.id,
                short_url=build_short_url(request, u.short_code),
                short_code=u.short_code,
                original_url=u.original_url,
                click_count=u.click_count,
                created_at=u.created_at
            )
        )
    return response_list


@router.get(
    "/stats/{short_code}",
    response_model=URLStatsResponse,
    summary="Get URL Stats",
    description="Returns basic analytics such as click count and creation timestamp for a short URL."
)
@router.get(
    "/api/v1/stats/{short_code}",
    response_model=URLStatsResponse,
    include_in_schema=False
)
async def get_url_stats(
    short_code: str,
    db: AsyncSession = Depends(get_db)
):
    url_obj = await URLService.get_by_code(db=db, short_code=short_code)
    if not url_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short URL with code '{short_code}' was not found."
        )

    return URLStatsResponse(
        short_code=url_obj.short_code,
        original_url=url_obj.original_url,
        click_count=url_obj.click_count,
        created_at=url_obj.created_at
    )


@router.delete(
    "/{short_code}",
    status_code=status.HTTP_200_OK,
    summary="Delete Short URL",
    description="Deletes a short URL by its short code."
)
@router.delete(
    "/api/v1/{short_code}",
    status_code=status.HTTP_200_OK,
    include_in_schema=False
)
async def delete_short_url(
    short_code: str,
    db: AsyncSession = Depends(get_db)
):
    deleted = await URLService.delete_url(db=db, short_code=short_code)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short URL with code '{short_code}' was not found."
        )
    return {"message": f"Short URL '{short_code}' successfully deleted."}


@router.get(
    "/{short_code}",
    summary="Redirect to Original URL",
    description="Redirects user to the target long URL and logs the click event."
)
async def redirect_to_url(
    short_code: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    # Reserved endpoints safeguard
    if short_code in ("docs", "redoc", "openapi.json", "health", "favicon.ico", "analytics"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    url_obj = await URLService.get_by_code(db=db, short_code=short_code)
    if not url_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short code '{short_code}' not found."
        )

    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    if request.headers.get("x-forwarded-for"):
        ip_address = request.headers.get("x-forwarded-for").split(",")[0].strip()

    original_url = await URLService.process_redirect(
        db=db,
        url_obj=url_obj,
        user_agent=user_agent,
        ip_address=ip_address
    )

    return RedirectResponse(url=original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
