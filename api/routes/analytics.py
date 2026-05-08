from fastapi import APIRouter, HTTPException, Depends, Query
from api.dependencies import get_analytics_service
from models.schemas import AnalyticsResponse
from services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/{code}", response_model=AnalyticsResponse)
async def analytics(
    code: str,
    days: int = Query(default=30, ge=1, le=365),
    svc: AnalyticsService = Depends(get_analytics_service),
):
    result = await svc.get_analytics(code, days)
    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result