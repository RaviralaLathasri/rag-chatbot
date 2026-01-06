# RAG Chatbot with OpenRouter Meta LLaMA

A complete Retrieval-Augmented Generation (RAG) chatbot that answers questions strictly from uploaded documents using Meta LLaMA via OpenRouter API.

## Features

- 📄 Upload PDF or TXT documents
- 🧠 Automatic text extraction and chunking
- 💾 JSON-based knowledge base
- 🤖 Uses Meta LLaMA (free tier) via OpenRouter
- ✅ Strict RAG - only answers from document content
- 🚫 No hallucination - refuses to answer when information not found
- 💬 Clean ChatGPT-style interface

## Project Structure

```
rag-chatbot/
├── backend/
│   ├── app.py                 # Flask API server
│   ├── document_processor.py  # Text extraction & chunking
│   ├── rag_engine.py          # RAG logic with OpenRouter
│   ├── requirements.txt       # Python dependencies
│   ├── knowledge_base/        # Stores JSON knowledge bases
│   └── uploads/               # Temporary file storage
├── frontend/
│   ├── index.html             # Main UI
│   ├── style.css              # Styling
│   └── script.js              # Frontend logic
├── .env                       # Environment variables (create this)
├── .env.example               # Example environment file
└── README.md                  # This file
```

## Prerequisites

- Python 3.8+
- OpenRouter API Key (free tier available)
- Modern web browser

## Setup Instructions

### 1. Get OpenRouter API Key

1. Go to https://openrouter.ai/
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key

### 2. Clone/Download Project

```bash
# Create project directory
mkdir rag-chatbot
cd rag-chatbot

# Create backend and frontend folders
mkdir -p backend/knowledge_base backend/uploads
mkdir frontend
```

### 3. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Create .env file in backend directory
cp .env.example .env

# Edit .env and add your OpenRouter API key
# OPENROUTER_API_KEY=your_actual_api_key_here
```

On Windows:
```bash
echo OPENROUTER_API_KEY=your_actual_api_key_here > .env
```

On Mac/Linux:
```bash
echo "OPENROUTER_API_KEY=your_actual_api_key_here" > .env
```

### 5. Start Backend Server

```bash
cd backend
python app.py
```

The backend should start on `http://localhost:5000`

### 6. Start Frontend

Open a new terminal:

```bash
cd frontend
python -m http.server 8000
```

Or use any other static file server.

### 7. Access Application

Open your browser and navigate to:
```
http://localhost:8000
```

## Usage

1. **Upload Document**
   - Click "Choose File"
   - Select a PDF or TXT file (max 16MB)
   - Click "Upload & Process"
   - Wait for processing to complete

2. **Ask Questions**
   - Type your question in the input box
   - Press Enter or click "Send"
   - Get answers based strictly on document content

3. **Upload New Document**
   - Click "Upload New Document"
   - Confirm to clear current chat
   - Upload a new file

## RAG Prompt Used

The system uses the following strict RAG prompt:

```
System Prompt:
You are a helpful assistant that answers questions strictly based on the provided document content.

CRITICAL RULES:
1. Answer ONLY using information from the context provided below
2. If the answer is not in the context, you MUST respond with: "I don't have enough information in the provided data to answer that."
3. Do NOT use any external knowledge
4. Do NOT make assumptions or inferences beyond what is explicitly stated
5. Be concise and accurate
6. If you're unsure, say you don't have enough information

User Prompt:
Context from the document:
{context}

Question: {query}

Answer based ONLY on the context above. If the information is not in the context, respond with: "I don't have enough information in the provided data to answer that."
```

## API Endpoints

### Backend API

- `GET /health` - Health check
- `POST /upload` - Upload and process document
- `POST /chat` - Send message and get response
- `POST /reset` - Reset knowledge base
- `GET /status` - Check if document is loaded

## Technical Details

### Document Processing
- **Chunk Size**: 500 words
- **Chunk Overlap**: 50 words
- **Retrieval Method**: Keyword-based scoring
- **Top K Chunks**: 3 most relevant chunks

### LLM Configuration
- **Model**: meta-llama/llama-3.2-3b-instruct:free
- **Temperature**: 0.1 (low for factual responses)
- **Max Tokens**: 500

### Supported File Types
- PDF (.pdf)
- Plain Text (.txt)

## Troubleshooting

### Backend won't start
- Check if Python 3.8+ is installed: `python --version`
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check if port 5000 is available

### Upload fails
- Ensure file is PDF or TXT
- Check file size is under 16MB
- Verify backend is running

### No API response
- Check OpenRouter API key is correct in `.env`
- Verify backend terminal for errors
- Check internet connection

### CORS errors
- Ensure `flask-cors` is installed
- Backend must be running on port 5000
- Frontend must be on port 8000 (or update API_BASE_URL in script.js)

## Customization

### Change chunk size
Edit `document_processor.py`:
```python
def __init__(self, chunk_size=500, chunk_overlap=50):
```

### Change LLM model
Edit `rag_engine.py`:
```python
self.model = "meta-llama/llama-3.2-3b-instruct:free"
```

### Change retrieval count
Edit `rag_engine.py`:
```python
def retrieve_relevant_chunks(self, query, knowledge_base, top_k=3):
```

## License

MIT License - Free to use and modify

## Support

For issues or questions:
1. Check console logs (browser and backend terminal)
2. Verify API key is valid
3. Ensure all dependencies are installed
4. Check file format and size

## Notes

- Free tier OpenRouter has rate limits
- First request may be slower (cold start)
- Large PDFs may take time to process
- Knowledge base is stored in memory per session
