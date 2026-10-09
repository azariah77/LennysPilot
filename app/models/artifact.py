from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from app.database import Base
import datetime
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Artifact(Base):
    __tablename__ = "artifacts"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    title = Column(String, nullable=False)
    content_type = Column(String, nullable=False) # 'markdown' or 'html'
    content = Column(Text, nullable=False)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
