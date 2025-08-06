"""
Insurance Reasoning Engine - Quickstart

1. Install dependencies:
   pip install -r requirements.txt

2. Set up .env with your OpenAI or OpenRouter API key.

3. Run the API locally:
   uvicorn main:app --reload

4. Endpoints:
   - POST /upload-docs: Upload and index insurance documents (PDF, DOCX, EML)
   - POST /ask-query: Ask a natural language query about coverage
   - GET /clauses/{id}: Retrieve full text of a clause by chunk_id
   - GET /health: Healthcheck

5. Run tests:
   pytest tests/

6. Deploy to Vercel: vercel --prod
"""
from fastapi import FastAPI
from routes import upload, query, clauses

app = FastAPI(title="Insurance Reasoning Engine")

# Include routers
app.include_router(upload.router)
app.include_router(query.router)
app.include_router(clauses.router)

@app.get("/health")
def healthcheck():
    """Healthcheck endpoint."""
    return {"status": "ok"}

# TODO: Add startup/shutdown events for FAISS index, model loading, etc.