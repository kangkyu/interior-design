"""
Pydantic schemas for API request/response validation
"""

from datetime import datetime
from typing import Optional, Any
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


# ============== Enums ==============

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class ProjectStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    FINALIZED = "finalized"
    ARCHIVED = "archived"


class ChangeType(str, Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"


class ExportFormat(str, Enum):
    PDF = "pdf"
    SHOPPING_LIST = "shopping_list"
    COLORS = "colors"
    JSON = "json"


# ============== Room Analysis ==============

class FurnitureItem(BaseModel):
    type: str
    color: Optional[str] = None
    style: Optional[str] = None
    position: Optional[str] = None


class RoomColors(BaseModel):
    walls: Optional[str] = None
    floor: Optional[str] = None
    ceiling: Optional[str] = None


class RoomAnalysis(BaseModel):
    room_type: str
    furniture: list[FurnitureItem] = []
    colors: RoomColors = RoomColors()
    lighting: Optional[str] = None
    style: Optional[str] = None
    features: list[str] = []
    dimensions_estimate: Optional[dict] = None


# ============== Design Changes ==============

class DesignChange(BaseModel):
    element: str
    action: str  # change_color, add, remove, replace
    value: Optional[str] = None
    style: Optional[str] = None
    position: Optional[str] = None
    properties: Optional[dict] = None


class DesignUnderstanding(BaseModel):
    changes: list[DesignChange]
    change_type: ChangeType
    generation_prompt: str
    needs_clarification: bool = False
    clarification_question: Optional[str] = None


# ============== Project Schemas ==============

class ProjectCreate(BaseModel):
    name: Optional[str] = "Untitled Project"


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[ProjectStatus] = None


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    status: str
    created_at: datetime
    updated_at: datetime
    has_room_photo: bool = False
    current_version: Optional[int] = None
    message_count: int = 0

    class Config:
        from_attributes = True


class ProjectDetailResponse(ProjectResponse):
    room_analysis: Optional[RoomAnalysis] = None
    current_image_url: Optional[str] = None
    original_image_url: Optional[str] = None


# ============== Message Schemas ==============

class ChatMessageCreate(BaseModel):
    content: str


class ChatMessageResponse(BaseModel):
    id: UUID
    role: MessageRole
    content: str
    image_url: Optional[str] = None
    uploaded_image_url: Optional[str] = None
    version_number: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    type: str  # "design", "clarification", "analysis", "error"
    message: str
    image_url: Optional[str] = None
    version: Optional[int] = None
    changes: Optional[list[DesignChange]] = None


# ============== Design Version Schemas ==============

class DesignVersionResponse(BaseModel):
    id: UUID
    version_number: int
    image_url: str
    thumbnail_url: Optional[str] = None
    changes: Optional[list[dict]] = None
    is_favorite: bool
    is_final: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============== Image Upload ==============

class ImageUploadResponse(BaseModel):
    image_url: str
    thumbnail_url: Optional[str] = None
    analysis: Optional[RoomAnalysis] = None
    message: str


# ============== Export Schemas ==============

class PaintMatch(BaseModel):
    brand: str
    name: str
    code: str
    hex: str


class PaintSpec(BaseModel):
    element: str  # "walls", "accent_wall", "trim"
    hex: str
    matches: list[PaintMatch]
    finish: Optional[str] = None
    coverage_sqft: Optional[float] = None
    gallons_needed: Optional[float] = None


class FurnitureSpec(BaseModel):
    item: str
    style: str
    color: str
    material: Optional[str] = None
    dimensions: Optional[str] = None
    similar_products: list[dict] = []
    price_range: Optional[str] = None


class BudgetEstimate(BaseModel):
    category: str
    low: float
    high: float


class DesignSpecification(BaseModel):
    project_id: UUID
    project_name: str
    generated_at: datetime

    # Images
    before_image_url: str
    after_image_url: str

    # Specs
    summary_of_changes: list[str]
    paint: list[PaintSpec]
    flooring: Optional[dict] = None
    furniture: list[FurnitureSpec]
    lighting: Optional[dict] = None
    decor: list[dict] = []

    # Budget
    budget: list[BudgetEstimate]
    total_budget_low: float
    total_budget_high: float


class ExportRequest(BaseModel):
    format: ExportFormat


# ============== WebSocket Messages ==============

class WSMessage(BaseModel):
    type: str
    content: Optional[str] = None
    data: Optional[dict] = None


class WSStatusUpdate(BaseModel):
    type: str = "status"
    status: str  # "understanding", "generating", "complete", "error"
    message: Optional[str] = None
    progress: Optional[float] = None
