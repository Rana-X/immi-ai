import os
from pathlib import Path
from src.data.document_loader import DocumentLoader
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    try:
        # Initialize document loader
        loader = DocumentLoader()
        
        # Get path to documents
        docs_path = Path(__file__).parent.parent / 'data' / 'documents'
        
        # Process each document in the directory
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
        
        logger.info("Document loading and indexing complete")
        
    except Exception as e:
        logger.error(f"Error in document loading process: {str(e)}")
        raise

if __name__ == "__main__":
    main() 