from typing import Dict, Set, Tuple, Optional, List
import re
from dataclasses import dataclass
from fuzzywuzzy import fuzz
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class QueryAnalysis:
    """Stores the analysis results of a query"""
    is_immigration_related: bool
    confidence_score: float
    matched_keywords: List[str]
    needs_clarification: bool
    clarification_message: Optional[str] = None

class ImmigrationQueryClassifier:
    """Classifies and handles immigration-related queries"""
    
    def __init__(self):
        # Define keyword categories with variations
        self.keyword_categories = {
            "visa_types": {
                "h1b", "h-1b", "h1-b", "h1", "o1", "o-1", "l1", "l-1",
                "eb1", "eb-1", "eb2", "eb-2", "eb3", "eb-3", "eb",
                "j1", "j-1", "f1", "f-1", "b1", "b-1", "b2", "b-2",
                # Add O-series visa variations
                "o-series", "o series", "o visa", "o1a", "o-1a", 
                "o1b", "o-1b", "o2", "o-2", "o3", "o-3"
            },
            "immigration_terms": {
                "visa", "immigration", "immigrant", "nonimmigrant",
                "green card", "permanent resident", "citizenship",
                "naturalization", "petition", "alien", "foreign national",
                # Add O-visa specific terms
                "extraordinary ability", "distinguished merit",
                "arts", "sciences", "athletics", "business", 
                "motion picture", "television"
            },
            "processes": {
                "application", "processing", "filing", "status", "extension",
                "transfer", "amendment", "renewal", "appeal", "rfe"
            },
            "documents": {
                "passport", "i20", "i-20", "ds160", "ds-160", "sevis",
                "i129", "i-129", "i485", "i-485", "ead", "i765", "i-765"
            }
        }
        
        # Combine all keywords for easy lookup
        self.all_keywords = set()
        for category in self.keyword_categories.values():
            self.all_keywords.update(category)
        
        # Define ambiguous terms that need clarification
        self.ambiguous_terms = {
            "eb": "Could you specify which EB category you're interested in? (EB-1, EB-2, or EB-3)",
            "h": "Are you referring to H-1B visa?",
            "o": "Which O-visa category are you interested in? (O-1A for sciences/business, O-1B for arts/entertainment, O-2 for support staff, or O-3 for dependents)",
            "status": "Could you specify which visa status you're asking about?",
            "visa": "Which type of visa are you interested in?"
        }
    
    def preprocess_query(self, query: str) -> str:
        """
        Preprocess the query for consistent matching
        
        Args:
            query: Raw user query
            
        Returns:
            Preprocessed query string
        """
        # Convert to lowercase
        query = query.lower()
        
        # Normalize visa type formats
        query = (query.replace("h1b", "h-1b")
                     .replace("h1-b", "h-1b")
                     .replace("o1a", "o-1a")
                     .replace("o1b", "o-1b")
                     .replace("o1", "o-1")
                     .replace("o2", "o-2")
                     .replace("o3", "o-3")
                     .replace("l1", "l-1"))
        
        # Remove extra whitespace
        query = " ".join(query.split())
        
        return query
    
    def check_for_ambiguity(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Check if query contains ambiguous terms that need clarification
        
        Args:
            query: Preprocessed query
            
        Returns:
            Tuple of (needs_clarification, clarification_message)
        """
        query = self.preprocess_query(query)
        
        # Check for specific visa categories first
        specific_categories = {
            "o-1a", "o-1b", "o-2", "o-3",
            "h-1b", "l-1", "eb-1", "eb-2", "eb-3"
        }
        
        if any(category in query for category in specific_categories):
            return False, None
            
        # Check for O series without specific category
        if "o series" in query or "o visa" in query or "o-series" in query:
            return True, self.ambiguous_terms["o"]
            
        # Then check for other ambiguous terms
        for term, message in self.ambiguous_terms.items():
            # Check if term appears as a whole word
            if re.search(rf'\b{term}\b', query):
                return True, message
                
        return False, None
    
    def calculate_keyword_match_score(self, query: str) -> Tuple[float, List[str]]:
        """
        Calculate how well the query matches immigration keywords using fuzzy matching
        
        Args:
            query: Preprocessed query
            
        Returns:
            Tuple of (confidence_score, matched_keywords)
        """
        words = query.split()
        matched_keywords = []
        max_score = 0
        
        # Common misspellings and variations
        common_variations = {
            "citizen": ["citizenship", "citezen", "citizn", "citzenshi", "citizenshp"],
            "visa": ["viza", "vis", "visas"],
            "immigration": ["imigration", "immigraton", "immig"],
            "passport": ["passprt", "pasport"],
            "employment": ["employ", "employmnt"],
            "authorization": ["auth", "authorize", "authoriz"],
        }
        
        # Check each word against keywords using fuzzy matching
        for word in words:
            # First check exact matches
            if word in self.all_keywords:
                matched_keywords.append(word)
                max_score = max(max_score, 1.0)
                continue
            
            # Then check common variations
            for correct_form, variations in common_variations.items():
                if word in variations or any(fuzz.ratio(word, var) > 85 for var in variations):
                    matched_keywords.append(correct_form)
                    max_score = max(max_score, 0.9)
                    continue
            
            # Finally check fuzzy matching against all keywords
            for keyword in self.all_keywords:
                ratio = fuzz.ratio(word, keyword)
                if ratio > 85:  # High confidence match
                    matched_keywords.append(keyword)
                    max_score = max(max_score, ratio / 100)
                elif ratio > 70:  # Partial match
                    matched_keywords.append(keyword)
                    max_score = max(max_score, ratio / 100)
        
        return max_score, list(set(matched_keywords))
    
    def is_immigration_related(self, query: str) -> QueryAnalysis:
        """
        Determine if a query is related to immigration
        
        Args:
            query: User's query
            
        Returns:
            QueryAnalysis object with classification results
        """
        # Preprocess query
        processed_query = self.preprocess_query(query)
        
        # Special handling for H1B variations
        h1b_variations = {'h1', 'h-1', 'h1b', 'h-1b', 'h1-b'}
        if any(variation in processed_query for variation in h1b_variations):
            return QueryAnalysis(
                is_immigration_related=True,
                confidence_score=0.95,
                matched_keywords=['h-1b', 'visa'],
                needs_clarification=True,
                clarification_message="Would you like to learn about the H-1B work visa requirements and process?"
            )
        
        # Special handling for short queries that might be visa types
        if len(processed_query) <= 3:
            visa_prefixes = {'h', 'l', 'o', 'j', 'f', 'b', 'eb'}
            if processed_query in visa_prefixes:
                return QueryAnalysis(
                    is_immigration_related=True,
                    confidence_score=0.9,
                    matched_keywords=[f"{processed_query}-visa"],
                    needs_clarification=True,
                    clarification_message=f"Are you asking about {processed_query.upper()}-series visas? Which specific category would you like to learn about?"
                )
        
        # Check for ambiguity
        needs_clarification, clarification_msg = self.check_for_ambiguity(processed_query)
        
        # Calculate match score
        confidence_score, matched_keywords = self.calculate_keyword_match_score(processed_query)
        
        # Determine if query is immigration-related
        is_related = confidence_score > 0.7 or len(matched_keywords) > 0
        
        return QueryAnalysis(
            is_immigration_related=is_related,
            confidence_score=confidence_score,
            matched_keywords=matched_keywords,
            needs_clarification=needs_clarification,
            clarification_message=clarification_msg if needs_clarification else None
        )

def process_query(query: str) -> str:
    """
    Process a user query and return appropriate response
    
    Args:
        query: User's question
        
    Returns:
        Response message
    """
    classifier = ImmigrationQueryClassifier()
    analysis = classifier.is_immigration_related(query)
    
    if analysis.needs_clarification:
        return f"I need some clarification: {analysis.clarification_message}"
    
    if analysis.is_immigration_related:
        # Here you would normally call your RAG system
        return f"Processing immigration query: '{query}'\nMatched keywords: {', '.join(analysis.matched_keywords)}"
    
    return "I'm sorry, I cannot answer that question. I can only assist with visa and immigration related matters."

def main():
    """Main interaction loop"""
    import sys

    # Check if input is being piped
    if not sys.stdin.isatty():
        # Handle piped input
        for line in sys.stdin:
            query = line.strip()
            if query:
                response = process_query(query)
                print(f"Query: {query}")
                print(f"Response: {response}")
        return

    # Interactive mode
    print("Welcome to the Immigration Query Classifier!")
    print("Enter your questions (or 'quit' to exit)")
    
    while True:
        try:
            query = input("\nYour question: ").strip()
            
            if query.lower() in {'quit', 'exit', 'q'}:
                print("Goodbye!")
                break
            
            if not query:
                print("Please enter a question.")
                continue
            
            response = process_query(query)
            print(f"\nResponse: {response}")
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main() 