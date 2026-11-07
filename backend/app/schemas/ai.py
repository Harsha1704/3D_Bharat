from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class AICitation(BaseModel):
    citation_id: str
    source_id: Optional[int] = None
    source_title: str
    institution: Optional[str] = None
    source_url: Optional[str] = None
    publication_date: Optional[str] = None
    relevant_excerpt: str
    associated_site_id: Optional[int] = None
    associated_site_name: Optional[str] = None
    associated_graph_entity_id: Optional[int] = None
    associated_graph_entity_name: Optional[str] = None
    evidence_classification: str = "DOCUMENTED"


class AIChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None
    selected_site_id: Optional[int] = None
    research_mode: bool = False
    retrieval_filters: Optional[Dict[str, Any]] = None


class AIChatResponse(BaseModel):
    answer: str
    citations: List[AICitation] = Field(default_factory=list)
    retrieved_evidence_summary: str
    evidence_status: str
    limitations: List[str] = Field(default_factory=list)
    conversation_id: Optional[str] = None
    provider_status: Dict[str, Any] = Field(default_factory=dict)
    research_mode: bool = False


class AISearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    entity_type: Optional[str] = None
    state: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=50)


class AISearchResult(BaseModel):
    id: str
    title: str
    result_type: str
    snippet: str
    score: float
    evidence_classification: str
    source_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AISearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[AISearchResult] = Field(default_factory=list)


class AIStatusResponse(BaseModel):
    service: str = "3D BHARAT AI Heritage Intelligence"
    provider: str
    model: str
    provider_configured: bool
    embedding_service_ready: bool
    embedding_model: str
    vector_backend: str
    retrieval_service_ready: bool
    knowledge_graph_integrated: bool
    total_indexed_documents: int
    total_indexed_chunks: int


class AIDocumentIngestRequest(BaseModel):
    document_id: str = Field(..., min_length=3, max_length=100)
    title: str = Field(..., min_length=1, max_length=255)
    document_type: str = Field(default="RESEARCH_REPORT", max_length=50)
    source_url: Optional[str] = Field(default=None, max_length=500)
    publisher_institution: Optional[str] = Field(default=None, max_length=255)
    author: Optional[str] = Field(default=None, max_length=255)
    publication_date: Optional[str] = Field(default=None, max_length=100)
    text_content: str = Field(..., min_length=20)
    permission_classification: str = Field(default="PUBLIC_HERITAGE_ARCHIVE", max_length=50)
    heritage_site_id: Optional[int] = None


class AIDocumentIngestResponse(BaseModel):
    id: int
    document_id: str
    title: str
    total_chunks: int
    content_hash: str
    status: str

    model_config = ConfigDict(from_attributes=True)
