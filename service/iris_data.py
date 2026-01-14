from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict

from app.repositories.iris import DataDiriRepository
from app.schema.iris import DataDiriResponse

class DataDiriService:
    def __init__(self, db: AsyncSession):
        self.repository = DataDiriRepository(db)
    
    async def get_data_diri_by_nik(self, nik: str) -> Optional[DataDiriResponse]:
        """Get full data diri by NIK"""
        db_data = await self.repository.get_by_nik(nik)
        if not db_data:
            return None
        return DataDiriResponse.model_validate(db_data)
    
    async def get_file_wajah_by_nik(self, nik: str) -> Optional[str]:
        """Get only file_wajah by NIK"""
        return await self.repository.get_file_wajah_by_nik(nik)
    
    async def get_file_suara_by_nik(self, nik: str) -> Optional[str]:
        """Get only file_suara by NIK"""
        return await self.repository.get_file_suara_by_nik(nik)
    
    async def get_files_by_nik(self, nik: str) -> Optional[Dict[str, str]]:
        """Get both file_wajah and file_suara by NIK"""
        return await self.repository.get_files_by_nik(nik)
    
    async def get_embeddings_status_by_nik(self, nik: str) -> Optional[Dict[str, str]]:
        """Get both file_wajah and file_suara by NIK"""
        return await self.repository.get_embeddings_status_by_nik(nik)
    
    async def update_embeddings_status_to_true(self, nik: str) -> Optional[Dict[str, str]]:
        """Get both file_wajah and file_suara by NIK"""
        return await self.repository.update_embeddings_status_to_true(nik)