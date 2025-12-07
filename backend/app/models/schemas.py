from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class UploadResponse(BaseModel):
    session_id: str
    filename: str
    text_length: int
    message: str


class SummarizeRequest(BaseModel):
    session_id: str
    custom_prompt: Optional[str] = None
    model: Optional[str] = None


class SummarizeResponse(BaseModel):
    session_id: str
    summary: str
    model: str


class AskRequest(BaseModel):
    session_id: str
    question: str
    model: Optional[str] = None


class AskResponse(BaseModel):
    session_id: str
    question: str
    answer: str
    sources: List[str]


class RateRequest(BaseModel):
    session_id: str
    rating: str  # "thumbs_up" or "thumbs_down"


class RateResponse(BaseModel):
    session_id: str
    rating: str
    message: str


class ModelInfo(BaseModel):
    id: str
    name: str
    is_default: bool


class SessionData(BaseModel):
    session_id: str
    filename: str
    text: str
    pdf_path: Optional[str] = None
    summary: Optional[str] = None
    storyline: Optional[str] = None
    rating: Optional[str] = None
    created_at: datetime


class SessionDetailResponse(BaseModel):
    session_id: str
    filename: str
    text: str
    has_pdf: bool = False
    summary: Optional[str] = None
    storyline: Optional[str] = None
    rating: Optional[str] = None
    created_at: str


class StorylineRequest(BaseModel):
    session_id: str
    model: Optional[str] = None
    language: Optional[str] = "en"  # "en" or "ko"


class StorylineResponse(BaseModel):
    session_id: str
    storyline: str
    model: str

