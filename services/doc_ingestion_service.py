"""
Service for ingesting, parsing, chunking, embedding, and indexing insurance documents.
"""
import os
import shutil
import uuid
from utils import parser_utils, text_splitter
from services.embedding_service import EmbeddingService
from utils.logging_utils import get_logger

logger = get_logger("doc_ingestion_service")

class DocIngestionService:
    def __init__(self, upload_dir="data/uploaded_docs"):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)
        self.embedding_service = EmbeddingService()

    def ingest_document(self, file_path: str):
        """Parse, chunk, embed, and index a document. Returns document UUID."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            text = parser_utils.parse_pdf(file_path)
        elif ext == ".docx":
            text = parser_utils.parse_docx(file_path)
        elif ext == ".eml":
            text = parser_utils.parse_eml(file_path)
        else:
            logger.error(f"Unsupported file type: {ext}")
            return None
        if not text:
            logger.error("No text extracted from document.")
            return None
        chunks = text_splitter.semantic_chunk(text)
        doc_id = str(uuid.uuid4())
        for i, chunk in enumerate(chunks):
            chunk["metadata"].update({
                "doc_id": doc_id,
                "filename": os.path.basename(file_path),
                "chunk_id": i
            })
        self.embedding_service.embed_chunks(chunks)
        # Save original file to uploaded_docs
        dest_path = os.path.join(self.upload_dir, f"{doc_id}_{os.path.basename(file_path)}")
        shutil.copy2(file_path, dest_path)
        logger.info(f"Document {file_path} ingested as {doc_id}")
        return doc_id