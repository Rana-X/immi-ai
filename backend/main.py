from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
import os
from dotenv import load_dotenv
from src.rag.retriever import VectorRetriever
from src.rag.generator import AnswerGenerator
from pydantic import BaseModel

# Configure logging first, before any other imports
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    question: str
    context: dict = {}
    is_first_message: bool = False

try:
    # Load environment variables
    load_dotenv()
    logger.info("Loaded environment variables")

    # Initialize FastAPI app
    app = FastAPI(title="Immi.AI - Immigration Assistant")
    logger.info("Initialized FastAPI application")

    # Get allowed origins from environment variable
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    logger.info(f"Configured CORS origins: {allowed_origins}")

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("Added CORS middleware")

    # Initialize components
    retriever = VectorRetriever()
    generator = AnswerGenerator()
    logger.info("Initialized RAG components")

    # Health check endpoint
    @app.get("/healthz")
    async def health_check():
        """Health check endpoint for Railway"""
        logger.info("Health check called")
        return {"status": "ok"}

    # Chat endpoint
    @app.post("/chat")
    async def chat(request: ChatRequest):
        """Chat endpoint for immigration queries"""
        try:
            logger.info(f"Received question: {request.question}")
            
            # Get relevant documents
            relevant_docs = retriever.get_relevant_documents(request.question)
            logger.info(f"Found {len(relevant_docs)} relevant documents")
            
            # Generate answer
            response = generator.generate_answer(request.question, relevant_docs)
            logger.info("Generated response")
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing chat request: {str(e)}")
            raise

except Exception as e:
    logger.error(f"Error during application initialization: {str(e)}")
    raise

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting the Immigration Assistant API...")
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000"))) 