from typing import List, Dict
import os
from pathlib import Path
import PyPDF2
from openai import OpenAI
import pinecone
from config.settings import (
    OPENAI_API_KEY,
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSION
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class DocumentLoader:
    def __init__(self):
        """Initialize OpenAI and Pinecone clients"""
        try:
            # Initialize OpenAI client
            self.openai_client = OpenAI(
                api_key=OPENAI_API_KEY
            )
            
            # Initialize Pinecone client
            self.pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
            
            logger.info(f"Successfully initialized Pinecone client")
            self.index = self.pc.Index(PINECONE_INDEX_NAME)
            logger.info(f"Successfully connected to index: {PINECONE_INDEX_NAME}")
            
        except Exception as e:
            logger.error(f"Error initializing document loader: {str(e)}")
            raise
    
    def load_document(self, file_path: str) -> List[Dict]:
        """Load and chunk document (PDF or TXT)"""
        chunks = []
        try:
            if file_path.endswith('.pdf'):
                chunks = self._load_pdf(file_path)
            elif file_path.endswith('.txt'):
                chunks = self._load_txt(file_path)
            return chunks
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {str(e)}")
            raise

    def _load_pdf(self, file_path: str) -> List[Dict]:
        """Load and chunk PDF document"""
        chunks = []
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    # Split into smaller chunks (e.g., paragraphs)
                    paragraphs = text.split('\n\n')
                    for para in paragraphs:
                        if len(para.strip()) > 100:  # Min length threshold
                            chunks.append({
                                'text': para.strip(),
                                'source': os.path.basename(file_path),
                                'page': page_num + 1
                            })
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error loading PDF {file_path}: {str(e)}")
            raise

    def _load_txt(self, file_path: str) -> List[Dict]:
        """Load and chunk text document"""
        chunks = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                # Split into sections by double newline
                sections = text.split('\n\n')
                for section in sections:
                    if len(section.strip()) > 50:  # Minimum length threshold
                        chunks.append({
                            'text': section.strip(),
                            'source': os.path.basename(file_path),
                            'page': 1  # For text files, use page 1
                        })
            return chunks
        except Exception as e:
            logger.error(f"Error loading text file {file_path}: {str(e)}")
            raise

    def create_embeddings(self, chunks: List[Dict]) -> List[Dict]:
        """Create embeddings for text chunks"""
        try:
            for chunk in chunks:
                response = self.openai_client.embeddings.create(
                    model=EMBEDDING_MODEL,
                    input=chunk['text']
                )
                chunk['embedding'] = response.data[0].embedding
            return chunks
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {str(e)}")
            raise

    def index_documents(self, chunks: List[Dict]):
        """Index documents in Pinecone"""
        try:
            # Prepare vectors for indexing
            vectors = []
            for i, chunk in enumerate(chunks):
                vector = {
                    'id': f"chunk_{i}",
                    'values': chunk['embedding'],
                    'metadata': {
                        'text': chunk['text'],
                        'source': chunk['source'],
                        'page': chunk['page']
                    }
                }
                vectors.append(vector)
            
            # Upsert to Pinecone in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)
            
            logger.info(f"Successfully indexed {len(vectors)} chunks")
            
        except Exception as e:
            logger.error(f"Error indexing documents: {str(e)}")
            raise 