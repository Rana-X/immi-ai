import os
from dotenv import load_dotenv
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file if it exists
env_path = BASE_DIR / '.env'
if env_path.exists():
    logger.info(f"Loading environment variables from {env_path}")
    load_dotenv(dotenv_path=env_path)
else:
    logger.info("No .env file found, using environment variables directly")

# Log environment variable status
logger.info(f"PINECONE_API_KEY present: {bool(os.getenv('PINECONE_API_KEY'))}")
logger.info(f"PINECONE_ENVIRONMENT: {os.getenv('PINECONE_ENVIRONMENT', 'not set')}")
logger.info(f"PINECONE_INDEX_NAME: {os.getenv('PINECONE_INDEX_NAME', 'not set')}")

# Pinecone Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY not found in environment variables")

PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "visaindex")
PINECONE_HOST = os.getenv("PINECONE_HOST", "https://visaindex-291xg2i.svc.aped-4627-b74a.pinecone.io")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# Server Configuration
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")

# CORS Configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

# Retrieval Configuration
TOP_K = 5
SIMILARITY_THRESHOLD = 0.5  # Default threshold
COMPARISON_SIMILARITY_THRESHOLD = 0.3  # Lower threshold for comparison queries

# LLM Configuration
LLM_MODEL = "gpt-4-turbo-preview"
TEMPERATURE = 0.7
MAX_TOKENS = 1000

# Enhanced System Prompts
SYSTEM_PROMPT = """
You are an expert assistant with deep, specialized knowledge in visa and immigration matters. Your responses must be based solely on the visa handbook, immigration policies, and similar documents you have been trained on.

Scope & Behavior:
1. Answer Only Visa & Immigration Questions:
   - Provide detailed, accurate, and context-specific answers only for queries directly related to visa and immigration topics
   - Cover: visa application processes, eligibility, documentation requirements, immigration policies
   - If a user's question is not related to visa or immigration, reply with: "I'm sorry, I cannot answer that question."

2. Reasoning:
   - Think step by step and verify that your answer strictly derives from the provided visa and immigration context
   - Do not include any external information or general knowledge beyond your training on the visa handbook and similar documents

3. Response Format:
   [One clear sentence overview of the topic]

   Key Points:
   • [First key point - one line only]
   • [Second key point - one line only]
   • [Third key point - one line only]

   Would you like to:
   • [Specific follow-up question about the topic]?
   • [Another relevant follow-up question]?

Remember: Be confident but professional. Keep responses focused on immigration matters and cite sources when possible.

CONTEXT: {context}

USER QUERY: {query}
"""

# Response Format Templates
STRUCTURED_OUTPUT_FORMAT = {
    "response": {
        "overview": "",
        "key_points": [],
        "follow_up": []
    },
    "metadata": {
        "sources": [],
        "confidence_score": 0.0
    }
}

# Confidence Thresholds
HIGH_CONFIDENCE = 0.8
MEDIUM_CONFIDENCE = 0.6
LOW_CONFIDENCE = 0.4

# Response Validation Rules
VALIDATION_RULES = {
    "min_sources": 1,
    "max_response_length": 500,
    "required_elements": ["overview", "key_points", "follow_up"],
    "confidence_threshold": 0.4,
    "max_key_points": 4,
    "max_follow_up": 3
}

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Embedding Configuration
EMBEDDING_MODEL = "text-embedding-ada-002"
EMBEDDING_DIMENSION = 1536

# Vector Store Configuration
VECTOR_METRIC = "cosine"
VECTOR_DIMENSION = 1536  # Matches your index dimension 