from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PDFResponse(BaseModel):
    pdf_id: str
    filename: str
    size: int
    pages: int
    uploaded_at: datetime
    message: str = "PDF uploaded successfully"


class ChatRequest(BaseModel):
    message: str = Field(..., description="The message to ask about the PDF content")


class ChatResponse(BaseModel):
    response: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    detail: str
