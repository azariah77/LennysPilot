from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from pgvector.sqlalchemy import Vector
from app.database import Base
import datetime

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True)  # Usually the guest slug
    guest_slug = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    content_hash = Column(String, nullable=False)  # Hash of file content for idempotency
    metadata_json = Column(JSONB, default={})
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

class Chunk(Base):
    __tablename__ = "chunks"
    
    id = Column(String, primary_key=True) # e.g. doc_id_chunk_0
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"))
    chunk_index = Column(Integer, nullable=False)
    speaker = Column(String)
    timestamp = Column(String) # HH:MM:SS
    text = Column(Text, nullable=False)
    # Using 768 dimensions which is standard for Nomic/Ollama embed models
    embedding = Column(Vector(768)) 
    search_vector = Column(TSVECTOR)
