import streamlit as st
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager
from typing import Dict, Any
import logging
from src.rag.retriever import VectorRetriever
from src.rag.generator import AnswerGenerator
from src.utils.logger import setup_logger
from src.utils.question_clarifier import QuestionClarifier
from prometheus_fastapi_instrumentator import Instrumentator
import httpx

# Configure logging
logger = setup_logger(__name__)

# Initialize FastAPI with lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up...")
    yield
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(title="Immi.AI - Immigration Assistant", lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    """Initialize monitoring on startup"""
    Instrumentator().instrument(app).expose(app)
    logger.info("Application startup complete")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "accepted_disclaimer" not in st.session_state:
    st.session_state.accepted_disclaimer = False

# Custom CSS for styling
st.markdown("""
<style>
    /* Hide Streamlit elements */
    #MainMenu, header, footer {display: none;}
    .stDeployButton {display: none;}
    
    /* Modal styling */
    .modal-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background-color: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }
    
    .modal-content {
        background-color: white;
        padding: 2rem;
        border-radius: 12px;
        width: 90%;
        max-width: 800px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .modal-title {
        font-size: 24px;
        font-weight: 600;
        color: #1A202C;
        margin-bottom: 1.5rem;
    }
    
    .modal-text {
        font-size: 16px;
        line-height: 1.6;
        color: #4A5568;
        margin-bottom: 1.5rem;
    }
    
    .modal-list {
        margin: 1.5rem 0;
        padding-left: 1.5rem;
    }
    
    .modal-list li {
        color: #4A5568;
        line-height: 1.6;
        margin-bottom: 0.5rem;
    }
    
    .button-container {
        display: flex;
        justify-content: flex-end;
        gap: 1rem;
        margin-top: 2rem;
    }
    
    .btn {
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .btn-no {
        background-color: #EDF2F7;
        color: #4A5568;
        border: none;
    }
    
    .btn-yes {
        background-color: #48BB78;
        color: white;
        border: none;
    }
    
    .btn:hover {
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

def show_disclaimer_modal():
    st.markdown("""
    <div class="modal-container">
        <div class="modal-content">
            <h2 class="modal-title">Important Disclaimer</h2>
            <p class="modal-text">
                Immi.AI is designed for educational purposes only. This tool does not provide legal advice, and we explicitly disclaim any assertion that it offers legal counsel.
            </p>
            <p class="modal-text">Please note:</p>
            <ul class="modal-list">
                <li>We do not store or save any chat history</li>
                <li>Your data is not used for training or sold to third parties</li>
                <li>All information is cleared when you close or refresh the page</li>
            </ul>
            <div class="button-container">
                <button class="btn btn-no" onclick="handleNo()">No</button>
                <button class="btn btn-yes" onclick="handleYes()">Yes, I Understand</button>
            </div>
        </div>
    </div>
    
    <script>
        function handleNo() {
            window.location.href = 'https://www.uscis.gov/';
        }
        
        function handleYes() {
            const element = document.querySelector('.modal-container');
            element.style.display = 'none';
            window.parent.postMessage({accepted: true}, '*');
        }
        
        window.addEventListener('message', function(e) {
            if (e.data.accepted) {
                const streamlitDoc = window.parent.document;
                const yesButton = streamlitDoc.querySelector('button[kind="primary"]');
                if (yesButton) yesButton.click();
            }
        });
    </script>
    """, unsafe_allow_html=True)

def process_chat(question: str) -> Dict[str, Any]:
    """Process chat messages and return response"""
    try:
        # Check if it's a greeting
        greeting_words = {"hi", "hello", "hey", "greetings", "hi there", "hello there"}
        if question.lower().strip() in greeting_words:
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

        # Get relevant chunks and generate answer
        relevant_chunks = retriever.get_relevant_chunks(question)
        answer = generator.generate_answer(question, relevant_chunks)
        return answer

    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        return {
            "response": {
                "overview": "I apologize, but I encountered an error. Please try again.",
                "key_points": [],
                "follow_up": ["Would you like to try rephrasing your question?"]
            },
            "metadata": {
                "error": str(e),
                "confidence_score": 0
            }
        }

def main():
    # Set page config
    st.set_page_config(
        page_title="Immi.AI - Immigration Assistant",
        page_icon="🌎",
        layout="wide"
    )
    
    # Show disclaimer if not accepted
    if not st.session_state.accepted_disclaimer:
        show_disclaimer_modal()
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("No", key="no_button", type="secondary"):
                st.markdown('<script>window.location.href = "https://www.uscis.gov/";</script>', unsafe_allow_html=True)
        with col2:
            if st.button("Yes, I Understand", key="yes_button", type="primary"):
                st.session_state.accepted_disclaimer = True
                st.experimental_rerun()
        return
    
    # Chat interface (only shown after accepting disclaimer)
    if st.session_state.accepted_disclaimer:
        # Display chat messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="assistant-message">{message["content"]}</div>', unsafe_allow_html=True)

        # Chat input
        if prompt := st.chat_input("What can I help you with?"):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Get bot response
            response = process_chat(prompt)
            
            # Format and add assistant response
            if "response" in response:
                resp = response["response"]
                message = ""
                if resp.get("greeting"):
                    message += f"{resp['greeting']}\n\n"
                message += resp["overview"]
                
                if resp.get("key_points"):
                    message += "\n\nKey Points:\n"
                    message += "\n".join(f"• {point}" for point in resp["key_points"])
                
                if resp.get("follow_up"):
                    message += "\n\nFollow-up Questions:\n"
                    message += "\n".join(f"• {q}" for q in resp["follow_up"])
                
                st.session_state.messages.append({"role": "assistant", "content": message})
            
            # Rerun to update chat
            st.rerun()

if __name__ == "__main__":
    main() 