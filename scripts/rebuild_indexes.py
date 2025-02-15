import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import pinecone
from src.data.document_loader import DocumentLoader
from src.utils.logger import setup_logger
from config.settings import (
    PINECONE_API_KEY,
    PINECONE_ENVIRONMENT,
    PINECONE_INDEX_NAME,
    VECTOR_DIMENSION
)

logger = setup_logger(__name__)

def rebuild_indexes():
    try:
        logger.info("Starting index rebuild process...")
        
        # Initialize Pinecone
        pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
        
        # Delete existing index if it exists
        if PINECONE_INDEX_NAME in pc.list_indexes().names():
            logger.info(f"Deleting existing index: {PINECONE_INDEX_NAME}")
            pc.delete_index(PINECONE_INDEX_NAME)
            logger.info("Index deleted successfully")
        
        # Create new index with proper spec
        logger.info(f"Creating new index: {PINECONE_INDEX_NAME}")
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=VECTOR_DIMENSION,
            metric="cosine",
            spec=pinecone.ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        logger.info("Index created successfully")
        
        # Initialize document loader
        loader = DocumentLoader()
        
        # Get path to documents
        docs_path = Path(__file__).parent.parent / 'data' / 'documents'
        
        # Process each document
        for doc_file in docs_path.glob('*.*'):
            if doc_file.suffix in ['.pdf', '.txt']:
                logger.info(f"Processing {doc_file}")
                
                # Load and chunk document
                chunks = loader.load_document(str(doc_file))
                logger.info(f"Created {len(chunks)} chunks from {doc_file}")
                
                # Create embeddings
                chunks_with_embeddings = loader.create_embeddings(chunks)
                
                # Index documents
                loader.index_documents(chunks_with_embeddings)
                logger.info(f"Indexed chunks from {doc_file}")
        
        logger.info("Index rebuild complete!")
        
    except Exception as e:
        logger.error(f"Error rebuilding index: {str(e)}")
        raise

if __name__ == "__main__":
    rebuild_indexes() 