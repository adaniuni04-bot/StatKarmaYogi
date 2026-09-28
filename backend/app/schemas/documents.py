from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class DocumentChunkResponse(BaseModel):
    id: str
    chunk_index: int
    content: str
    page_number: int
    section_header: Optional[str] = None
    competency_code: Optional[str] = None
    token_count: int

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: str
    title: str
    filename: str
    file_type: str
    file_size_bytes: int
    source_organization: str
    authority_tier: str
    status: str
    error_message: Optional[str] = None
    total_pages: int
    total_chunks: int
    scan_status: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentDetailResponse(DocumentResponse):
    chunks: List[DocumentChunkResponse] = []
