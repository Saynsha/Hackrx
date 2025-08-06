# Insurance Reasoning Engine

A powerful, flexible AI-powered document analysis system that can understand and answer questions about any uploaded document using natural language processing, semantic search, and large language models.

## 🚀 Features

- **Universal Document Support**: Upload and analyze PDFs, DOCX files, and EML emails
- **Natural Language Queries**: Ask any question in plain English about your documents
- **Intelligent Retrieval**: Advanced semantic search using FAISS and HuggingFace embeddings
- **Comprehensive Responses**: Detailed answers with source references and confidence levels
- **Flexible Architecture**: Works with any type of document, not just insurance policies
- **RESTful API**: Easy-to-use FastAPI endpoints with automatic documentation
- **Production Ready**: Includes logging, error handling, and deployment configurations

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- An OpenAI API key or OpenRouter API key

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd insurance-ai-engine
```

### 2. Create a Virtual Environment (Recommended)
```bash
# On Windows
python -m venv .venv
.venv\Scripts\activate

# On macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the project root:
```env
# Choose your LLM provider
LLM_PROVIDER=openrouter  # or openai

# API Keys (get one from the provider you chose)
OPENAI_API_KEY=your_openai_key_here
OPENROUTER_API_KEY=your_openrouter_key_here

# Optional: Customize embedding model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

**Getting API Keys:**
- **OpenAI**: Visit [OpenAI Platform](https://platform.openai.com/) to get an API key
- **OpenRouter**: Visit [OpenRouter](https://openrouter.ai/) for free and paid models

## 🚀 Quick Start

### 1. Start the Server
```bash
uvicorn main:app --reload
```

The API will be available at:
- **API**: http://127.0.0.1:8000
- **Interactive Docs**: http://127.0.0.1:8000/docs

### 2. Upload a Document
Use the `/upload-docs` endpoint to upload your first document:
- Go to http://127.0.0.1:8000/docs
- Click on `POST /upload-docs`
- Click "Try it out"
- Upload a PDF, DOCX, or EML file
- You'll receive a `doc_id` upon successful upload

### 3. Ask Questions
Use the `/ask-query` endpoint to ask questions about your document:
```json
{
  "query": "What is the grace period for premium payment?"
}
```

## 📚 API Endpoints

### `POST /upload-docs`
Upload and index a document for analysis.

**Request:**
- Content-Type: `multipart/form-data`
- Body: File upload (PDF, DOCX, EML)

**Response:**
```json
{
  "doc_id": "f4c532bd-88b4-4de1-bdf1-ea64b50771ad"
}
```

### `POST /ask-query`
Ask any question about uploaded documents.

**Request:**
```json
{
  "query": "What is the waiting period for pre-existing diseases?"
}
```

**Response:**
```json
{
  "answer": "Comprehensive answer with full context and explanations...",
  "confidence": "high",
  "source_sections": [
    {
      "section": "Section 3.2",
      "content": "Relevant text from the document...",
      "relevance": "Detailed explanation of why this section is relevant..."
    }
  ],
  "additional_info": "Additional context, practical implications, and helpful guidance..."
}
```

### `GET /clauses/{id}`
Retrieve the full text of a specific document chunk.

### `GET /debug/chunks`
List all available document chunks (for debugging).

### `GET /health`
Health check endpoint.

## 💡 Usage Examples

### Insurance Policy Analysis
```json
{
  "query": "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?"
}
```

### General Document Questions
```json
{
  "query": "What are the main benefits of this policy?"
}
```

### Specific Coverage Questions
```json
{
  "query": "Does this policy cover maternity expenses, and what are the conditions?"
}
```

### Claim Process Questions
```json
{
  "query": "How do I file a claim and what documents do I need?"
}
```

## 🏗️ Project Structure

```
insurance-ai-engine/
├── main.py                 # FastAPI application entry point
├── asgi.py                 # ASGI entry point for deployment
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── vercel.json            # Vercel deployment configuration
├── README.md              # This file
│
├── routes/                 # API route handlers
│   ├── upload.py          # Document upload endpoint
│   ├── query.py           # Query processing endpoint
│   └── clauses.py         # Clause retrieval endpoint
│
├── services/              # Core business logic
│   ├── doc_ingestion_service.py    # Document processing
│   ├── embedding_service.py        # Embedding generation and FAISS
│   └── query_reasoning_service.py  # Query analysis and LLM integration
│
├── utils/                 # Utility functions
│   ├── parser_utils.py    # Document parsing (PDF, DOCX, EML)
│   ├── text_splitter.py   # Semantic text chunking
│   ├── prompt_templates.py # LLM prompt templates
│   └── logging_utils.py   # Logging configuration
│
├── data/                  # Data storage
│   ├── uploaded_docs/     # Original uploaded files
│   └── faiss_index/       # FAISS vector index and metadata
│
└── tests/                 # Test files
    ├── test_upload.py
    ├── test_query.py
    └── test_embeddings.py
```

## 🔧 Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | Choose between 'openai' or 'openrouter' | 'openrouter' |
| `OPENAI_API_KEY` | Your OpenAI API key | Required if using OpenAI |
| `OPENROUTER_API_KEY` | Your OpenRouter API key | Required if using OpenRouter |
| `EMBEDDING_MODEL` | HuggingFace embedding model | 'sentence-transformers/all-MiniLM-L6-v2' |

### Customization Options
- **Chunk Size**: Modify `chunk_size` in `utils/text_splitter.py`
- **Retrieval Count**: Adjust `top_k` in `services/query_reasoning_service.py`
- **LLM Model**: Change the model in the `_call_llm` method

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

## 🚀 Deployment

### Local Development
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Vercel Deployment
1. Install Vercel CLI: `npm i -g vercel`
2. Deploy: `vercel --prod`

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔍 Troubleshooting

### Common Issues

**1. "No relevant information found"**
- Check if the document was uploaded successfully
- Try rephrasing your question with different keywords
- Use `/debug/chunks` to see available content
- Ensure the document contains the information you're asking about

**2. API Key Errors**
- Verify your API key is correct in `.env`
- Check if you have sufficient credits/quota
- Ensure the LLM provider is set correctly

**3. Document Upload Fails**
- Check file format (PDF, DOCX, EML only)
- Ensure file is not corrupted
- Check server logs for specific error messages

**4. Poor Response Quality**
- Try asking more specific questions
- Check if the document contains relevant information
- Consider using a better LLM model

### Debug Endpoints
- `/debug/chunks`: List all available document chunks
- `/health`: Check system status
- Server logs: Check terminal output for detailed information

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review server logs for error messages
3. Test with the debug endpoints
4. Open an issue with detailed information about the problem

## 🎯 Use Cases

This system is perfect for:
- **Insurance Companies**: Analyze policies and answer customer questions
- **Legal Firms**: Review contracts and legal documents
- **Healthcare**: Process medical policies and procedures
- **Education**: Analyze textbooks and educational materials
- **Business**: Review company policies and procedures
- **Research**: Analyze research papers and reports

The system is designed to be flexible and can work with any type of document where you need to extract and understand information through natural language queries. 