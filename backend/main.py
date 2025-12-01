from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import uuid
from datetime import datetime

from models import (
    AuthRequest, AuthResponse, ChatRequest, ChatResponse,
    StructuredExtractionRequest, StructuredExtractionResponse,
    IngestionStatus
)
from document_processor import document_processor
from retriever import rag_retriever
from structured_extractor import structured_extractor
from config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Constructure AI - RAG API",
    description="API for construction document Q&A and structured extraction",
    version="1.0.0"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Vercel domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory conversation storage (in production, use a database)
conversations: Dict[str, list] = {}

# Authorized user email
AUTHORIZED_EMAIL = "testingcheckuser1234@gmail.com"


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Constructure AI RAG API is running",
        "version": "1.0.0"
    }


@app.post("/api/auth/login", response_model=AuthResponse)
async def login(auth_request: AuthRequest):
    """
    Authenticate user
    
    Only allows testingcheckuser1234@gmail.com
    """
    if auth_request.email.lower() == AUTHORIZED_EMAIL.lower():
        return AuthResponse(
            success=True,
            message="Authentication successful",
            user_email=auth_request.email
        )
    else:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized email address"
        )


@app.post("/api/ingest", response_model=IngestionStatus)
async def ingest_documents():
    """
    Ingest documents from the documents directory
    
    This should be called once to index all PDF documents
    """
    try:
        # Ingest documents from parent directory
        import os
        documents_dir = os.path.join(os.path.dirname(__file__), "..")
        
        status = document_processor.ingest_documents(documents_dir)
        
        return IngestionStatus(**status)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error ingesting documents: {str(e)}"
        )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest):
    """
    Handle chat requests with RAG
    
    Supports both Q&A and structured extraction
    """
    try:
        # Get or create conversation
        conversation_id = chat_request.conversation_id or str(uuid.uuid4())
        
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        
        # Add user message to conversation
        conversations[conversation_id].append({
            'role': 'user',
            'content': chat_request.message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Check if this is a structured extraction request
        is_extraction, extraction_type = rag_retriever.detect_extraction_intent(
            chat_request.message
        )
        
        if is_extraction:
            # Handle structured extraction
            if extraction_type == 'door_schedule':
                extracted_data, sources = structured_extractor.extract_door_schedule()
                
                if extracted_data:
                    response_message = f"I found {len(extracted_data)} doors in the construction documents. The door schedule is displayed below."
                else:
                    response_message = "I couldn't find any door schedule information in the documents. This might be because the documents don't contain door schedules or the format is not recognized."
                
                response = ChatResponse(
                    message=response_message,
                    sources=sources,
                    conversation_id=conversation_id,
                    is_structured_extraction=True,
                    structured_data=extracted_data
                )
            
            elif extraction_type == 'room_summary':
                extracted_data, sources = structured_extractor.extract_room_summary()
                
                if extracted_data:
                    response_message = f"I found {len(extracted_data)} rooms in the construction documents."
                else:
                    response_message = "I couldn't find room summary information in the documents."
                
                response = ChatResponse(
                    message=response_message,
                    sources=sources,
                    conversation_id=conversation_id,
                    is_structured_extraction=True,
                    structured_data=extracted_data
                )
            
            else:
                response_message = f"Structured extraction for '{extraction_type}' is not yet implemented."
                response = ChatResponse(
                    message=response_message,
                    sources=[],
                    conversation_id=conversation_id,
                    is_structured_extraction=False
                )
        
        else:
            # Handle regular Q&A
            answer, sources = rag_retriever.answer_question(chat_request.message)
            
            response = ChatResponse(
                message=answer,
                sources=sources,
                conversation_id=conversation_id,
                is_structured_extraction=False
            )
        
        # Add assistant response to conversation
        conversations[conversation_id].append({
            'role': 'assistant',
            'content': response.message,
            'timestamp': datetime.now().isoformat(),
            'sources': response.sources
        })
        
        return response
    
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )


@app.get("/api/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history"""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {
        "conversation_id": conversation_id,
        "messages": conversations[conversation_id]
    }


@app.post("/api/extract", response_model=StructuredExtractionResponse)
async def extract_structured_data(request: StructuredExtractionRequest):
    """
    Extract structured data from documents
    
    Supports: door_schedule, room_summary, equipment_list
    """
    try:
        if request.extraction_type == 'door_schedule':
            extracted_data, sources = structured_extractor.extract_door_schedule()
        elif request.extraction_type == 'room_summary':
            extracted_data, sources = structured_extractor.extract_room_summary()
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported extraction type: {request.extraction_type}"
            )
        
        return StructuredExtractionResponse(
            extraction_type=request.extraction_type,
            data=extracted_data,
            sources=sources
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting structured data: {str(e)}"
        )


@app.get("/api/status")
async def get_status():
    """Get system status"""
    vector_store = document_processor.get_vector_store()
    
    try:
        # Try to get collection info
        collection = vector_store._collection
        doc_count = collection.count()
    except:
        doc_count = 0
    
    return {
        "status": "operational",
        "documents_indexed": doc_count,
        "conversations_active": len(conversations)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
