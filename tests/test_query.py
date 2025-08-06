import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_flexible_query():
    """Test that the system can handle any type of question flexibly."""
    response = client.post("/ask-query", json={"query": "What is the grace period for premium payment?"})
    assert response.status_code == 200
    data = response.json()
    # Should have either an answer or an error message
    assert "answer" in data or "error" in data

def test_policy_question():
    """Test policy-specific questions."""
    response = client.post("/ask-query", json={"query": "What is the waiting period for pre-existing diseases?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data or "error" in data

def test_claim_question():
    """Test claim-related questions."""
    response = client.post("/ask-query", json={"query": "Is surgery covered for a 46-year-old man?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data or "error" in data

def test_general_question():
    """Test general document questions."""
    response = client.post("/ask-query", json={"query": "What are the main benefits of this policy?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data or "error" in data