from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from src.utils.query_classifier import ImmigrationQueryClassifier, QueryAnalysis
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ClarificationType(Enum):
    VISA_CATEGORY = "visa_category"
    TIMELINE = "timeline"
    DOCUMENT_TYPE = "document_type"
    PROCESS_STAGE = "process_stage"
    ELIGIBILITY = "eligibility"
    LOCATION = "location"

@dataclass
class ClarificationRequest:
    original_query: str
    clarification_type: ClarificationType
    suggested_questions: List[str]
    context: Optional[str] = None
    confidence_score: float = 0.0

class QuestionClarifier:
    """Enhanced question clarification system combining classifier and RAG insights"""
    
    def __init__(self):
        self.classifier = ImmigrationQueryClassifier()
        
        # Define clarification patterns and their follow-up questions
        self.clarification_patterns = {
            ClarificationType.VISA_CATEGORY: {
                "keywords": ["visa", "status", "category", "type"],
                "questions": [
                    "Which specific visa category are you interested in?",
                    "Are you applying as a worker, student, or visitor?",
                    "Is this for temporary or permanent residence?"
                ]
            },
            ClarificationType.TIMELINE: {
                "keywords": ["how long", "timeline", "processing", "wait", "duration"],
                "questions": [
                    "When are you planning to apply?",
                    "Is this for initial application or extension?",
                    "Which processing center or embassy would you use?"
                ]
            },
            ClarificationType.DOCUMENT_TYPE: {
                "keywords": ["document", "form", "application", "paperwork"],
                "questions": [
                    "Which stage of the application process are you in?",
                    "Have you already submitted any forms?",
                    "Are you asking about supporting documents or application forms?"
                ]
            },
            ClarificationType.PROCESS_STAGE: {
                "keywords": ["process", "step", "next", "procedure", "how to"],
                "questions": [
                    "Which stage of the process are you currently in?",
                    "Have you already started the application process?",
                    "Are you preparing for a specific step like interview or filing?"
                ]
            },
            ClarificationType.ELIGIBILITY: {
                "keywords": ["qualify", "eligible", "requirements", "criteria"],
                "questions": [
                    "What is your current occupation or field?",
                    "Do you have a specific employer sponsor?",
                    "What are your educational qualifications?"
                ]
            },
            ClarificationType.LOCATION: {
                "keywords": ["where", "location", "country", "embassy", "consulate"],
                "questions": [
                    "Which country are you applying from?",
                    "Have you identified your processing center or embassy?",
                    "Are you currently in the US or abroad?"
                ]
            }
        }

    def analyze_query_context(self, query: str, rag_context: Optional[Dict] = None) -> List[ClarificationRequest]:
        """
        Analyze query and context to identify needed clarifications
        
        Args:
            query: User's question
            rag_context: Optional context from RAG system
            
        Returns:
            List of clarification requests
        """
        clarifications = []
        
        # Get classifier analysis
        analysis = self.classifier.is_immigration_related(query)
        
        # If classifier already needs clarification, add it first
        if analysis.needs_clarification:
            clarifications.append(
                ClarificationRequest(
                    original_query=query,
                    clarification_type=ClarificationType.VISA_CATEGORY,
                    suggested_questions=[analysis.clarification_message],
                    confidence_score=1.0
                )
            )
            return clarifications
        
        # Check each clarification pattern
        query_lower = query.lower()
        for c_type, pattern in self.clarification_patterns.items():
            # Check if query contains pattern keywords but lacks specificity
            if any(keyword in query_lower for keyword in pattern["keywords"]):
                needs_clarification = self._check_specificity(query, c_type, analysis)
                if needs_clarification:
                    clarifications.append(
                        ClarificationRequest(
                            original_query=query,
                            clarification_type=c_type,
                            suggested_questions=pattern["questions"],
                            confidence_score=0.8
                        )
                    )
        
        return clarifications

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
                     .replace("h1 b", "h-1b")
                     .replace("h1", "h-1b")
                     .replace("h2b", "h-2b")
                     .replace("h2", "h-2b")
                     .replace("o1a", "o-1a")
                     .replace("o1b", "o-1b")
                     .replace("o1", "o-1")
                     .replace("o2", "o-2")
                     .replace("o3", "o-3")
                     .replace("l1", "l-1")
                     .replace("eb1", "eb-1")
                     .replace("eb2", "eb-2")
                     .replace("eb3", "eb-3"))
        
        # Remove extra whitespace
        query = " ".join(query.split())
        
        return query

    def _check_specificity(self, query: str, c_type: ClarificationType, analysis: QueryAnalysis) -> bool:
        """Check if query lacks specificity for given clarification type"""
        query = self.preprocess_query(query)
        
        if c_type == ClarificationType.VISA_CATEGORY:
            # Check if query mentions specific visa types
            specific_visas = {
                "h-1b", "h-2b", "l-1", "o-1a", "o-1b", "o-2", "o-3",
                "eb-1", "eb-2", "eb-3", "f-1", "j-1"
            }
            # Also check for visa categories
            visa_categories = {
                "work visa", "student visa", "business visa",
                "employment visa", "dependent visa"
            }
            return not (
                any(visa in query for visa in specific_visas) or
                any(category in query for category in visa_categories)
            )
            
        elif c_type == ClarificationType.TIMELINE:
            # Check if query includes specific timeframes
            timeframes = {"month", "year", "week", "day", "initial", "extension"}
            return not any(time in query for time in timeframes)
            
        elif c_type == ClarificationType.DOCUMENT_TYPE:
            # Check if query mentions specific forms or documents
            documents = {"i-129", "i-485", "i-765", "ds-160", "passport"}
            return not any(doc in query for doc in documents)
            
        elif c_type == ClarificationType.PROCESS_STAGE:
            # Check if query mentions specific stages
            stages = {"interview", "filing", "premium processing", "biometrics"}
            return not any(stage in query for stage in stages)
            
        elif c_type == ClarificationType.ELIGIBILITY:
            # Check if query includes specific eligibility criteria
            criteria = {"degree", "experience", "salary", "sponsor", "education"}
            return not any(crit in query for crit in criteria)
            
        elif c_type == ClarificationType.LOCATION:
            # Check if query mentions specific locations
            return not any(word in query for word in ["us", "usa", "america", "abroad"])
            
        return False

    def format_clarification_response(self, clarifications: List[ClarificationRequest]) -> Dict:
        """Format clarification requests into a response"""
        if not clarifications:
            return None
            
        # Sort clarifications by confidence score
        clarifications.sort(key=lambda x: x.confidence_score, reverse=True)
        
        # Take top 2 most confident clarifications
        top_clarifications = clarifications[:2]
        
        return {
            "needs_clarification": True,
            "message": "I need some additional information to better assist you:",
            "clarifications": [
                {
                    "type": c.clarification_type.value,
                    "questions": c.suggested_questions[:2]  # Limit to 2 questions per type
                }
                for c in top_clarifications
            ]
        }

def main():
    """Test the question clarifier"""
    clarifier = QuestionClarifier()
    
    print("Question Clarification System")
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
            
            clarifications = clarifier.analyze_query_context(query)
            response = clarifier.format_clarification_response(clarifications)
            
            if response:
                print("\nClarification needed:")
                for c in response["clarifications"]:
                    print(f"\n{c['type'].title()}:")
                    for q in c["questions"]:
                        print(f"- {q}")
            else:
                print("\nQuery is specific enough to process.")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main() 