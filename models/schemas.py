from pydantic import BaseModel, HttpUrl, field_validator
from datetime import datetime

# ── Request bodies ──────────────────────────────────────────

class ShortenRequest(BaseModel):
    url: HttpUrl
    custom_code: str | None = None

    @field_validator("custom_code")
    @classmethod
    def code_alphanumeric(cls, v: str | None) -> str | None:
        if v and not v.isalnum():
            raise ValueError("custom_code must be alphanumeric")
        return v

# ── Response bodies ─────────────────────────────────────────

class ShortenResponse(BaseModel):
    short_url: str
    code: str

class StatsResponse(BaseModel):
    code: str
    long_url: str
    clicks: int
    created_at: datetime

class ClicksOverTime(BaseModel):
    date: str
    clicks: int

class AnalyticsResponse(BaseModel):
    code: str
    long_url: str
    total_clicks: int
    clicks_by_day: list[ClicksOverTime]
    top_referers: list[dict]
    browsers: list[dict]
    devices: list[dict]
    operating_systems: list[dict]

# ── Internal data transfer objects (no HTTP concern) ────────

class ClickEvent(BaseModel):
    url_code: str
    ip: str | None
    user_agent: str | None
    referer: str | None