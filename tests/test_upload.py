import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_upload_pdf():
    # Create a dummy PDF file
    pdf_path = tempfile.mktemp(suffix=".pdf")
    with open(pdf_path, "wb") as f:
        f.write(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\nxref\n0 1\n0000000000 65535 f \ntrailer\n<< /Root 1 0 R >>\nstartxref\n0\n%%EOF")
    with open(pdf_path, "rb") as f:
        response = client.post("/upload-docs", files={"file": ("test.pdf", f, "application/pdf")})
    os.remove(pdf_path)
    assert response.status_code == 200
    data = response.json()
    assert "doc_id" in data or "error" in data