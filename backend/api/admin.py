from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import aiofiles
import os
from datetime import datetime

from services.rag_service import RAGService
from services.ingestion_service import IngestionService
from database import get_db, DataSource, ChatLog
from api.auth import get_current_admin
from config import settings

router = APIRouter()

rag_service = RAGService()
ingestion_service = IngestionService(
    chunk_size=settings.chunk_size,
    chunk_overlap=settings.chunk_overlap
)


class XMLIngestRequest(BaseModel):
    url: Optional[str] = None


@router.post("/ingest/xml")
async def ingest_xml(
    request: XMLIngestRequest,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """???????? XML ?????"""
    try:
        xml_url = request.url or settings.xml_catalog_url
        
        # ??????? XML
        chunks = await ingestion_service.ingest_xml(xml_url)
        
        # ?????????? ? ????????? ?????????
        batch_id = f"xml_{int(datetime.now().timestamp())}"
        rag_service.add_chunks(chunks, batch_id=batch_id)
        
        # ?????????? ?????????? ? ?????????
        data_source = DataSource(
            name=f"XML Catalog - {xml_url}",
            source_type="xml",
            source_path=xml_url,
            chunks_count=len(chunks)
        )
        db.add(data_source)
        db.commit()
        
        return {
            "message": "XML ingested successfully",
            "chunks_count": len(chunks),
            "source": xml_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting XML: {str(e)}")


@router.post("/ingest/file")
async def ingest_file(
    file: UploadFile = File(...),
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """???????? ????????????? ?????"""
    try:
        # ????????? ????
        os.makedirs(settings.upload_dir, exist_ok=True)
        file_path = os.path.join(settings.upload_dir, file.filename)
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # ??????? ?????
        chunks = ingestion_service.ingest_file(file_path, file.content_type)
        
        # ?????????? ? ????????? ?????????
        batch_id = f"file_{int(datetime.now().timestamp())}"
        rag_service.add_chunks(chunks, batch_id=batch_id)
        
        # ?????????? ?????????? ? ?????????
        data_source = DataSource(
            name=file.filename,
            source_type="file",
            source_path=file_path,
            chunks_count=len(chunks)
        )
        db.add(data_source)
        db.commit()
        
        return {
            "message": "File ingested successfully",
            "chunks_count": len(chunks),
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting file: {str(e)}")


@router.get("/stats")
async def get_stats(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """?????????? ?????????????"""
    try:
        # ?????????? ?? ?????
        total_chats = db.query(ChatLog).count()
        
        # ?????????? ?? ??????????
        data_sources = db.query(DataSource).all()
        total_sources = len(data_sources)
        total_chunks = sum([ds.chunks_count for ds in data_sources])
        
        # ?????????? ? ????????? Qdrant
        collection_info = rag_service.get_collection_info()
        
        return {
            "total_chats": total_chats,
            "total_sources": total_sources,
            "total_chunks": total_chunks,
            "qdrant_points": collection_info.get("points_count", 0),
            "data_sources": [
                {
                    "id": ds.id,
                    "name": ds.name,
                    "type": ds.source_type,
                    "chunks_count": ds.chunks_count,
                    "created_at": ds.created_at.isoformat()
                }
                for ds in data_sources
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


@router.post("/reindex")
async def reindex(
    current_admin: dict = Depends(get_current_admin)
):
    """???????????? ?????????? ???????"""
    try:
        # ??????? ?????????
        success = rag_service.clear_collection()
        
        if success:
            # ?????????????? ???? ??????????
            # ? ???????? ?????????? ????? ????? ?????????? ??? ????????? ?? ??
            # ? ?????? ???????? ?? ? Qdrant
            return {"message": "Index cleared successfully. Please re-ingest your data sources."}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear index")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reindexing: {str(e)}")
