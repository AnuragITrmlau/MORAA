"""Prompt generation Pydantic schemas.

Faithfully replicates the n8n "Raw to Promotable" workflow's
data structures for prompt generation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class WorkflowAnalysisData(BaseModel):
    """11-field analysis schema from the n8n workflow's Gemini Vision node."""

    productIdentity: str = Field(default="", alias="Product Identity")
    materialProperties: str = Field(default="", alias="Material Properties")
    scaleAndProportion: str = Field(default="", alias="Scale and Proportion")
    designStyle: str = Field(default="", alias="Design Style")
    visualCraftsmanship: str = Field(default="", alias="Visual Craftsmanship")
    targetDemographic: str = Field(default="", alias="Target Demographic")
    psychographics: str = Field(default="", alias="Psychographics")
    functionalUtility: str = Field(default="", alias="Functional Utility")
    lifestyleBranding: str = Field(default="", alias="Lifestyle Branding")
    indianFestiveContext: str = Field(default="", alias="Indian Festive Context")
    marketReadiness: str = Field(default="", alias="Market Readiness")

    class Config:
        populate_by_name = True
        extra = "ignore"


class PromptGenerateRequest(BaseModel):
    """Request to generate promotional prompts for an image."""

    image_id: str = Field(..., description="ID of the uploaded image")
    description: Optional[str] = Field(None, description="Optional consumer description")


class PromptGenerateResponse(BaseModel):
    """Response containing generated prompts for all 8 categories."""

    success: bool = Field(default=True)
    workflowAnalysis: Optional[WorkflowAnalysisData] = Field(None, alias="workflow_analysis")
    prompts: Optional[Dict[str, str]] = Field(None, description="Map of category -> generated prompt")
    generationTimeMs: float = Field(default=0.0, alias="generation_time_ms")
    imageId: str = Field(default="", alias="image_id")
    error: Optional[str] = Field(None)

    class Config:
        populate_by_name = True


class PromptProcessingResponse(BaseModel):
    """Response returned while prompt generation is processing."""

    status: str = Field("processing")
    imageId: str = Field(..., alias="image_id")
    requestId: str = Field(..., alias="request_id")

    class Config:
        populate_by_name = True
