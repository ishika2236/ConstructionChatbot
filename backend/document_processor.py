import os
import re
from typing import List, Dict, Any
from pathlib import Path
import pypdf
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from config import settings


class DocumentProcessor:
    """Handles document ingestion, chunking, and indexing"""
    
    def __init__(self):
        # Use local Hugging Face embeddings (no API key needed)
        # This uses the sentence-transformers library already in requirements
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",  # Fast and effective model
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
        )
        self.vector_store = None
        self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Initialize or load existing ChromaDB vector store"""
        persist_dir = settings.chroma_persist_dir
        
        if os.path.exists(persist_dir) and os.listdir(persist_dir):
            # Load existing vector store
            self.vector_store = Chroma(
                persist_directory=persist_dir,
                embedding_function=self.embeddings,
                collection_name="construction_docs"
            )
            print(f"Loaded existing vector store from {persist_dir}")
        else:
            # Create new vector store
            os.makedirs(persist_dir, exist_ok=True)
            self.vector_store = Chroma(
                persist_directory=persist_dir,
                embedding_function=self.embeddings,
                collection_name="construction_docs"
            )
            print(f"Created new vector store at {persist_dir}")
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract text from PDF with page numbers
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of dicts with page text and metadata
        """
        pages_data = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                for page_num in range(total_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    if text.strip():  # Only add pages with content
                        pages_data.append({
                            'text': text,
                            'page_number': page_num + 1,
                            'total_pages': total_pages
                        })
                        
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {str(e)}")
            raise
        
        return pages_data
    
    def chunk_documents(self, pages_data: List[Dict[str, Any]], file_name: str) -> List[Document]:
        """
        Chunk document pages into smaller units for better retrieval
        
        Args:
            pages_data: List of page text and metadata
            file_name: Name of the source file
            
        Returns:
            List of LangChain Document objects
        """
        documents = []
        
        for page_data in pages_data:
            # Split the page text into chunks
            chunks = self.text_splitter.split_text(page_data['text'])
            
            for chunk_idx, chunk in enumerate(chunks):
                # Create metadata for each chunk
                metadata = {
                    'source': file_name,
                    'page': page_data['page_number'],
                    'total_pages': page_data['total_pages'],
                    'chunk_index': chunk_idx,
                }
                
                # Detect if this chunk contains structured data (tables, schedules)
                if self._contains_structured_data(chunk):
                    metadata['content_type'] = 'structured'
                else:
                    metadata['content_type'] = 'text'
                
                documents.append(Document(page_content=chunk, metadata=metadata))
        
        return documents
    
    def _contains_structured_data(self, text: str) -> bool:
        """
        Heuristic to detect if text contains structured data like tables
        
        Args:
            text: Text to analyze
            
        Returns:
            True if likely contains structured data
        """
        # Look for patterns that suggest tables/schedules
        patterns = [
            r'\b(?:MARK|DOOR|TYPE|SIZE|RATING|MATERIAL)\b.*\n',  # Column headers
            r'\d+\s*[xX]\s*\d+',  # Dimensions like "900 x 2100"
            r'\b[A-Z]-?\d+\b',  # Door marks like "D-101" or "D101"
            r'\|\s*\w+\s*\|',  # Pipe-separated values
            r'\t\w+\t',  # Tab-separated values
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def ingest_documents(self, documents_dir: str) -> Dict[str, Any]:
        """
        Ingest all PDF documents from a directory
        
        Args:
            documents_dir: Directory containing PDF files
            
        Returns:
            Ingestion status dictionary
        """
        pdf_files = list(Path(documents_dir).glob("*.pdf"))
        
        if not pdf_files:
            return {
                'status': 'error',
                'message': 'No PDF files found in directory',
                'total_documents': 0,
                'processed_documents': 0,
                'total_chunks': 0
            }
        
        all_documents = []
        processed_count = 0
        
        for pdf_file in pdf_files:
            try:
                print(f"Processing {pdf_file.name}...")
                
                # Extract text from PDF
                pages_data = self.extract_text_from_pdf(str(pdf_file))
                
                # Chunk the document
                chunks = self.chunk_documents(pages_data, pdf_file.name)
                all_documents.extend(chunks)
                
                processed_count += 1
                print(f"  -> Extracted {len(chunks)} chunks")
                
            except Exception as e:
                print(f"Error processing {pdf_file.name}: {str(e)}")
                continue
        
        # Add documents to vector store
        if all_documents:
            try:
                self.vector_store.add_documents(all_documents)
                print(f"\nAdded {len(all_documents)} chunks to vector store")
            except Exception as e:
                print(f"Error adding documents to vector store: {str(e)}")
                return {
                    'status': 'error',
                    'message': f'Error indexing documents: {str(e)}',
                    'total_documents': len(pdf_files),
                    'processed_documents': processed_count,
                    'total_chunks': 0
                }
        
        return {
            'status': 'success',
            'message': 'Documents ingested successfully',
            'total_documents': len(pdf_files),
            'processed_documents': processed_count,
            'total_chunks': len(all_documents)
        }
    
    def get_vector_store(self):
        """Get the vector store instance"""
        return self.vector_store


# Global instance
document_processor = DocumentProcessor()
