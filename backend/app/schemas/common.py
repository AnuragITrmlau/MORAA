"""Common/shared Pydantic schemas."""

from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field("healthy", description="Service health status")


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Optional error code")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Error timestamp"
    )


class ValidationErrorResponse(BaseModel):
    """Validation error details."""

    field: str = Field(..., description="Field name with error")
    message: str = Field(..., description="Error message")


class DeleteResponse(BaseModel):
    """Delete operation response."""

    success: bool = Field(..., description="Whether deletion succeeded")
    message: str = Field(..., description="Status message")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""

    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(20, description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")


class PricePointResponse(BaseModel):
    """Price point data for charts."""

    date: str = Field(..., description="Date string")
    price: float = Field(..., description="Price value")
    volume: int = Field(..., description="Sales volume")


class MarketDataResponse(BaseModel):
    """Market data summary."""

    id: str = Field(..., description="Market data ID")
    date: str = Field(..., description="Date string")
    averagePrice: float = Field(..., alias="average_price")
    medianPrice: float = Field(..., alias="median_price")
    highestPrice: float = Field(..., alias="highest_price")
    lowestPrice: float = Field(..., alias="lowest_price")
    totalListings: int = Field(..., alias="total_listings")
    totalSales: int = Field(..., alias="total_sales")
    category: str = Field(..., description="Product category")

    class Config:
        populate_by_name = True


class CompetitorProductResponse(BaseModel):
    """Competitor product listing."""

    id: str
    name: str
    platform: str
    price: float
    currency: str
    link: str
    material: str
    weight: float
    goldPurity: str = Field(..., alias="gold_purity")
    sellerRating: float = Field(..., alias="seller_rating")
    salesCount: int = Field(..., alias="sales_count")
    listedDate: str = Field(..., alias="listed_date")

    class Config:
        populate_by_name = True


class TrendDataResponse(BaseModel):
    """Market trend data."""

    keyword: str
    growth: float
    volume: int
    sentiment: str


class SEODataResponse(BaseModel):
    """SEO keyword analysis."""

    keyword: str
    searchVolume: int = Field(..., alias="search_volume")
    difficulty: int
    opportunity: str
    currentRank: Optional[int] = Field(None, alias="current_rank")
    suggestedTags: List[str] = Field(default_factory=list, alias="suggested_tags")

    class Config:
        populate_by_name = True


class RiskAssessmentResponse(BaseModel):
    """Risk assessment data."""

    category: str
    risk: str
    score: float
    description: str
    mitigation: str
