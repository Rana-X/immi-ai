from langchain_openai import OpenAIEmbeddings
from config.settings import OPENAI_API_KEY, EMBEDDING_MODEL
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class EmbeddingManager:
    """Manages document embeddings using OpenAI's embedding model"""
    
    def __init__(self):
        """Initialize the embedding model"""
        try:
            self.embedding_model = OpenAIEmbeddings(
                model=EMBEDDING_MODEL,
                openai_api_key=OPENAI_API_KEY
            )
            logger.info(f"Successfully initialized embedding model: {EMBEDDING_MODEL}")
        except Exception as e:
            logger.error(f"Error initializing embedding model: {str(e)}")
            raise
    
    def get_embeddings(self, texts):
        """
        Generate embeddings for the given texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings
        """
        try:
            embeddings = self.embedding_model.embed_documents(texts)
            logger.info(f"Successfully generated embeddings for {len(texts)} texts")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise 