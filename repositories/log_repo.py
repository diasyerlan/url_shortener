import asyncpg

class LogRepository:
    def __init__(self, conn: asyncpg.Connection):
        self._conn = conn

    async def insert_click(
        self,
        url_code: str,
        ip: str | None,
        user_agent: str | None,
        referer: str | None,
        browser: str,
        os: str,
        device: str,
    ) -> None:
        await self._conn.execute(
            """
            INSERT INTO redirect_logs
                (url_code, ip, user_agent, referer, browser, os, device)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            url_code, ip, user_agent, referer or None, browser, os, device,
        )

    async def clicks_by_day(self, url_code: str, days: int) -> list[asyncpg.Record]:
        return await self._conn.fetch(
            """
            SELECT
                TO_CHAR(clicked_at AT TIME ZONE 'UTC', 'YYYY-MM-DD') AS date,
                COUNT(*) AS clicks
            FROM redirect_logs
            WHERE url_code = $1
              AND clicked_at >= NOW() - ($2 || ' days')::INTERVAL
            GROUP BY date
            ORDER BY date
            """,
            url_code, str(days),
        )

    async def top_referers(self, url_code: str, limit: int = 10) -> list[asyncpg.Record]:
        return await self._conn.fetch(
            """
            SELECT COALESCE(referer, 'Direct') AS referer, COUNT(*) AS count
            FROM redirect_logs
            WHERE url_code = $1
            GROUP BY referer
            ORDER BY count DESC
            LIMIT $2
            """,
            url_code, limit,
        )

    async def breakdown(self, url_code: str, column: str) -> list[asyncpg.Record]:
        # column is always one of a fixed set — see analytics_service guard
        return await self._conn.fetch(
            f"""
            SELECT {column}, COUNT(*) AS count
            FROM redirect_logs
            WHERE url_code = $1
            GROUP BY {column}
            ORDER BY count DESC
            """,
            url_code,
        )