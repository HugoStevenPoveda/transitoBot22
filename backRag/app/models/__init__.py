from pydantic import BaseModel
from typing import List, Optional


class QueryRequest(BaseModel):
    query: str
    max_results: Optional[int] = 3
    confidence_threshold: Optional[float] = 0.4  # Umbral m�s bajo por defecto


class Source(BaseModel):
    article: str
    law: str
    description: str
    similarity_score: float
    content_snippet: str


class QueryResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[Source]
    processing_time: float


class HealthResponse(BaseModel):
    status: str
    version: str
    database_status: str
    total_articles: Optional[int] = None


class ContextData(BaseModel):
    system: str
    user: str


class OpenRouterRequest(BaseModel):
    context: ContextData
    pregunta: str
    entidades: List[dict] = []
    intencion: str


class OpenRouterResponse(BaseModel):
    answer: str
    model_used: str
    processing_time: float


class AnthropicRequest(BaseModel):
    context: ContextData
    pregunta: str
    entidades: List[dict] = []
    intencion: str


class AnthropicResponse(BaseModel):
    answer: str
    model_used: str
    processing_time: float
