from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime


class AuthRequest(BaseModel):
    """Authentication request model"""
    email: EmailStr


class AuthResponse(BaseModel):
    """Authentication response model"""
    success: bool
    message: str
    user_email: Optional[str] = None


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: Optional[datetime] = None
    sources: Optional[List[Dict[str, Any]]] = None


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    message: str
    sources: List[Dict[str, Any]]
    conversation_id: str
    is_structured_extraction: bool = False
    structured_data: Optional[List[Dict[str, Any]]] = None


class SourceDocument(BaseModel):
    """Source document reference"""
    file_name: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    content_snippet: str
    score: Optional[float] = None


class DoorScheduleItem(BaseModel):
    """Door schedule item model"""
    mark: str
    location: Optional[str] = None
    width_mm: Optional[int] = None
    height_mm: Optional[int] = None
    fire_rating: Optional[str] = None
    material: Optional[str] = None


class StructuredExtractionRequest(BaseModel):
    """Structured extraction request"""
    extraction_type: str  # 'door_schedule', 'room_summary', etc.


class StructuredExtractionResponse(BaseModel):
    """Structured extraction response"""
    extraction_type: str
    data: List[Dict[str, Any]]
    sources: List[Dict[str, Any]]


class IngestionStatus(BaseModel):
    """Document ingestion status"""
    total_documents: int
    processed_documents: int
    total_chunks: int
    status: str
