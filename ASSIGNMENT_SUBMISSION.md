# Assignment Submission - Constructure AI RAG Application

## 🚀 Live Demo Links

**Frontend (Vercel):** [Add your Vercel frontend URL here]  
**Backend (ngrok tunnel):** [Add ngrok URL after starting - see below]

**GitHub Repository:** https://github.com/ishika2236/ConstructionChatbot

---

## 📌 Deployment Note

Due to free tier memory limitations on cloud hosting platforms (Render: 512MB, Vercel: 512MB), the backend requires ~400-450MB RAM which exceeds these limits. The application has been optimized with a smaller embedding model (paraphrase-MiniLM-L3-v2) but still requires more resources than available on free tiers.

**Solution for Demo:**
- ✅ Frontend deployed to Vercel (works perfectly)
- ✅ Backend running locally with ngrok public tunnel (temporary public URL)
- ✅ Full application functionality demonstrated

**For Production:** Would deploy backend on:
- Railway (with credits) or Render Paid ($7/month with 2GB RAM)
- Azure App Service (already using Azure OpenAI)
- AWS Lambda with increased memory allocation

---

## 🔧 How to Run & Test

### Backend Setup (Local + ngrok)

1. **Start Backend Server:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

2. **Expose with ngrok (in new terminal):**
```bash
ngrok http 8000
```

3. **Copy the ngrok URL** (looks like: `https://abc123.ngrok.io`)

4. **Update Frontend Environment:**
- Go to Vercel dashboard → Your Frontend Project
- Settings → Environment Variables
- Set `NEXT_PUBLIC_API_URL` to your ngrok URL
- Redeploy frontend

### Frontend Access

Visit your Vercel frontend URL and login with:
- **Email:** `testingcheckuser1234@gmail.com`

### Test Queries

Try these sample queries:
- "What is the fire rating for corridor partitions?"
- "Generate a door schedule"
- "What flooring material is specified for the lobby?"
- "List all rooms with their area and floor finish"

---

## ✨ Features Implemented

### Core Functionality
✅ PDF Document Ingestion with chunking and vector indexing  
✅ RAG-Powered Q&A with source citations  
✅ Structured Data Extraction (door schedules, room summaries)  
✅ Conversational Interface with modern UI  
✅ Source Attribution with document and page references  

### Technical Implementation
✅ Vector Search with ChromaDB and HuggingFace embeddings  
✅ Smart Chunking with metadata preservation  
✅ Evaluation Framework with quality metrics  
✅ Email-based Authentication  
✅ RESTful API with comprehensive endpoints  

---

## 🛠️ Technology Stack

**Backend:**
- FastAPI + Python 3.9
- Azure OpenAI GPT-4o
- HuggingFace paraphrase-MiniLM-L3-v2 (optimized for memory)
- LangChain for RAG pipeline
- ChromaDB for vector storage

**Frontend:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Responsive design

**Deployment:**
- Vercel (Frontend)
- Local + ngrok (Backend - due to free tier memory constraints)

---

## 📊 Design Decisions

### Memory Optimization
- Used smaller embedding model (60MB vs 400MB) to fit within hosting constraints
- Recursive character splitting with optimal chunk sizes
- Efficient document indexing and retrieval

### RAG Pipeline
- Vector search with semantic embeddings
- Top-5 retrieval with score-based ranking
- LLM-based structured extraction with regex fallback
- Hallucination control through prompt engineering

---

## 🧪 Evaluation

Run the evaluation script to test RAG quality:
```bash
cd backend
python evaluate.py
```

Results include:
- Keyword matching scores
- Source quality metrics
- Uncertainty handling assessment
- Overall quality ratings

---

## 📂 Repository Structure

```
ConstructionChatbot/
├── backend/           # FastAPI application
│   ├── main.py       # API routes
│   ├── document_processor.py
│   ├── retriever.py
│   ├── structured_extractor.py
│   └── evaluate.py
├── frontend/         # Next.js application
│   ├── app/
│   │   ├── page.tsx  # Login
│   │   └── chat/page.tsx  # Chat interface
│   └── lib/api.ts
├── documents/        # Sample PDFs
└── README.md
```

---

## 💡 Future Enhancements

- Multi-modal support (GPT-4V for drawings)
- Hybrid search (vector + BM25 keyword)
- Persistent conversation storage
- Export capabilities (Excel, CSV)
- Red-flag detection for conflicting specifications

---

## 📝 Testing Checklist

- [x] Backend API running and accessible
- [x] Frontend deployed to Vercel
- [x] Documents ingested and indexed
- [x] Q&A returning accurate answers with sources
- [x] Structured extraction working (door schedules)
- [x] Authentication functional
- [x] CORS configured correctly
- [x] Error handling implemented
- [x] Evaluation script tested

---

## 🎥 Demo Video

[Optional: Add link to demo video showing full functionality]

---

## 📧 Contact

For any questions or clarifications about the implementation:
- GitHub: https://github.com/ishika2236
- Email: [Your email]

---

## ⏱️ Development Timeline

- Core RAG implementation: ~8 hours
- Structured extraction: ~3 hours
- Frontend development: ~4 hours
- Testing & evaluation: ~2 hours
- Deployment & documentation: ~3 hours
- **Total:** ~20 hours

---

Thank you for reviewing my submission!
