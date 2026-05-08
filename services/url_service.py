import secrets
import asyncpg
from core.config import settings
from core.database import get_pool
from repositories.url_repo import UrlRepository
from models.schemas import ShortenRequest, ShortenResponse, StatsResponse

_ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

def _generate_code(length: int) -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(length))

class UrlService:
    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool

    async def shorten(self, body: ShortenRequest) -> ShortenResponse:
        code = body.custom_code or _generate_code(settings.code_length)

        async with self._pool.acquire() as conn:
            repo = UrlRepository(conn)
            try:
                row = await repo.insert(code, str(body.url))
            except asyncpg.UniqueViolationError:
                raise ValueError(f"Code '{code}' is already taken")

        return ShortenResponse(
            short_url=f"{settings.base_url}/{row['code']}",
            code=row["code"],
        )

    async def get_for_redirect(self, code: str) -> str | None:
        """Returns the long URL after atomically incrementing clicks."""
        async with self._pool.acquire() as conn:
            repo = UrlRepository(conn)
            row = await repo.increment_clicks(code)
        return row["long_url"] if row else None

    async def get_stats(self, code: str) -> StatsResponse | None:
        async with self._pool.acquire() as conn:
            repo = UrlRepository(conn)
            row = await repo.get_by_code(code)
        if not row:
            return None
        return StatsResponse(**dict(row))

    async def delete(self, code: str) -> bool:
        async with self._pool.acquire() as conn:
            repo = UrlRepository(conn)
            return await repo.delete(code)