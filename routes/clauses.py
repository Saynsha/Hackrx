from fastapi import APIRouter
from services.embedding_service import EmbeddingService

router = APIRouter()
embedding_service = EmbeddingService()

@router.get("/clauses/{id}")
def get_clause(id: str):
    """Return full text of clause by ID (chunk_id)."""
    try:
        chunk_id = int(id)
        for meta in embedding_service.metadata:
            if meta.get("chunk_id") == chunk_id:
                return {"text": meta.get("text", ""), "metadata": meta}
        return {"error": "Clause not found."}
    except Exception as e:
        return {"error": str(e)}

@router.get("/debug/chunks")
def list_all_chunks():
    """Debug endpoint to list all available chunks."""
    try:
        chunks = []
        for i, meta in enumerate(embedding_service.metadata):
            chunks.append({
                "chunk_id": i,
                "text_preview": meta.get("text", "")[:200] + "..." if len(meta.get("text", "")) > 200 else meta.get("text", ""),
                "metadata": meta
            })
        return {
            "total_chunks": len(chunks),
            "chunks": chunks
        }
    except Exception as e:
        return {"error": str(e)}