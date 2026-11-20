import uuid
from dataclasses import dataclass
from functools import lru_cache
from typing import Any
from app.core.config import get_settings

@dataclass
class Chunk:
    text: str
    source: str
    score: float = 1.0

class KnowledgeService:
    def __init__(self) -> None:
        self._fallback: list[Chunk] = []
        self._client = None
        self._model = None
        self._ready = False

    def _init(self) -> None:
        if self._ready: return
        self._ready = True
        settings = get_settings()
        try:
            from sentence_transformers import SentenceTransformer
            from qdrant_client import QdrantClient, models
            self._model = SentenceTransformer(settings.embedding_model)
            self._client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None, timeout=3)
            names = [c.name for c in self._client.get_collections().collections]
            if settings.qdrant_collection not in names:
                self._client.create_collection(collection_name=settings.qdrant_collection, vectors_config=models.VectorParams(size=self._model.get_sentence_embedding_dimension(), distance=models.Distance.COSINE))
        except Exception:
            self._client = None
            self._model = None

    @staticmethod
    def split(text: str, size: int = 700, overlap: int = 100) -> list[str]:
        text = " ".join(text.split())
        if not text: return []
        chunks=[]; start=0
        while start < len(text):
            end=min(len(text), start+size); chunks.append(text[start:end])
            if end == len(text): break
            start=max(end-overlap, start+1)
        return chunks

    def ingest(self, text: str, source: str) -> int:
        self._init(); parts=self.split(text)
        if self._client and self._model and parts:
            from qdrant_client import models
            vectors=self._model.encode(parts, normalize_embeddings=True).tolist()
            self._client.upsert(collection_name=get_settings().qdrant_collection, points=[models.PointStruct(id=str(uuid.uuid4()), vector=v, payload={"text": p, "source": source}) for p,v in zip(parts,vectors)])
        else:
            self._fallback.extend(Chunk(p, source) for p in parts)
        return len(parts)

    def search(self, query: str, limit: int | None = None) -> list[Chunk]:
        self._init(); settings=get_settings(); limit=limit or settings.rag_top_k
        if self._client and self._model:
            vector=self._model.encode(query, normalize_embeddings=True).tolist()
            hits=self._client.query_points(collection_name=settings.qdrant_collection, query=vector, limit=limit, with_payload=True).points
            return [Chunk(str(h.payload.get("text", "")), str(h.payload.get("source", "unknown")), float(h.score)) for h in hits if float(h.score) >= settings.rag_score_threshold]
        terms=set(query.lower().split())
        ranked=[]
        for chunk in self._fallback:
            overlap=len(terms & set(chunk.text.lower().split()))
            if overlap: ranked.append(Chunk(chunk.text, chunk.source, overlap/max(len(terms),1)))
        return sorted(ranked, key=lambda x:x.score, reverse=True)[:limit]

knowledge = KnowledgeService()
