from typing import List
import pinecone
from langchain_community.vectorstores import Pinecone
from config.settings import (
    PINECONE_API_KEY,
    PINECONE_ENVIRONMENT,
    PINECONE_INDEX_NAME
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class PineconeManager:
    """Manages interactions with Pinecone vector store"""
    
    def __init__(self, embedding_model):
        """
        Initialize Pinecone client and vector store
        
        Args:
            embedding_model: The embedding model to use
        """
        try:
            self.pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
            
            self.vector_store = Pinecone.from_existing_index(
                index_name=PINECONE_INDEX_NAME,
                embedding=embedding_model
            )
            logger.info("Successfully initialized Pinecone vector store")
            
        except Exception as e:
            logger.error(f"Error initializing Pinecone: {str(e)}")
            raise
    
    def add_documents(self, documents: List):
        """
        Add documents to the vector store
        
        Args:
            documents: List of documents to add
        """
        try:
            self.vector_store.add_documents(documents)
            logger.info(f"Successfully added {len(documents)} documents to Pinecone")
        except Exception as e:
            logger.error(f"Error adding documents to Pinecone: {str(e)}")
            raise
    
    def similarity_search(self, query: str, k: int = 4):
        """
        Perform similarity search
        
        Args:
            query: Query text
            k: Number of results to return
            
        Returns:
            List of similar documents
        """
        try:
            results = self.vector_store.similarity_search(query, k=k)
            logger.info(f"Successfully performed similarity search for query: {query}")
            return results
        except Exception as e:
            logger.error(f"Error performing similarity search: {str(e)}")
            raise 