"""
Research History Models
MongoDB models for storing research queries and results
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class TokenUsage(BaseModel):
    """Token usage information"""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class ResearchResult(BaseModel):
    """Research result data"""
    content: str
    citations: List[str] = []
    sources_count: int = 0
    related_questions: Optional[List[str]] = None
    model_used: Optional[str] = None


class ResearchHistoryItem(BaseModel):
    """Research history item stored in MongoDB"""
    id: str = Field(default_factory=lambda: f"research_{int(datetime.now().timestamp())}_{id(object())}")
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    query: str
    result: ResearchResult
    duration_seconds: Optional[float] = None
    token_usage: Optional[TokenUsage] = None
    is_favorite: bool = False


class ResearchHistoryCreate(BaseModel):
    """Request to create research history"""
    query: str
    result: ResearchResult
    duration_seconds: Optional[float] = None
    token_usage: Optional[TokenUsage] = None


class ResearchHistoryResponse(BaseModel):
    """Response for research history"""
    id: str
    user_id: str
    timestamp: datetime
    query: str
    result: ResearchResult
    duration_seconds: Optional[float] = None
    token_usage: Optional[TokenUsage] = None
    is_favorite: bool = False


class BulkExportRequest(BaseModel):
    """Request to export multiple research items as PDF"""
    research_ids: List[str]
    title: Optional[str] = "Research Export"
    include_sources: bool = True
    include_metadata: bool = True