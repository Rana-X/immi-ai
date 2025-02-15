from typing import Dict, List, Tuple
import re
from enum import Enum
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class QueryType(Enum):
    VISA_COMPARISON = "visa_comparison"
    VISA_REQUIREMENTS = "visa_requirements"
    IMMIGRATION_PROCESS = "immigration_process"
    LEGAL_REQUIREMENTS = "legal_requirements"
    DOCUMENTATION = "documentation"
    GENERAL = "general"

class QueryProcessor:
    """Handles query preprocessing, classification, and expansion"""
    
    # Keywords for query classification
    QUERY_KEYWORDS = {
        QueryType.VISA_COMPARISON: [
            "difference", "compare", "versus", "vs", "better",
            "comparison", "differences", "between"
        ],
        QueryType.VISA_REQUIREMENTS: [
            "visa", "requirements", "eligible", "qualify", "criteria",
            "h1b", "h-1b", "h1-b", "o1", "o-1", "l1", "l-1"
        ],
        QueryType.IMMIGRATION_PROCESS: [
            "process", "procedure", "steps", "how to", "timeline", 
            "duration", "processing time", "application"
        ],
        QueryType.LEGAL_REQUIREMENTS: [
            "law", "legal", "regulation", "rule", "compliance",
            "statute", "requirement", "mandatory"
        ],
        QueryType.DOCUMENTATION: [
            "document", "form", "certificate", "evidence", "proof",
            "documentation", "papers", "records"
        ]
    }

    def preprocess_query(self, query: str) -> str:
        """
        Clean and standardize the query
        
        Args:
            query: Original query string
            
        Returns:
            Preprocessed query
        """
        # Remove special characters
        query = re.sub(r'[^\w\s?]', ' ', query)
        
        # Remove extra whitespace
        query = ' '.join(query.split())
        
        # Convert to lowercase
        query = query.lower()
        
        return query

    def classify_query(self, query: str) -> QueryType:
        """Enhanced query classification"""
        query_words = set(query.lower().split())
        
        # Check for visa comparison first
        comparison_indicators = set(["difference", "compare", "vs", "versus", "between"])
        visa_indicators = set(["h1b", "h-1b", "h1", "o1", "o-1", "l1", "l-1", "visa"])
        
        if (comparison_indicators & query_words) and (len(visa_indicators & query_words) >= 2):
            return QueryType.VISA_COMPARISON
        
        # Continue with regular classification
        type_scores = {
            query_type: sum(1 for keyword in keywords 
                          if keyword in query)  # Check full query, not just words
            for query_type, keywords in self.QUERY_KEYWORDS.items()
        }
        
        max_score = max(type_scores.values())
        if max_score > 0:
            return max(type_scores.items(), key=lambda x: x[1])[0]
        
        return QueryType.GENERAL

    def expand_query(self, query: str, query_type: QueryType) -> List[str]:
        """Enhanced query expansion with better visa comparison handling"""
        expanded_queries = [query]
        
        # Normalize visa types
        query = query.lower()
        query = (query.replace("h1b", "h-1b")
                     .replace("h1-b", "h-1b")
                     .replace("h1", "h-1b")
                     .replace("o1", "o-1"))
        
        # Extract visa types from query
        visa_types = []
        if "h-1b" in query:
            visa_types.append("h-1b")
        if "o-1" in query:
            visa_types.append("o-1")
        if "l-1" in query:
            visa_types.append("l-1")
        
        if query_type == QueryType.VISA_COMPARISON and len(visa_types) >= 2:
            # Add individual queries for each visa type
            for visa_type in visa_types:
                expanded_queries.extend([
                    f"{visa_type} visa",
                    f"{visa_type} requirements",
                    f"{visa_type} eligibility",
                    f"{visa_type} qualification",
                    f"qualify for {visa_type}",
                    f"{visa_type} visa process"
                ])
            
            # Add comparison specific queries
            expanded_queries.extend([
                f"difference between {' and '.join(visa_types)}",
                f"compare {' vs '.join(visa_types)}",
                f"{' '.join(visa_types)} comparison"
            ])
        
        return list(set(expanded_queries))  # Remove duplicates

    def process_query(self, query: str) -> Tuple[str, QueryType, List[str]]:
        """
        Complete query processing pipeline
        
        Args:
            query: Original user query
            
        Returns:
            Tuple of (preprocessed_query, query_type, expanded_queries)
        """
        try:
            # Preprocess
            processed_query = self.preprocess_query(query)
            
            # Classify
            query_type = self.classify_query(processed_query)
            
            # Expand
            expanded_queries = self.expand_query(processed_query, query_type)
            
            logger.info(f"Processed query. Type: {query_type.value}")
            return processed_query, query_type, expanded_queries
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise 