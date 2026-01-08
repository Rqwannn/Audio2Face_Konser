from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime, timezone
import uuid
from app.config import Base

class Iris(Base):
    __tablename__ = "mt_data_diris"
    
    uuid = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4, 
        unique=True, 
        nullable=False
    )
    user_uuid = Column(UUID(as_uuid=True), nullable=False, index=True)
    nik = Column(String(16), nullable=False, unique=True, index=True)
    file_suara = Column(String(255), nullable=True)
    file_wajah = Column(String(255), nullable=True)

    embeddings_status = Column(Boolean, default=False, nullable=False)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<DataDiri(uuid={self.uuid}, nik={self.nik})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "uuid": str(self.uuid),
            "user_uuid": str(self.user_uuid),
            "nik": self.nik,
            "file_suara": self.file_suara,
            "file_wajah": self.file_wajah,
            "embeddings_status": self.embeddings_status,
            "createdAt": self.createdAt.isoformat() if self.createdAt else None,
            "updatedAt": self.updatedAt.isoformat() if self.updatedAt else None,
        }