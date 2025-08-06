"""
Utilities for semantic chunking of text using LangChain's RecursiveCharacterTextSplitter.
"""
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .logging_utils import get_logger

logger = get_logger("text_splitter")

def extract_document_info(text):
    """Extract any available document structure information."""
    info = {}
    
    # Look for any section-like patterns (flexible)
    section_patterns = [
        r'(Section|Clause|Article|Part)\s*(\d+[\.\d]*)[:\s]+(.+)',
        r'(\d+[\.\d]*)\s*[:\s]+(.+)',
        r'([A-Z][A-Z\s]+)[:\s]+(.+)'
    ]
    
    for pattern in section_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            info['section_type'] = matches[0][0] if len(matches[0]) > 2 else 'Section'
            info['section_number'] = matches[0][1] if len(matches[0]) > 2 else matches[0][0]
            info['section_title'] = matches[0][-1].strip()
            break
    
    # Extract any numbers, dates, percentages that might be important
    numbers = re.findall(r'\d+[\.\d]*%?', text)
    if numbers:
        info['numbers'] = numbers[:5]  # Limit to first 5 numbers
    
    # Extract any currency amounts
    currency = re.findall(r'₹\s*\d+[,\d]*|\$\s*\d+[,\d]*|Rs\.?\s*\d+[,\d]*', text)
    if currency:
        info['currency_amounts'] = currency[:3]  # Limit to first 3 amounts
    
    return info

def semantic_chunk(text: str, chunk_size: int = 600, chunk_overlap: int = 100):
    """Split text into semantically meaningful chunks with flexible metadata."""
    try:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", "!", "?", " "]
        )
        chunks = splitter.create_documents([text])
        
        # Process each chunk to add flexible metadata
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_text = chunk.page_content
            doc_info = extract_document_info(chunk_text)
            
            # Combine existing metadata with document info
            metadata = chunk.metadata.copy()
            metadata.update(doc_info)
            metadata['chunk_id'] = i
            metadata['text'] = chunk_text  # Store text in metadata for retrieval
            metadata['length'] = len(chunk_text)
            
            processed_chunks.append({
                "text": chunk_text,
                "metadata": metadata
            })
        
        logger.info(f"Created {len(processed_chunks)} flexible chunks")
        return processed_chunks
        
    except Exception as e:
        logger.error(f"Failed to chunk text: {e}")
        return []