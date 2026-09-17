import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator


class URLCreate(BaseModel):
    """
    Schema for creating a short URL.
    Accepts long URL and optional custom short code.
    """
    url: str = Field(
        ...,
        description="The original long URL to shorten",
        json_schema_extra={"example": "https://example.com/very-long-path"}
    )
    custom_code: Optional[str] = Field(
        None,
        min_length=3,
        max_length=30,
        description="Optional custom short code (alphanumeric, hyphens, underscores)",
        json_schema_extra={"example": "my-custom-code"}
    )

    @field_validator("url")
    @classmethod
    def validate_url_scheme(cls, v: str) -> str:
        v = v.strip()
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("URL must start with 'http://' or 'https://'")
        if len(v) > 2048:
            raise ValueError("URL length must be 2048 characters or less")
        return v

    @field_validator("custom_code")
    @classmethod
    def validate_custom_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v.isalnum() and not all(c in "-_" or c.isalnum() for c in v):
            raise ValueError("Custom short code can only contain alphanumeric characters, hyphens, and underscores")
        return v


class URLResponse(BaseModel):
    """
    Schema for short URL response.
    """
    id: uuid.UUID
    short_url: str = Field(..., description="Full accessible short URL")
    short_code: str = Field(..., description="Unique short code identifier")
    original_url: str = Field(..., description="Target original long URL")
    click_count: int = Field(..., description="Total redirect click count")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = ConfigDict(from_attributes=True)


class URLShortenResponse(BaseModel):
    """
    Minimal schema matching exact POST /shorten request requirement while supporting full fields.
    """
    short_url: str
    short_code: str
    original_url: Optional[str] = None
    click_count: Optional[int] = 0
    created_at: Optional[datetime] = None


class URLStatsResponse(BaseModel):
    """
    Basic analytics schema for GET /stats/{short_code}
    """
    short_code: str
    original_url: str
    click_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class URLAnalyticsResponse(BaseModel):
    """
    Advanced analytics schema for GET /analytics/{short_code}
    """
    short_code: str
    original_url: str
    total_clicks: int
    clicks_today: int
    last_7_days_clicks: int
    last_30_days_clicks: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
