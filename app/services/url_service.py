from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.url import URL
from app.models.click_log import ClickLog
from app.schemas.url import URLCreate
from app.utils.shortener import generate_short_code
from app.core.logging import logger


class URLService:
    """
    Business logic layer for handling URL shortening operations, redirects,
    click tracking, and advanced analytics.
    """

    @staticmethod
    async def create_short_url(db: AsyncSession, url_in: URLCreate) -> URL:
        """
        Creates a new short URL record. Handles custom short codes or auto-generates
        a unique Base62 code with collision resolution.
        """
        # Case 1: Custom short code specified by user
        if url_in.custom_code:
            existing_stmt = select(URL).where(URL.short_code == url_in.custom_code)
            result = await db.execute(existing_stmt)
            if result.scalar_one_or_none() is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Short code '{url_in.custom_code}' is already in use."
                )
            short_code = url_in.custom_code
        else:
            # Case 2: Auto-generate unique short code with retry logic
            max_retries = 5
            short_code = None
            for _ in range(max_retries):
                candidate = generate_short_code(length=6)
                stmt = select(URL).where(URL.short_code == candidate)
                res = await db.execute(stmt)
                if res.scalar_one_or_none() is None:
                    short_code = candidate
                    break

            if not short_code:
                # Fallback to longer code if 6-char collisions occur
                short_code = generate_short_code(length=8)

        new_url = URL(
            original_url=url_in.url,
            short_code=short_code,
            click_count=0
        )
        db.add(new_url)
        await db.commit()
        await db.refresh(new_url)
        logger.info(f"Created short URL code='{short_code}' for original='{url_in.url}'")
        return new_url

    @staticmethod
    async def get_by_code(db: AsyncSession, short_code: str) -> Optional[URL]:
        """
        Fetch a URL record by short code.
        """
        stmt = select(URL).where(URL.short_code == short_code)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def process_redirect(
        db: AsyncSession,
        url_obj: URL,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> str:
        """
        Increments click count for a URL, logs detailed click event asynchronously,
        and returns the original long URL.
        """
        # Increment total click counter
        url_obj.click_count += 1
        url_obj.updated_at = datetime.now(timezone.utc)

        # Log click metadata for advanced analytics
        click_log = ClickLog(
            url_id=url_obj.id,
            timestamp=datetime.now(timezone.utc),
            user_agent=user_agent[:512] if user_agent else None,
            ip_address=ip_address[:45] if ip_address else None
        )
        db.add(click_log)
        await db.commit()
        logger.info(f"Redirect processed for short_code='{url_obj.short_code}' | total_clicks={url_obj.click_count}")
        return url_obj.original_url

    @staticmethod
    async def get_advanced_analytics(db: AsyncSession, short_code: str) -> Optional[Dict[str, Any]]:
        """
        Computes detailed click analytics for a given short code:
        - Total clicks
        - Clicks today
        - Clicks last 7 days
        - Clicks last 30 days
        """
        url_obj = await URLService.get_by_code(db, short_code)
        if not url_obj:
            return None

        now = datetime.now(timezone.utc)
        start_of_today = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
        seven_days_ago = now - timedelta(days=7)
        thirty_days_ago = now - timedelta(days=30)

        # Query clicks today
        today_stmt = select(func.count(ClickLog.id)).where(
            ClickLog.url_id == url_obj.id,
            ClickLog.timestamp >= start_of_today
        )
        today_res = await db.execute(today_stmt)
        clicks_today = today_res.scalar() or 0

        # Query clicks last 7 days
        stmt_7d = select(func.count(ClickLog.id)).where(
            ClickLog.url_id == url_obj.id,
            ClickLog.timestamp >= seven_days_ago
        )
        res_7d = await db.execute(stmt_7d)
        clicks_7d = res_7d.scalar() or 0

        # Query clicks last 30 days
        stmt_30d = select(func.count(ClickLog.id)).where(
            ClickLog.url_id == url_obj.id,
            ClickLog.timestamp >= thirty_days_ago
        )
        res_30d = await db.execute(stmt_30d)
        clicks_30d = res_30d.scalar() or 0

        return {
            "short_code": url_obj.short_code,
            "original_url": url_obj.original_url,
            "total_clicks": url_obj.click_count,
            "clicks_today": clicks_today,
            "last_7_days_clicks": clicks_7d,
            "last_30_days_clicks": clicks_30d,
            "created_at": url_obj.created_at,
        }

    @staticmethod
    async def list_urls(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[URL]:
        """
        List all shortened URLs with pagination.
        """
        stmt = select(URL).order_by(URL.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def delete_url(db: AsyncSession, short_code: str) -> bool:
        """
        Deletes a shortened URL record by short_code. Associated click logs are removed via ON DELETE CASCADE.
        """
        url_obj = await URLService.get_by_code(db, short_code)
        if not url_obj:
            return False

        await db.delete(url_obj)
        await db.commit()
        logger.info(f"Deleted URL record for short_code='{short_code}'")
        return True
