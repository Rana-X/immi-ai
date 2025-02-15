from typing import List, Dict
import pinecone
from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from config.settings import (
    PINECONE_API_KEY,
    PINECONE_ENVIRONMENT,
    PINECONE_INDEX_NAME,
    TOP_K,
    SIMILARITY_THRESHOLD,
    OPENAI_API_KEY
)
from src.utils.logger import setup_logger
from src.rag.query_processor import QueryProcessor, QueryType

logger = setup_logger(__name__)

class VectorRetriever:
    """Enhanced retriever with hybrid search and re-ranking"""
    
    def __init__(self):
        """Initialize connection to Pinecone"""
        try:
            # Initialize Pinecone with explicit values
            api_key = "pcsk_73bNrj_7YwqkwP76jvEyMy3aU7Z5eASbRA3Gd9CbLfzW96sewVYAUhZgWjq5K6U4prdk2n"
            environment = "us-east-1"
            
            # Initialize Pinecone client
            self.pc = pinecone.Pinecone(api_key=api_key)
            self.index = self.pc.Index("visaindex")
            
            logger.info(f"Successfully connected to Pinecone index: visaindex")
            
            # Initialize other components
            self.query_processor = QueryProcessor()
            self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
            self.tfidf = TfidfVectorizer(
                stop_words='english',
                max_features=5000
            )
            
        except Exception as e:
            logger.error(f"Error initializing VectorRetriever: {str(e)}")
            raise

    def get_semantic_results(self, query: str, top_k: int) -> List[Dict]:
        """Get results using semantic search"""
        try:
            # Generate embedding for the query
            query_embedding = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=query
            ).data[0].embedding
            
            # Query Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Format results to match expected structure
            formatted_results = []
            for match in results['matches']:
                formatted_result = {
                    'id': match.get('id', ''),
                    'score': match.get('score', 0),
                    'metadata': {
                        'text': match.get('metadata', {}).get('text', ''),
                        'source': match.get('metadata', {}).get('source', 'Unknown'),
                        'page': match.get('metadata', {}).get('page', 0)
                    }
                }
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            return []

    def get_keyword_results(self, query: str, chunks: List[Dict], top_k: int) -> List[Dict]:
        """Get results using keyword matching"""
        try:
            # Create TF-IDF matrix
            texts = [chunk.get('text', '') for chunk in chunks]
            if not texts:
                return []
            
            tfidf_matrix = self.tfidf.fit_transform(texts)
            
            # Get query vector
            query_vec = self.tfidf.transform([query])
            
            # Calculate similarities
            similarities = cosine_similarity(query_vec, tfidf_matrix)[0]
            
            # Get top results
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            results = []
            for i in top_indices:
                if similarities[i] > 0:
                    result = {
                        'id': str(i),  # Generate an ID if none exists
                        'text': chunks[i].get('text', ''),
                        'source': chunks[i].get('source', 'Unknown'),
                        'page': chunks[i].get('page', 0),
                        'keyword_score': float(similarities[i])
                    }
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in keyword search: {str(e)}")
            return []

    def rerank_results(self, query: str, semantic_results: List[Dict], keyword_results: List[Dict], query_type: QueryType) -> List[Dict]:
        """Enhanced reranking for comparison queries"""
        try:
            combined_results = {}
            
            # Add semantic results
            for result in semantic_results:
                doc_id = result.get('id', '')
                if doc_id:
                    combined_results[doc_id] = {
                        'text': result['metadata'].get('text', ''),
                        'source': result['metadata'].get('source', 'Unknown'),
                        'page': result['metadata'].get('page', 0),
                        'semantic_score': result.get('score', 0),
                        'keyword_score': 0
                    }
            
            # Add/update keyword results
            for result in keyword_results:
                doc_id = result.get('id', '')
                if doc_id in combined_results:
                    combined_results[doc_id]['keyword_score'] = result.get('keyword_score', 0)
                else:
                    combined_results[doc_id] = {
                        'text': result.get('text', ''),
                        'source': result.get('source', 'Unknown'),
                        'page': result.get('page', 0),
                        'semantic_score': 0,
                        'keyword_score': result.get('keyword_score', 0)
                    }
            
            # Calculate final scores with type-specific boosts
            for doc_id, result in combined_results.items():
                if not result['text']:  # Skip empty results
                    continue
                
                text_lower = result['text'].lower()
                base_score = (0.7 * result['semantic_score']) + (0.3 * result['keyword_score'])
                
                # Boost scores for comparison queries
                if query_type == QueryType.VISA_COMPARISON:
                    if "h-1b" in text_lower and "o-1" in text_lower:
                        base_score *= 1.5
                    elif "comparison" in text_lower or "difference" in text_lower:
                        base_score *= 1.3
                
                result['final_score'] = min(1.0, base_score)
            
            # Remove empty results and sort
            valid_results = [r for r in combined_results.values() if r['text']]
            return sorted(valid_results, key=lambda x: x['final_score'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error in reranking: {str(e)}")
            return []

    def get_relevant_chunks(self, query: str, top_k: int = TOP_K) -> List[Dict]:
        """
        Enhanced retrieval with query processing and hybrid search
        
        Args:
            query: The query text
            top_k: Number of chunks to retrieve
            
        Returns:
            List of relevant chunks with their metadata
        """
        try:
            # Process query
            processed_query, query_type, expanded_queries = self.query_processor.process_query(query)
            
            # Get semantic search results for each expanded query
            all_semantic_results = []
            for exp_query in expanded_queries:
                results = self.get_semantic_results(exp_query, top_k)
                all_semantic_results.extend(results)
            
            # Deduplicate results based on text content
            seen_texts = set()
            unique_results = []
            for result in all_semantic_results:
                text = result['metadata']['text']
                if text not in seen_texts:
                    seen_texts.add(text)
                    unique_results.append(result)
            
            # Get keyword search results
            keyword_results = self.get_keyword_results(
                processed_query,
                [r['metadata'] for r in unique_results],
                top_k
            )
            
            # Rerank results with adjusted weights for comparison queries
            final_results = self.rerank_results(
                processed_query,
                unique_results,
                keyword_results,
                query_type
            )
            
            # Filter and format results
            relevant_chunks = []
            for result in final_results:
                if result['final_score'] >= SIMILARITY_THRESHOLD:
                    chunk = {
                        'text': result['text'],
                        'source': result['source'],
                        'page': result['page'],
                        'similarity': result['final_score']
                    }
                    relevant_chunks.append(chunk)
            
            # If no results found with threshold, take top 2 results anyway
            if not relevant_chunks and final_results:
                top_2 = final_results[:2]
                relevant_chunks = [
                    {
                        'text': result['text'],
                        'source': result['source'],
                        'page': result['page'],
                        'similarity': result['final_score']
                    }
                    for result in top_2
                ]
            
            logger.info(f"Retrieved {len(relevant_chunks)} relevant chunks for query: {query}")
            return relevant_chunks[:top_k]
            
        except Exception as e:
            logger.error(f"Error retrieving chunks: {str(e)}")
            raise 