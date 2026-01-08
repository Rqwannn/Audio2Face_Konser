from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional, Dict

from app.models.iris import Iris

class DataDiriRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_nik(self, nik: str) -> Optional[Iris]:
        """Get data diri by NIK"""
        result = await self.db.execute(
            select(Iris).where(Iris.nik == nik)
        )
        return result.scalar_one_or_none()
    
    async def get_file_wajah_by_nik(self, nik: str) -> Optional[str]:
        """Get only file_wajah by NIK"""
        result = await self.db.execute(
            select(Iris.file_wajah).where(Iris.nik == nik)
        )
        return result.scalar_one_or_none()
    
    async def get_file_suara_by_nik(self, nik: str) -> Optional[str]:
        """Get only file_suara by NIK"""
        result = await self.db.execute(
            select(Iris.file_suara).where(Iris.nik == nik)
        )
        return result.scalar_one_or_none()
    
    async def get_files_by_nik(self, nik: str) -> Optional[Dict[str, str]]:
        """Get file_wajah and file_suara by NIK"""
        result = await self.db.execute(
            select(Iris.file_wajah, Iris.file_suara)
            .where(Iris.nik == nik)
        )
        row = result.first()
        
        if row:
            return {
                "file_wajah": row[0],
                "file_suara": row[1]
            }
        return None
    
    async def get_embeddings_status_by_nik(self, nik: str) -> Optional[bool]:
        """Get only embeddings_status by NIK"""
        result = await self.db.execute(
            select(Iris.embeddings_status).where(Iris.nik == nik)
        )
        return result.scalar_one_or_none()
    
    async def update_embeddings_status_to_true(self, nik: str) -> bool:
        """Update embeddings_status to True by NIK"""
        stmt = (
            update(Iris)
            .where(Iris.nik == nik)
            .values(embeddings_status=True)
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit() 
        
        return result.rowcount > 0