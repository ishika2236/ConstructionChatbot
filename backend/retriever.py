from typing import List, Dict, Any, Tuple
from langchain_openai import AzureChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from config import settings
from document_processor import document_processor


class RAGRetriever:
    """Handles retrieval-augmented generation for Q&A"""
    
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            azure_deployment=settings.azure_openai_deployment,
            openai_api_version=settings.azure_openai_api_version,
            temperature=0.1,
        )
        
        # Custom prompt template for construction Q&A
        self.qa_prompt_template = """You are an AI assistant specialized in construction project documentation. 
You help users understand specifications, drawings, schedules, and other construction documents.

Use the following pieces of context from construction documents to answer the question at the end.
If you don't know the answer based on the context provided, say so clearly - do not make up information.
Always cite which document and page your information comes from.

Context:
{context}

Question: {question}

Provide a clear, concise answer with citations to specific documents and pages:
Answer:"""

        self.qa_prompt = PromptTemplate(
            template=self.qa_prompt_template,
            input_variables=["context", "question"]
        )
    
    def retrieve_documents(self, query: str, k: int = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: User query
            k: Number of documents to retrieve (default from settings)
            
        Returns:
            List of document dictionaries with content and metadata
        """
        if k is None:
            k = settings.max_retrieval_docs
        
        vector_store = document_processor.get_vector_store()
        
        if not vector_store:
            return []
        
        # Retrieve documents with scores
        docs_and_scores = vector_store.similarity_search_with_score(query, k=k)
        
        # Format results
        results = []
        for doc, score in docs_and_scores:
            results.append({
                'content': doc.page_content,
                'source': doc.metadata.get('source', 'Unknown'),
                'page': doc.metadata.get('page', None),
                'content_type': doc.metadata.get('content_type', 'text'),
                'score': float(score),
            })
        
        return results
    
    def answer_question(self, question: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Answer a question using RAG
        
        Args:
            question: User question
            
        Returns:
            Tuple of (answer, source_documents)
        """
        # Retrieve relevant documents
        retrieved_docs = self.retrieve_documents(question)
        
        if not retrieved_docs:
            return ("I don't have any relevant documents to answer this question. "
                   "Please make sure documents have been ingested.", [])
        
        # Build context from retrieved documents
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            context_parts.append(
                f"[Document {i}: {doc['source']}, Page {doc['page']}]\n{doc['content']}"
            )
        context = "\n\n".join(context_parts)
        
        # Generate answer using LLM
        formatted_prompt = self.qa_prompt.format(context=context, question=question)
        
        try:
            response = self.llm.invoke(formatted_prompt)
            answer = response.content
        except Exception as e:
            answer = f"Error generating answer: {str(e)}"
        
        # Format sources for response
        sources = []
        for doc in retrieved_docs:
            sources.append({
                'file_name': doc['source'],
                'page_number': doc['page'],
                'content_snippet': doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content'],
                'score': doc['score']
            })
        
        return answer, sources
    
    def detect_extraction_intent(self, query: str) -> Tuple[bool, str]:
        """
        Detect if user wants structured extraction
        
        Args:
            query: User query
            
        Returns:
            Tuple of (is_extraction_request, extraction_type)
        """
        query_lower = query.lower()
        
        # Check for door schedule extraction
        if any(keyword in query_lower for keyword in ['door schedule', 'door table', 'list doors', 'generate door']):
            return True, 'door_schedule'
        
        # Check for room summary extraction
        if any(keyword in query_lower for keyword in ['room summary', 'room list', 'list rooms', 'room schedule']):
            return True, 'room_summary'
        
        # Check for equipment extraction
        if any(keyword in query_lower for keyword in ['equipment list', 'equipment schedule', 'mep equipment']):
            return True, 'equipment_list'
        
        return False, None


# Global instance
rag_retriever = RAGRetriever()
