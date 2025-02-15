import os
from dotenv import load_dotenv
from pathlib import Path

# Build paths and load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent
env_file = BASE_DIR / '.env'
load_dotenv(env_file)

print(f"Checking environment variables...")
print(f"Environment file path: {env_file}")
print(f"Environment file exists: {env_file.exists()}")

# Check Pinecone variables
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_env = os.getenv("PINECONE_ENVIRONMENT")
pinecone_index = os.getenv("PINECONE_INDEX_NAME")

print("\nPinecone Configuration:")
print(f"API Key: {pinecone_api_key[:10]}..." if pinecone_api_key else "API Key: Not found")
print(f"Environment: {pinecone_env}")
print(f"Index Name: {pinecone_index}")

# Check OpenAI variables
openai_api_key = os.getenv("OPENAI_API_KEY")
print("\nOpenAI Configuration:")
print(f"API Key: {openai_api_key[:10]}..." if openai_api_key else "API Key: Not found") 