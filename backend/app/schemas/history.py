"""History Pydantic schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class HistoryCreate(BaseModel):
    """Internal history entry creation data."""

    user_id: Optional[str] = None
    analysis_id: str
    image_id: str
    product_name: Optional[str] = None
    image_url: Optional[str] = None
    status: str = "completed"
    estimated_price: Optional[float] = None


class HistoryItemResponse(BaseModel):
    """History item response matching frontend HistoryItem type.

    Uses camelCase field names (no aliases) for correct serialisation.
    """

    id: str = Field(..., description="History entry ID")
    productName: str = Field(default="", description="Product name")
    imageUrl: str = Field(default="", description="Image URL")
    analysisDate: str = Field(default="", description="Analysis date")
    status: str = Field(default="completed", description="Analysis status")
    estimatedPrice: float = Field(default=0.0, description="Estimated price")


class HistoryListResponse(BaseModel):
    """List of history items."""

    items: List[HistoryItemResponse] = Field(default_factory=list)
    total: int = Field(0, description="Total count")


class HistoryStatsResponse(BaseModel):
    """History statistics response."""

    total: int = Field(0, description="Total analyses count")
    thisMonth: int = Field(0, description="Analyses this month")
    averagePrice: float = Field(0.0, description="Average estimated price")
