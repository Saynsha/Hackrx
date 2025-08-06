from services.embedding_service import EmbeddingService

def test_embeddings_stub():
    service = EmbeddingService()
    # Should have index loaded or empty
    assert service.index is not None or service.metadata == []