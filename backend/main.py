from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
from src.rag.retriever import VectorRetriever
from src.rag.generator import AnswerGenerator
from src.utils.logger import setup_logger
from src.utils.question_clarifier import QuestionClarifier
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = setup_logger(__name__)

app = FastAPI(title="Immi.AI - Immigration Assistant")

# Get allowed origins from environment variable
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
logger.info(f"Configured CORS origins: {allowed_origins}")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
retriever = VectorRetriever()
generator = AnswerGenerator()
clarifier = QuestionClarifier()

@app.on_event("startup")
async def startup():
    """Initialize application"""
    logger.info("Application startup complete")
    logger.info(f"CORS origins configured: {app.middleware_stack.__dict__}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "components": {
            "retriever": "ok",
            "generator": "ok",
            "clarifier": "ok"
        }
    }

@app.post("/chat")
async def chat(request: Request):
    """Chat endpoint with question clarification"""
    try:
        body = await request.json()
        question = body.get("question", "").strip().lower()
        conversation_context = body.get("context", {})
        is_first_message = body.get("is_first_message", False)
        
        logger.info(f"Received question: {question}")
        logger.info(f"Context: {conversation_context}")
        
        if not question:
            return {"error": "Question is required"}
        
        # Base response structure
        base_response = {
            "greeting": "Hi, I'm Immi!" if is_first_message else None,
            "overview": "",
            "key_points": [],
            "follow_up": []
        }
        
        # Check if it's a greeting
        greeting_words = {"hi", "hello", "hey", "greetings", "hi there", "hello there"}
        if question in greeting_words:
            return {
                "response": {
                    "greeting": "Hi, I'm Immi! 👋",
                    "overview": "I'm here to help with your US immigration and visa questions.",
                    "key_points": [],
                    "follow_up": [
                        "What type of visa are you interested in?",
                        "Would you like to learn about the immigration process?",
                        "Do you have specific visa requirements questions?"
                    ]
                },
                "metadata": {
                    "confidence_score": 1.0
                }
            }
        
        # Handle "yes" responses to clarification questions
        if question == "yes":
            # Extract the previous context
            last_topic = conversation_context.get("last_topic", "").lower()
            logger.info(f"Last topic: {last_topic}")
            
            # Check for H1B mentions in the last topic
            if "h1b" in last_topic or "h-1b" in last_topic:
                # Directly provide H1B information instead of asking again
                relevant_chunks = retriever.get_relevant_chunks("What are the H1B visa requirements and process")
                answer = generator.generate_answer("What are the H1B visa requirements and process", relevant_chunks)
                if "response" in answer:
                    answer["response"] = {**base_response, **answer["response"]}
                return answer
                
            # Check for F1 mentions in the last topic
            elif "f1" in last_topic or "f-1" in last_topic:
                # Directly provide F1 information instead of asking again
                relevant_chunks = retriever.get_relevant_chunks("What are the F1 visa requirements and process")
                answer = generator.generate_answer("What are the F1 visa requirements and process", relevant_chunks)
                if "response" in answer:
                    answer["response"] = {**base_response, **answer["response"]}
                return answer
            
            else:
                # If no specific context, ask for clarification
                return {
                    "response": {
                        **base_response,
                        "overview": "Could you please specify which type of visa you're interested in?",
                        "follow_up": [
                            "Are you interested in H-1B work visas?",
                            "Are you interested in F-1 student visas?",
                            "Or would you like to learn about a different visa type?"
                        ]
                    },
                    "metadata": {
                        "confidence_score": 1.0
                    }
                }
        
        # Use classifier for initial analysis
        classifier_analysis = clarifier.classifier.is_immigration_related(question)
        
        # If classifier detects it needs clarification, return that immediately
        if classifier_analysis.needs_clarification:
            # Check if the question mentions specific visa types
            if any(term in question for term in ["h1b", "h-1b", "h1", "h-1"]):
                return {
                    "response": {
                        **base_response,
                        "overview": "Would you like to learn about the H-1B work visa requirements and process?",
                        "key_points": [
                            "H-1B is a specialty occupation work visa",
                            "Requires a bachelor's degree or equivalent",
                            "Annual cap of 85,000 visas with lottery system"
                        ],
                        "follow_up": [
                            "Type 'yes' to get detailed H-1B visa information",
                            "Would you like to know about the application process?",
                            "Are you interested in H-1B visa requirements?"
                        ]
                    },
                    "metadata": {
                        "needs_clarification": True,
                        "clarification_types": ["visa_category"],
                        "confidence_score": classifier_analysis.confidence_score
                    }
                }
            elif "f1" in question or "f-1" in question:
                return {
                    "response": {
                        **base_response,
                        "overview": "Would you like to learn about the F-1 student visa requirements and process?",
                        "key_points": [
                            "F-1 is a visa for international students",
                            "Requires acceptance to a US educational institution",
                            "Allows for study at accredited schools"
                        ],
                        "follow_up": ["Type 'yes' to get detailed information about F-1 visas"]
                    },
                    "metadata": {
                        "needs_clarification": True,
                        "clarification_types": ["visa_category"],
                        "confidence_score": classifier_analysis.confidence_score
                    }
                }
            
        # If question is specific enough, proceed with RAG
        relevant_chunks = retriever.get_relevant_chunks(question)
        logger.info(f"Found {len(relevant_chunks)} relevant chunks for question: {question}")
        
        # Generate answer using the chunks
        answer = generator.generate_answer(question, relevant_chunks)
        logger.info("Successfully generated answer")
        
        # Update the answer with base response structure
        if "response" in answer:
            answer["response"] = {**base_response, **answer["response"]}
        
        return answer
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return {
            "response": {
                "greeting": None,
                "disclaimer": "This is general information, not legal advice. Please consult with an immigration attorney for legal counsel.",
                "overview": "I apologize, but I encountered an error while processing your question.",
                "key_points": [],
                "follow_up": ["Would you like to try rephrasing your question?"]
            },
            "metadata": {
                "error": str(e),
                "confidence_score": 0
            }
        }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting the Immigration Assistant API...")
    uvicorn.run(app, host="0.0.0.0", port=8080) 