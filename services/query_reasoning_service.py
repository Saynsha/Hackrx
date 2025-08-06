"""
Flexible service for natural language document analysis and question answering.
"""
import os
import json
import numpy as np
from services.embedding_service import EmbeddingService
from utils.prompt_templates import FLEXIBLE_QUERY_PROMPT
from utils.logging_utils import get_logger
import openai
import httpx
from dotenv import load_dotenv

logger = get_logger("query_reasoning_service")
load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class QueryReasoningService:
    def __init__(self, top_k=12):  # Increased from 8 to 12 for more comprehensive coverage
        self.embedding_service = EmbeddingService()
        self.top_k = top_k

    def _call_llm(self, prompt, model="gpt-3.5-turbo"):
        """Call the LLM with the given prompt."""
        try:
            if LLM_PROVIDER == "openai":
                openai.api_key = OPENAI_API_KEY
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,  # Slightly higher for more natural responses
                )
                return response.choices[0].message["content"]
            else:
                headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
                data = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                }
                url = "https://openrouter.ai/api/v1/chat/completions"
                with httpx.Client(timeout=60) as client:
                    resp = client.post(url, headers=headers, json=data)
                    resp.raise_for_status()
                    return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return None

    def _retrieve_relevant_content(self, query: str, k=None):
        """Retrieve relevant document chunks for the query."""
        if k is None:
            k = self.top_k
            
        try:
            logger.info(f"Starting retrieval for query: '{query}'")
            logger.info(f"FAISS index exists: {self.embedding_service.index is not None}")
            logger.info(f"Total metadata entries: {len(self.embedding_service.metadata)}")
            
            # Semantic retrieval using embeddings
            query_emb = self.embedding_service.model.encode([query])
            logger.info(f"Query embedding shape: {query_emb.shape}")
            
            if self.embedding_service.index is None:
                logger.error("FAISS index not loaded.")
                return []
                
            D, I = self.embedding_service.index.search(
                np.array(query_emb, dtype=np.float32), k
            )
            logger.info(f"FAISS search results - Distances: {D[0]}, Indices: {I[0]}")
            
            results = []
            for idx in I[0]:
                if idx < len(self.embedding_service.metadata):
                    meta = self.embedding_service.metadata[idx]
                    chunk_text = meta.get("text", "")
                    if chunk_text.strip():  # Only include non-empty chunks
                        results.append({
                            "text": chunk_text,
                            "metadata": meta,
                            "relevance_score": float(D[0][list(I[0]).index(idx)]) if idx in I[0] else 0.0
                        })
                        logger.info(f"Added chunk {idx} with text preview: {chunk_text[:100]}...")
                    else:
                        logger.warning(f"Chunk {idx} has empty text")
                else:
                    logger.warning(f"Index {idx} out of bounds for metadata")
            
            # Sort by relevance (lower distance = higher relevance)
            results.sort(key=lambda x: x["relevance_score"])
            
            logger.info(f"Retrieved {len(results)} relevant chunks for query")
            return results
            
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return []

    def answer_query(self, query: str):
        """
        Answer any natural language question about the uploaded document.
        This is a completely flexible system that can handle any type of question.
        """
        try:
            # Step 1: Retrieve relevant document content
            relevant_chunks = self._retrieve_relevant_content(query)
            
            if not relevant_chunks:
                return {
                    "answer": "I could not find any relevant information in the uploaded documents to answer your question. This could be due to several reasons: 1) The document may not contain information about this specific topic, 2) The information might be in a different section that wasn't retrieved, 3) The document might need to be re-uploaded or processed differently, or 4) The question might be too specific for the available content.",
                    "confidence": "low",
                    "source_sections": [],
                    "additional_info": "Here are some suggestions to help: 1) Try rephrasing your question with different keywords or terms, 2) Ask a more general question about the document first to see what information is available, 3) Check if you have uploaded the correct document that should contain this information, 4) Consider uploading additional documents if this information might be in a different file, 5) If this is about a specific policy term, try asking about related terms or broader categories. You can also use the /debug/chunks endpoint to see what content is actually available in the uploaded document."
                }
            
            # Step 2: Prepare document content for analysis
            document_content = "\n\n---\n\n".join([
                f"Section {chunk['metadata'].get('chunk_id', '?')}:\n{chunk['text']}"
                for chunk in relevant_chunks
            ])
            
            # Step 3: Build the analysis prompt
            analysis_prompt = f"""
{FLEXIBLE_QUERY_PROMPT}

User Question: {query}

Document Content:
{document_content}

Please analyze the document content and provide a comprehensive, detailed answer to the user's question. Remember to be extremely thorough and provide maximum context and explanation.
"""
            
            # Step 4: Get LLM response
            llm_response = self._call_llm(analysis_prompt)
            
            if not llm_response:
                return {
                    "answer": "I apologize, but I encountered an error while processing your question. This could be due to a temporary issue with the language model service, network connectivity problems, or an issue with the API configuration.",
                    "confidence": "low",
                    "source_sections": [],
                    "additional_info": "Here are some steps you can try: 1) Wait a moment and try your question again, 2) Check if your API keys are properly configured in the .env file, 3) Verify that you have sufficient API credits or quota remaining, 4) Try asking a simpler question first to test the system, 5) If the problem persists, you may need to restart the server or check the server logs for more detailed error information. The system is designed to be robust, so temporary issues usually resolve quickly."
                }
            
            # Step 5: Parse the response
            try:
                result = json.loads(llm_response)
                
                # Validate response structure and enhance if needed
                if "answer" not in result:
                    result = {
                        "answer": f"The system processed your question but returned an unexpected format. Here's what was found: {llm_response}",
                        "confidence": "medium",
                        "source_sections": [],
                        "additional_info": "The response format was not as expected, but the system did process your query. This might indicate that the language model returned a different format than anticipated. The answer above contains the raw response from the analysis. If this doesn't fully address your question, try rephrasing it or asking a more specific question."
                    }
                
                # Enhance the response with additional context if it's too brief
                if len(result.get("answer", "")) < 100:
                    result["additional_info"] = result.get("additional_info", "") + " Note: The answer provided is quite brief. This might indicate that the specific information you're looking for is not extensively covered in the document, or it might be mentioned only in passing. Consider asking follow-up questions or checking related topics in the document."
                
                return result
                
            except json.JSONDecodeError:
                # If LLM didn't return valid JSON, wrap the response with detailed explanation
                return {
                    "answer": f"The system analyzed your question and found relevant information, but encountered a formatting issue. Here's the analysis result: {llm_response}",
                    "confidence": "medium",
                    "source_sections": [],
                    "additional_info": "The language model provided an answer but it wasn't in the expected JSON format. This sometimes happens when the model provides a natural language response instead of structured data. The answer above contains the raw response from the analysis. While this might not be as structured as usual, it should still contain relevant information to help answer your question. If you need more specific details, try asking follow-up questions or rephrasing your original question."
                }
                
        except Exception as e:
            logger.error(f"Error in answer_query: {e}")
            return {
                "answer": f"An unexpected error occurred while processing your question: {str(e)}. This is not typical and indicates a system issue that needs attention.",
                "confidence": "low",
                "source_sections": [],
                "additional_info": "This error suggests there might be an issue with the system configuration, the document processing, or the language model service. Here are some troubleshooting steps: 1) Check if the document was properly uploaded and processed, 2) Verify that all required services are running correctly, 3) Check the server logs for more detailed error information, 4) Try restarting the server, 5) If the problem persists, there might be an issue with the API configuration or the language model service. Please try again, and if the issue continues, consider checking the system logs or contacting support."
            }