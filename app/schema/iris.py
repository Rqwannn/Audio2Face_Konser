from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from uuid import UUID

class DataDiriBase(BaseModel):
    user_uuid: UUID
    nik: str = Field(..., min_length=16, max_length=16)
    file_suara: Optional[str] = None
    file_wajah: Optional[str] = None
    embeddings_status: Optional[bool] = None
    
    @field_validator('nik')
    @classmethod
    def validate_nik(cls, v):
        if not v.isdigit():
            raise ValueError('NIK harus berupa angka')
        if len(v) != 16:
            raise ValueError('NIK harus 16 digit')
        return v

class DataDiriResponse(DataDiriBase):
    uuid: UUID
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }

class DataDiriListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    data: list[DataDiriResponse]