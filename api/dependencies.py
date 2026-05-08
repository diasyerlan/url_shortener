from fastapi import Depends
import asyncpg
from core.database import get_pool
from services.url_service import UrlService
from services.analytics_service import AnalyticsService

async def get_url_service() -> UrlService:
    return UrlService(await get_pool())

async def get_analytics_service() -> AnalyticsService:
    return AnalyticsService(await get_pool())