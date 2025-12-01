"""
Script to manually ingest documents into the vector store
Run this after setting up the environment and before starting the server
"""

import os
import sys
from document_processor import document_processor


def main():
    print("=" * 80)
    print("DOCUMENT INGESTION SCRIPT")
    print("=" * 80)
    print()
    
    # Get the parent directory (project root)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    documents_dir = os.path.join(project_root, 'documents')
    
    print(f"Looking for PDF documents in: {documents_dir}")
    print()
    
    # Check if documents directory exists
    if not os.path.exists(documents_dir):
        print(f"❌ Documents directory not found: {documents_dir}")
        print("   Creating documents directory...")
        os.makedirs(documents_dir, exist_ok=True)
        print(f"✅ Created directory. Please place your PDF documents in: {documents_dir}")
        sys.exit(1)
    
    # Check for PDF files
    pdf_files = [f for f in os.listdir(documents_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print("❌ No PDF files found in the documents directory!")
        print(f"   Please place your PDF documents in: {documents_dir}")
        sys.exit(1)
    
    print(f"Found {len(pdf_files)} PDF file(s):")
    for pdf in pdf_files:
        print(f"  - {pdf}")
    print()
    
    # Confirm ingestion
    response = input("Do you want to ingest these documents? (y/n): ")
    if response.lower() != 'y':
        print("Ingestion cancelled.")
        sys.exit(0)
    
    print()
    print("Starting ingestion...")
    print("-" * 80)
    
    # Ingest documents
    try:
        status = document_processor.ingest_documents(documents_dir)
        
        print()
        print("-" * 80)
        print("INGESTION COMPLETE")
        print("-" * 80)
        print(f"Status: {status['status']}")
        print(f"Total documents: {status['total_documents']}")
        print(f"Processed documents: {status['processed_documents']}")
        print(f"Total chunks: {status['total_chunks']}")
        print()
        
        if status['status'] == 'success':
            print("✅ Documents ingested successfully!")
            print("   You can now start the FastAPI server and ask questions.")
        else:
            print(f"❌ Ingestion failed: {status.get('message', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        print()
        print(f"❌ Error during ingestion: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
