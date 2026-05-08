import asyncpg
from datetime import datetime

class UrlRepository:
    def __init__(self, conn: asyncpg.Connection):
        self._conn = conn

    async def insert(self, code: str, long_url: str) -> asyncpg.Record:
        return await self._conn.fetchrow(
            """
            INSERT INTO urls (code, long_url)
            VALUES ($1, $2)
            RETURNING id, code, long_url, clicks, created_at
            """,
            code, long_url,
        )

    async def get_by_code(self, code: str) -> asyncpg.Record | None:
        return await self._conn.fetchrow(
            "SELECT * FROM urls WHERE code = $1", code
        )

    async def increment_clicks(self, code: str) -> asyncpg.Record | None:
        return await self._conn.fetchrow(
            """
            UPDATE urls SET clicks = clicks + 1
            WHERE code = $1
            RETURNING *
            """,
            code,
        )

    async def delete(self, code: str) -> bool:
        result = await self._conn.execute(
            "DELETE FROM urls WHERE code = $1", code
        )
        return result == "DELETE 1"