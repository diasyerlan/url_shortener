from pathlib import Path
import asyncpg

from core.config import settings

_pool: asyncpg.Pool | None = None

async def create_pool() -> asyncpg.Pool:
    global _pool
    _pool = await asyncpg.create_pool(settings.database_url, min_size=2, max_size=10)
    return _pool

async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        raise RuntimeError("DB pool not initialised — call create_pool() first")
    return _pool

async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def run_migrations() -> None:
    sql = (Path(__file__).parent.parent / "migrations" / "001_init.sql").read_text()
    pool = await get_pool()
    async with pool.acquire() as conn:
        for statement in sql.split(";"):
            statement = statement.strip()
            if statement:
                await conn.execute(statement)