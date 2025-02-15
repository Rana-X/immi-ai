from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ErrorType(Enum):
    LOW_CONFIDENCE = "low_confidence"
    RETRIEVAL_ERROR = "retrieval_error"
    GENERATION_ERROR = "generation_error"
    RATE_LIMIT = "rate_limit"
    PII_DETECTED = "pii_detected"
    VALIDATION_ERROR = "validation_error"

@dataclass
class ErrorResponse:
    error_type: ErrorType
    message: str
    suggestions: list[str]
    details: Optional[Dict] = None

class ErrorHandler:
    """Centralized error handling for the RAG system"""
    
    @staticmethod
    def handle_low_confidence(response: Dict, confidence_threshold: float = 0.7) -> Dict:
        """Handle responses with low confidence scores"""
        if response.get("confidence_score", 0) < confidence_threshold:
            return {
                "response": response.get("direct_answer", ""),
                "warning": "Limited confidence in this response",
                "suggestions": [
                    "Rephrase your question to be more specific",
                    "Include relevant visa types or categories",
                    "Specify the immigration process you're interested in",
                    "Consult official immigration sources for verification"
                ],
                "original_response": response
            }
        return response

    @staticmethod
    def handle_retrieval_error(error: Exception) -> ErrorResponse:
        """Handle errors during document retrieval"""
        logger.error(f"Retrieval error: {str(error)}")
        return ErrorResponse(
            error_type=ErrorType.RETRIEVAL_ERROR,
            message="Unable to retrieve relevant information",
            suggestions=[
                "Try again in a few moments",
                "Rephrase your question",
                "Break down complex questions into simpler ones"
            ],
            details={"error": str(error)}
        )

    @staticmethod
    def handle_generation_error(error: Exception) -> ErrorResponse:
        """Handle errors during answer generation"""
        logger.error(f"Generation error: {str(error)}")
        return ErrorResponse(
            error_type=ErrorType.GENERATION_ERROR,
            message="Error generating response",
            suggestions=[
                "Try simplifying your question",
                "Check if the question is clear and specific",
                "Ensure question relates to immigration topics"
            ],
            details={"error": str(error)}
        ) 