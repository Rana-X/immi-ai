from typing import Dict, Any, Optional
import hashlib
import json
from datetime import datetime, timedelta
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class SemanticCache:
    """Caches similar questions and their responses"""
    
    def __init__(self, ttl: timedelta = timedelta(hours=24)):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl
    
    def _generate_key(self, query: str) -> str:
        """Generate cache key from query"""
        return hashlib.md5(query.lower().encode()).hexdigest()
    
    def _is_expired(self, timestamp: datetime) -> bool:
        """Check if cache entry has expired"""
        return datetime.now() - timestamp > self.ttl
    
    def get(self, query: str) -> Optional[Dict[str, Any]]:
        """Get cached response for similar query"""
        key = self._generate_key(query)
        if key in self.cache:
            entry = self.cache[key]
            if not self._is_expired(entry['timestamp']):
                logger.info(f"Cache hit for query: {query}")
                return entry['response']
            else:
                del self.cache[key]
        return None
    
    def set(self, query: str, response: Dict[str, Any]):
        """Cache query response"""
        key = self._generate_key(query)
        self.cache[key] = {
            'response': response,
            'timestamp': datetime.now(),
            'query': query
        }
        logger.info(f"Cached response for query: {query}") 