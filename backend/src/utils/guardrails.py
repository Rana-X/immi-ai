from typing import Dict, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class QueryCategory(Enum):
    VISA_APPLICATION = "visa_application"
    IMMIGRATION_POLICY = "immigration_policy"
    DOCUMENTATION = "documentation"
    ELIGIBILITY = "eligibility"
    GREETING = "greeting"
    INVALID = "invalid"

@dataclass
class ValidationResult:
    is_valid: bool
    category: QueryCategory
    confidence: float
    rejection_message: Optional[str] = None

class VisaImmigrationGuardrails:
    """Implements strict guardrails for visa and immigration queries"""
    
    def __init__(self):
        # Define valid topics and their keywords
        self.valid_topics: Dict[str, Set[str]] = {
            "visa": {
                # Standard visa types
                "visa", "h1b", "h-1b", "h1", "h-1", "h2b", "h-2b", "h2", "h-2",
                "f1", "f-1", "j1", "j-1", "o1", "o-1", "l1", "l-1",
                "eb1", "eb-1", "eb2", "eb-2", "eb3", "eb-3", "eb",
                # Common variations and abbreviations
                "h1 b", "h-1 b", "f 1", "f-1", "j 1", "o 1", "l 1",
                "eb 1", "eb 2", "eb 3", "ea", "ed", "ead", "vis", "visa",
                # Categories
                "work visa", "student visa", "business visa", "tourist visa",
                "employment visa", "dependent visa"
            },
            "immigration": {
                "immigration", "immigrant", "permanent resident", "green card",
                "naturalization", "citizenship", "alien", "foreign national",
                "status", "petition", "ead", "employment authorization"
            },
            "documentation": {
                "passport", "i20", "i-20", "ds160", "ds-160", "sevis", "i129",
                "i-129", "i485", "i-485", "ead", "document", "form", "ea", "ed"
            },
            "process": {
                "application", "process", "fee", "status", "interview",
                "appointment", "filing", "petition", "extension", "renewal"
            }
        }
        
        # Define greeting words
        self.greeting_words = {
            "hi", "hello", "hey", "greetings", "good morning", "good afternoon",
            "good evening", "hi there", "hello there"
        }
        
    def validate_query(self, query: str) -> ValidationResult:
        """
        Validate if the query is related to visa/immigration
        
        Args:
            query: User's question
            
        Returns:
            ValidationResult with validation details
        """
        query_lower = query.lower().strip()
        words = set(query_lower.split())
        
        # Check if it's a greeting
        if any(greeting in query_lower for greeting in self.greeting_words):
            return ValidationResult(
                is_valid=True,
                category=QueryCategory.GREETING,
                confidence=1.0
            )
        
        # Special handling for abbreviated terms
        if query_lower in {"h", "o", "l", "j", "f", "b"}:
            return ValidationResult(
                is_valid=True,
                category=QueryCategory.VISA_APPLICATION,
                confidence=0.7,
                rejection_message="Could you specify which visa category you're interested in?"
            )
        
        # Handle H1B variations
        if query_lower in {"h1", "h-1", "h1b", "h-1b", "h1-b", "h1 b"}:
            return ValidationResult(
                is_valid=True,
                category=QueryCategory.VISA_APPLICATION,
                confidence=0.8,
                rejection_message="Would you like to learn about the H-1B work visa requirements and process?"
            )
        
        # Handle O visa variations
        if query_lower in {"o1", "o-1", "o2", "o-2", "o3", "o-3"}:
            return ValidationResult(
                is_valid=True,
                category=QueryCategory.VISA_APPLICATION,
                confidence=0.8,
                rejection_message="Which O-visa category are you interested in? (O-1A for sciences/business, O-1B for arts/entertainment, O-2 for support staff, or O-3 for dependents)"
            )
        
        # Handle visa variations
        if query_lower in {"vis", "visa", "viza"}:
            return ValidationResult(
                is_valid=True,
                category=QueryCategory.VISA_APPLICATION,
                confidence=0.7,
                rejection_message="Which type of visa would you like to learn about?"
            )
        
        # Handle EAD variations
        if query_lower in {"ea", "ed", "ead"}:
            return ValidationResult(
                is_valid=True,
                category=QueryCategory.DOCUMENTATION,
                confidence=0.7,
                rejection_message="Are you asking about Employment Authorization Documents (EAD)?"
            )
        
        # Normalize common visa type formats and abbreviations
        query_lower = (query_lower.replace("h1b", "h-1b")
                                .replace("h1-b", "h-1b")
                                .replace("h1 b", "h-1b")
                                .replace("h1", "h-1b")
                                .replace("o1", "o-1")
                                .replace("l1", "l-1")
                                .replace("vis", "visa")
                                .replace("viza", "visa"))
        
        # Check topic relevance with normalized query
        topic_matches = {
            topic: len(keywords & set(query_lower.split()))
            for topic, keywords in self.valid_topics.items()
        }
        
        max_relevance = max(topic_matches.values())
        
        # If query is relevant to visa/immigration
        if max_relevance > 0:
            # Determine the category
            if any(word in self.valid_topics["visa"] for word in query_lower.split()):
                category = QueryCategory.VISA_APPLICATION
            elif any(word in self.valid_topics["documentation"] for word in query_lower.split()):
                category = QueryCategory.DOCUMENTATION
            elif any(word in self.valid_topics["immigration"] for word in query_lower.split()):
                category = QueryCategory.IMMIGRATION_POLICY
            else:
                category = QueryCategory.ELIGIBILITY
            
            return ValidationResult(
                is_valid=True,
                category=category,
                confidence=max_relevance
            )
        
        # Query is not related to visa/immigration
        return ValidationResult(
            is_valid=False,
            category=QueryCategory.INVALID,
            confidence=0.0,
            rejection_message=(
                "I'm sorry, I cannot answer that question. "
                "I can only assist with visa and immigration related matters."
            )
        )
    
    def format_response(self, validation_result: ValidationResult) -> Dict:
        """Format the response based on validation result"""
        if validation_result.is_valid:
            if validation_result.category == QueryCategory.GREETING:
                return {
                    "response": {
                        "greeting": "Hi! I'm Immi! I'm here to help with your visa and immigration questions. 👋",
                        "overview": "",
                        "key_points": [],
                        "follow_up": [
                            "What would you like to know about US visas?",
                            "Do you have questions about the immigration process?",
                            "Can I help you understand visa requirements?"
                        ]
                    },
                    "metadata": {
                        "confidence_score": 1.0
                    }
                }
            elif validation_result.rejection_message:  # For queries needing clarification
                # Special handling for visa-related queries
                if validation_result.category == QueryCategory.VISA_APPLICATION:
                    return {
                        "response": {
                            "greeting": "Hi, I'm Immi!",
                            "overview": "I need some clarification:",
                            "key_points": [],
                            "follow_up": [validation_result.rejection_message]
                        },
                        "metadata": {
                            "needs_clarification": True,
                            "clarification_types": ["visa_category"],
                            "confidence_score": validation_result.confidence
                        }
                    }
                # Special handling for documentation queries
                elif validation_result.category == QueryCategory.DOCUMENTATION:
                    return {
                        "response": {
                            "greeting": "Hi, I'm Immi!",
                            "overview": "I need some clarification:",
                            "key_points": [],
                            "follow_up": [validation_result.rejection_message]
                        },
                        "metadata": {
                            "needs_clarification": True,
                            "clarification_types": ["documentation"],
                            "confidence_score": validation_result.confidence
                        }
                    }
            return None  # Allow normal processing for other valid queries
        
        # Return rejection response for invalid queries
        return {
            "response": {
                "greeting": "Hi, I'm Immi!",
                "overview": validation_result.rejection_message,
                "key_points": [],
                "follow_up": [
                    "Would you like to know about different types of visas?",
                    "Can I help you understand the immigration process?",
                    "Do you have questions about visa requirements?"
                ]
            },
            "metadata": {
                "confidence_score": 0.0
            }
        } 