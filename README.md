# Constructure AI - Applied LLM Engineer Technical Assignment

A RAG (Retrieval Augmented Generation) powered application for construction document Q&A and structured data extraction. This application ingests construction PDFs, indexes them using vector embeddings, and provides intelligent question answering with source citations, plus structured extraction capabilities (e.g., door schedules).

## 🚀 Live Demo

**Deployed URL:** [To be added after deployment]

## 📋 Features

### Core Functionality
- **Document Ingestion**: Automatic PDF parsing, chunking, and vector indexing
- **RAG-Powered Q&A**: Natural language questions about construction documents with source citations
- **Structured Extraction**: Extract door schedules, room summaries, and other structured data
- **Source Citations**: Every answer includes references to specific documents and page numbers
- **Conversational Interface**: Clean, modern chat UI built with Next.js and Tailwind CSS

### Technical Highlights
- **Hybrid Retrieval**: Vector search with ChromaDB for semantic understanding
- **Smart Chunking**: Intelligent document splitting with overlap and metadata preservation
- **Structured Data Detection**: Heuristics to identify tables and schedules in documents
- **Evaluation Framework**: Built-in testing with predefined queries and quality metrics

## 🏗️ Architecture

### Backend (FastAPI + Python)
```
backend/
├── main.py                    # FastAPI application and routes
├── config.py                  # Configuration management
├── models.py                  # Pydantic models for API
├── document_processor.py      # PDF ingestion and chunking
├── retriever.py               # RAG retrieval logic
├── structured_extractor.py    # Door schedule extraction
├── evaluate.py                # Evaluation script
└── requirements.txt           # Python dependencies
```

### Frontend (Next.js + TypeScript)
```
frontend/
├── app/
│   ├── page.tsx              # Login page
│   ├── chat/page.tsx         # Main chat interface
│   ├── layout.tsx            # Root layout
│   └── globals.css           # Global styles
├── lib/
│   └── api.ts                # API client
└── package.json              # Node dependencies
```

## 🔧 Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+
- Azure OpenAI API access with deployment endpoints

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Azure OpenAI credentials:
   ```
   AZURE_OPENAI_API_KEY=your_azure_openai_api_key
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com
   AZURE_OPENAI_DEPLOYMENT=gpt-4o
   AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   CHROMA_PERSIST_DIR=./chroma_db
   ```

5. **Ingest documents**
   
   Place your PDF documents in the project root directory, then run:
   ```bash
   python -c "from document_processor import document_processor; import os; print(document_processor.ingest_documents(os.path.dirname(os.getcwd())))"
   ```
   
   Or use the API endpoint after starting the server (see step 6).

6. **Run the backend server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   
   The API will be available at `http://localhost:8000`
   API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   ```
   
   Edit `.env.local`:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Run the development server**
   ```bash
   npm run dev
   ```
   
   The application will be available at `http://localhost:3000`

5. **Build for production**
   ```bash
   npm run build
   npm start
   ```

## 🔐 Authentication

The application uses a simple email-based authentication:
- **Authorized Email**: `testingcheckuser1234@gmail.com`
- Enter this email on the login page to access the application

## 📝 How to Use

### 1. Ingest Documents
After starting the backend, ingest documents using the API:
```bash
curl -X POST http://localhost:8000/api/ingest
```

### 2. Ask Questions
Examples of natural language queries:
- "What is the fire rating for corridor partitions?"
- "What flooring material is specified for the lobby?"
- "Are there accessibility requirements for doors?"
- "What are the typical door dimensions in the project?"

### 3. Extract Structured Data
Request structured extraction by asking:
- "Generate a door schedule"
- "List all rooms with their area and floor finish"

The system will automatically detect the intent and extract structured JSON data, displayed as a table.

## 🧪 Evaluation

Run the evaluation script to test the RAG pipeline:

```bash
cd backend
python evaluate.py
```

This will:
- Run 8 predefined test queries
- Evaluate retrieval quality and answer accuracy
- Generate a quality report with metrics
- Save results to `evaluation_results.json`

## 🎨 Design Decisions

### Document Chunking
- **Strategy**: Recursive character splitting with 1000 char chunks and 200 char overlap
- **Rationale**: Balances context preservation with retrieval precision
- **Metadata**: Each chunk includes source file, page number, and content type

### Retrieval Pipeline
- **Vector Search**: OpenAI `text-embedding-ada-002` embeddings with ChromaDB
- **Top-k**: Retrieve 5 most relevant chunks by default
- **Reranking**: Future enhancement - could add cross-encoder reranking

### Structured Extraction
- **Approach**: LLM-based extraction with JSON schema validation
- **Fallback**: Regex-based manual extraction if LLM parsing fails
- **Schema**: Flexible schema that adapts to document content

### Prompting Strategy
- **System Context**: Specialized construction assistant persona
- **Answer Format**: Concise answers with explicit source citations
- **Hallucination Control**: Instructions to admit uncertainty when lacking information

## 🚀 Deployment

### Vercel Deployment (Frontend)

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy**
   ```bash
   cd frontend
   vercel
   ```

3. **Set environment variables in Vercel dashboard**
   - `NEXT_PUBLIC_API_URL`: Your deployed backend URL

### Backend Deployment Options

**Option 1: Railway / Render**
- Push code to GitHub
- Connect repository to Railway/Render
- Set environment variables
- Deploy

**Option 2: Cloud Run / AWS Lambda**
- Containerize FastAPI app
- Deploy to serverless platform

**Option 3: Traditional VPS**
- Use systemd or supervisor to manage uvicorn
- Set up nginx reverse proxy

## 📊 API Endpoints

### Authentication
- `POST /api/auth/login` - Authenticate user

### Document Management
- `POST /api/ingest` - Ingest PDF documents
- `GET /api/status` - Get system status

### Chat & RAG
- `POST /api/chat` - Send chat message, get RAG response
- `GET /api/conversation/{id}` - Get conversation history

### Structured Extraction
- `POST /api/extract` - Extract structured data (door_schedule, room_summary)

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.109
- **LLM**: OpenAI GPT-4 Turbo
- **Embeddings**: OpenAI text-embedding-ada-002
- **Vector DB**: ChromaDB 0.4.22
- **RAG Framework**: LangChain 0.1.4

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP Client**: Axios

## 🔍 Evaluation Metrics

The evaluation script measures:
- **Keyword Score**: Presence of expected keywords in answers
- **Source Quality**: Whether sources are provided
- **Uncertainty Handling**: Ability to admit when information is not available
- **Overall Quality**: Good / Partial / Honest Unknown / Poor / Error

## 📈 Future Enhancements

- [ ] Multi-modal support (extract data from drawing images using GPT-4V)
- [ ] Hybrid search (vector + BM25 keyword search with reranking)
- [ ] Persistent conversation storage (PostgreSQL)
- [ ] Real-time collaboration
- [ ] Export capabilities (Excel, CSV)
- [ ] Red-flag detection for conflicting specifications
- [ ] Advanced analytics dashboard

## 📄 License

This project is created as part of the Constructure AI technical assessment.

## 👤 Author

Built for Constructure AI Applied LLM Engineer Technical Assignment

## 🙏 Acknowledgments

- OpenAI for GPT-4 and embeddings API
- LangChain for RAG framework
- ChromaDB for vector storage
- Vercel for frontend hosting
