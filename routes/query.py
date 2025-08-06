from fastapi import APIRouter, Body
from services.query_reasoning_service import QueryReasoningService

router = APIRouter()
query_service = QueryReasoningService()

@router.post("/ask-query")
def ask_query(query: str = Body(..., embed=True)):
    """Accepts a natural language query and returns structured JSON decision."""
    result = query_service.answer_query(query)
    return result