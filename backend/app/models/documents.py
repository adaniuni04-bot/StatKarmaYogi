import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(20), nullable=False)  # PDF, DOCX, PPTX, TXT
    mime_type = Column(String(100), nullable=True)
    file_size_bytes = Column(Integer, default=0)
    source_organization = Column(String(255), default="MoSPI")
    authority_tier = Column(String(10), default="TIER_A")  # TIER_A, TIER_B, TIER_C, TIER_D
    status = Column(String(50), default="UPLOADED")  # UPLOADED, PROCESSING, READY, FAILED
    error_message = Column(Text, nullable=True)
    total_pages = Column(Integer, default=1)
    total_chunks = Column(Integer, default=0)
    scan_status = Column(String(50), default="CLEAN")  # CLEAN, SCANNING, INFECTED
    uploaded_by = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan", order_by="DocumentChunk.chunk_index")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    page_number = Column(Integer, default=1)
    section_header = Column(String(255), nullable=True)
    competency_code = Column(String(50), nullable=True, index=True)
    token_count = Column(Integer, default=0)
    embedding_json = Column(Text, nullable=True)  # Stores vector as JSON string for portability
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    document = relationship("Document", back_populates="chunks")
