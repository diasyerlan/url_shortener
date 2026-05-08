import asyncpg
from core.database import get_pool
from core.ua_parser import parse_user_agent
from models.schemas import ClickEvent, AnalyticsResponse

_ALLOWED_COLUMNS = {"browser", "os", "device"}

class AnalyticsService:
    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool

    async def log_click(self, event: ClickEvent) -> None:
        """Called as a BackgroundTask — must not raise."""
        try:
            parsed = parse_user_agent(event.user_agent)
            async with self._pool.acquire() as conn:
                from repositories.log_repo import LogRepository
                repo = LogRepository(conn)
                await repo.insert_click(
                    url_code=event.url_code,
                    ip=event.ip,
                    user_agent=event.user_agent,
                    referer=event.referer,
                    **parsed,
                )
        except Exception as exc:
            # Log to stdout — swap for proper logger in production
            print(f"[analytics] log_click failed: {exc}")

    async def get_analytics(self, code: str, days: int = 30) -> AnalyticsResponse | None:
        async with self._pool.acquire() as conn:
            from repositories.url_repo import UrlRepository
            from repositories.log_repo import LogRepository

            url_repo = UrlRepository(conn)
            log_repo = LogRepository(conn)

            url_row = await url_repo.get_by_code(code)
            if not url_row:
                return None

            clicks_by_day     = await log_repo.clicks_by_day(code, days)
            top_referers      = await log_repo.top_referers(code)
            browsers          = await log_repo.breakdown(code, "browser")
            devices           = await log_repo.breakdown(code, "device")
            operating_systems = await log_repo.breakdown(code, "os")

        return AnalyticsResponse(
            code=url_row["code"],
            long_url=url_row["long_url"],
            total_clicks=url_row["clicks"],
            clicks_by_day=[dict(r) for r in clicks_by_day],
            top_referers=[dict(r) for r in top_referers],
            browsers=[dict(r) for r in browsers],
            devices=[dict(r) for r in devices],
            operating_systems=[dict(r) for r in operating_systems],
        )