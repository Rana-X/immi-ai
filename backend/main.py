from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
import os
from dotenv import load_dotenv

# Configure logging first, before any other imports
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Log startup information
logger.info("Starting application...")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Directory contents: {os.listdir('.')}")
logger.info(f"Python version: {sys.version}")
logger.info(f"Environment variables: PORT={os.getenv('PORT')}")

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

    # Health check endpoint - make it super simple
    @app.get("/healthz")
    async def health_check():
        """Health check endpoint for Railway"""
        logger.info("Health check called")
        return {"status": "ok"}

    @app.on_event("startup")
    async def startup():
        """Initialize application"""
        try:
            # Import components here to catch any import errors
            from src.rag.retriever import VectorRetriever
            from src.rag.generator import AnswerGenerator
            from src.utils.question_clarifier import QuestionClarifier
            
            logger.info("Imported all required modules")
            
            global retriever, generator, clarifier
            retriever = VectorRetriever()
            generator = AnswerGenerator()
            clarifier = QuestionClarifier()
            
            logger.info("Initialized all components")
            logger.info("Application startup complete")
            
        except Exception as e:
            logger.error(f"Error during startup: {str(e)}", exc_info=True)
            raise

    # Rest of your existing routes...

except Exception as e:
    logger.error(f"Error during application initialization: {str(e)}", exc_info=True)
    raise

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting the Immigration Assistant API...")
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000"))) 