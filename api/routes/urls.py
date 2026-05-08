from fastapi import APIRouter, HTTPException, Request, BackgroundTasks, Depends
from fastapi.responses import RedirectResponse

from api.dependencies import get_url_service, get_analytics_service
from models.schemas import ShortenRequest, ShortenResponse, StatsResponse, ClickEvent
from services.url_service import UrlService
from services.analytics_service import AnalyticsService

router = APIRouter(tags=["urls"])

@router.post("/shorten", response_model=ShortenResponse, status_code=201)
async def shorten(
    body: ShortenRequest,
    svc: UrlService = Depends(get_url_service),
):
    try:
        return await svc.shorten(body)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.get("/stats/{code}", response_model=StatsResponse)
async def stats(
    code: str,
    svc: UrlService = Depends(get_url_service),
):
    result = await svc.get_stats(code)
    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result

@router.delete("/{code}", status_code=204)
async def delete(
    code: str,
    svc: UrlService = Depends(get_url_service),
):
    if not await svc.delete(code):
        raise HTTPException(status_code=404, detail="Not found")

@router.get("/{code}")
async def redirect(
    code: str,
    request: Request,
    background_tasks: BackgroundTasks,
    url_svc: UrlService = Depends(get_url_service),
    analytics_svc: AnalyticsService = Depends(get_analytics_service),
):
    long_url = await url_svc.get_for_redirect(code)
    if not long_url:
        raise HTTPException(status_code=404, detail="Not found")

    background_tasks.add_task(
        analytics_svc.log_click,
        ClickEvent(
            url_code=code,
            ip=request.headers.get("X-Forwarded-For", request.client.host),
            user_agent=request.headers.get("User-Agent"),
            referer=request.headers.get("Referer"),
        ),
    )

    return RedirectResponse(url=long_url, status_code=307)