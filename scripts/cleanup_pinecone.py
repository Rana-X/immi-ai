import pinecone
from config.settings import PINECONE_API_KEY, PINECONE_INDEX_NAME
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def cleanup_pinecone():
    try:
        # Initialize Pinecone
        pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
        
        # Delete existing index if it exists
        if PINECONE_INDEX_NAME in pc.list_indexes().names():
            logger.info(f"Deleting existing index: {PINECONE_INDEX_NAME}")
            pc.delete_index(PINECONE_INDEX_NAME)
            logger.info("Index deleted successfully")
        else:
            logger.info("No existing index found")
            
    except Exception as e:
        logger.error(f"Error cleaning up Pinecone: {str(e)}")
        raise

if __name__ == "__main__":
    cleanup_pinecone() 