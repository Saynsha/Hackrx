"""
Service for generating embeddings and managing FAISS index.
"""
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import pickle
from utils.logging_utils import get_logger

logger = get_logger("embedding_service")

class EmbeddingService:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2", index_path="data/faiss_index/index.bin", meta_path="data/faiss_index/meta.pkl"):
        self.model = SentenceTransformer(model_name)
        self.index_path = index_path
        self.meta_path = meta_path
        self.index = None
        self.metadata = []  # List of dicts, one per chunk
        self.load_index()

    def embed_chunks(self, chunks):
        """Generate embeddings for a list of text chunks. Each chunk is a dict with 'text' and 'metadata'."""
        texts = [c["text"] for c in chunks]
        embeddings = self.model.encode(texts, show_progress_bar=False)
        if self.index is None:
            self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(np.array(embeddings, dtype=np.float32))
        self.metadata.extend([c["metadata"] for c in chunks])
        self.save_index()
        return embeddings

    def save_index(self):
        """Persist FAISS index and metadata to disk."""
        if self.index is not None:
            faiss.write_index(self.index, self.index_path)
            with open(self.meta_path, "wb") as f:
                pickle.dump(self.metadata, f)
            logger.info("FAISS index and metadata saved.")

    def load_index(self):
        """Load FAISS index and metadata from disk."""
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            if os.path.exists(self.meta_path):
                with open(self.meta_path, "rb") as f:
                    self.metadata = pickle.load(f)
            logger.info("FAISS index and metadata loaded.")
        else:
            self.index = None
            self.metadata = []