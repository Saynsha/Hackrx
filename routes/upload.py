from fastapi import APIRouter, UploadFile, File
import os
import tempfile
from services.doc_ingestion_service import DocIngestionService

router = APIRouter()
doc_service = DocIngestionService()

@router.post("/upload-docs")
def upload_docs(file: UploadFile = File(...)):
    """Upload and index insurance documents (PDF, DOCX, EML)."""
    # Save uploaded file to temp location
    try:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name
        doc_id = doc_service.ingest_document(tmp_path)
        os.remove(tmp_path)
        if doc_id:
            return {"doc_id": doc_id}
        else:
            return {"error": "Failed to ingest document."}
    except Exception as e:
        return {"error": str(e)}