from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.database import create_pool, close_pool, run_migrations
from api.routes import urls, analytics

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_pool()
    await run_migrations()
    yield
    await close_pool()

app = FastAPI(title="URL Shortener", lifespan=lifespan)

# analytics router first — prevents /analytics being swallowed by /{code}
app.include_router(analytics.router)
app.include_router(urls.router)