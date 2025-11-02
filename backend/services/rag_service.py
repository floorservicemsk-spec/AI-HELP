from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import logging
import hashlib
from config import settings
from services.logging_config import logger


class RAGService:
    def __init__(self):
        self.qdrant_client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            grpc_port=settings.qdrant_grpc_port
        )
        self.embedding_model = SentenceTransformer(settings.embedding_model)
        self.collection_name = "knowledge_base"
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Создать коллекцию в Qdrant, если её нет"""
        try:
            collections = self.qdrant_client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_model.get_sentence_embedding_dimension(),
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error ensuring collection: {e}")
            raise
    
    def add_chunks(self, chunks: List[Dict[str, any]], batch_id: Optional[str] = None):
        """Добавить чанки в векторное хранилище"""
        if not chunks:
            return
        
        points = []
        for idx, chunk in enumerate(chunks):
            # ?Генерируем эмбеддинг для текста
            text = chunk.get("text", "")
            if not text:
                continue
            embedding = self.embedding_model.encode(text).tolist()
            
            # ?Используем хеш для point_id для уникальности (Qdrant требует числовой ID)
            point_id_str = f"{batch_id}_{idx}_{text[:50]}" if batch_id else f"{idx}_{text[:50]}"
            point_id = int(hashlib.md5(point_id_str.encode()).hexdigest()[:8], 16)
            
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "text": text,
                    "source": chunk.get("source", ""),
                    "metadata": chunk.get("metadata", {})
                }
            )
            points.append(point)
        
        # Вставляем точки батчами
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=batch
            )
        
        logger.info(f"Added {len(chunks)} chunks to Qdrant")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Поиск релевантных чанков по запросу"""
        # ?Генерируем эмбеддинг для текста?
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Поиск в Qdrant
        results = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k
        )
        
        # Форматируем результаты
        relevant_chunks = []
        for result in results:
            relevant_chunks.append({
                "text": result.payload.get("text", ""),
                "source": result.payload.get("source", ""),
                "metadata": result.payload.get("metadata", {}),
                "score": result.score
            })
        
        return relevant_chunks
    
    def clear_collection(self):
        """Очистить коллекцию"""
        try:
            self.qdrant_client.delete_collection(self.collection_name)
            self._ensure_collection()
            logger.info(f"Cleared collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            return False
    
    def get_collection_info(self) -> Dict:
        """Очистить коллекцию? ? ?????????"""
        try:
            info = self.qdrant_client.get_collection(self.collection_name)
            return {
                "points_count": info.points_count,
                "vectors_count": info.vectors_count
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {"points_count": 0, "vectors_count": 0}
