import streamlit as st
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from contextlib import asynccontextmanager
import uvicorn
import logging
import os
from prometheus_fastapi_instrumentator import Instrumentator
from datetime import datetime
from typing import Dict, Any

# Configure logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Prometheus instrumentation
instrumentator = Instrumentator()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    startup_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    app.state.startup_time = startup_time
    logger.info(f"===== Application Startup at {startup_time} =====")
    yield
    # Shutdown
    logger.info("Application shutdown")

# Initialize FastAPI for backend endpoints
app = FastAPI(
    title="Immi.AI API",
    description="""
    Immi.AI is an intelligent assistant designed to help answer questions about US immigration and visa processes.
    Using advanced RAG (Retrieval-Augmented Generation) technology, it provides accurate, up-to-date information
    about various visa types, immigration procedures, and requirements.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Set up Prometheus instrumentation
instrumentator.instrument(app).expose(app)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",     # Local development
        "https://*.hf.space",        # Hugging Face Spaces
        "https://*.huggingface.co",  # Hugging Face domains
        "https://*.vercel.app",      # Vercel domains
        "https://immi-ai.vercel.app" # Our production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        
        # For now, return a simple response
        return {
            "response": {
                "greeting": "Hi, I'm Immi!",
                "overview": "I'm currently being set up. Please check back soon for full functionality!",
                "key_points": [],
                "follow_up": [
                    "Would you like to learn about different visa types?",
                    "Do you have questions about the immigration process?"
                ]
            },
            "metadata": {
                "confidence_score": 1.0
            }
        }
        
    except Exception as e:
        logger.error(f"Error in chat processing: {str(e)}")
        return {
            "response": {
                "greeting": None,
                "overview": "I apologize, but I encountered an error while processing your question.",
                "key_points": [],
                "follow_up": ["Would you like to try again?"]
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
        page_icon="👋",
        layout="centered"
    )

    # Custom CSS
    st.markdown("""
        <style>
        .stApp {
            background-color: #0A0A0F;
            color: white;
        }
        .stTextInput > div > div > input {
            background-color: #1E1E1E;
            color: white;
            border-radius: 10px;
        }
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            border-radius: 20px;
            padding: 10px 20px;
        }
        .chat-message {
            padding: 15px;
            border-radius: 10px;
            margin: 5px 0;
        }
        .user-message {
            background-color: #2C3E50;
        }
        .assistant-message {
            background-color: #1E1E1E;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.title("Welcome to Immi.AI 👋")
    st.markdown("Your intelligent assistant for US immigration and visa inquiries.")

    # Initialize session state for chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.container():
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user-message">You: {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message assistant-message">Immi: {message["content"]}</div>', unsafe_allow_html=True)

    # Chat input
    with st.container():
        input_placeholder = "Type your immigration or visa related question here..."
        user_input = st.text_input("", placeholder=input_placeholder, key="user_input")
        
        if st.button("Send", key="send_button"):
            if user_input:
                # Add user message to chat
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                # Get response from backend
                response = process_chat(user_input)
                
                # Format response
                assistant_response = response["response"]
                formatted_response = []
                
                if assistant_response.get("greeting"):
                    formatted_response.append(assistant_response["greeting"])
                
                if assistant_response.get("overview"):
                    formatted_response.append(assistant_response["overview"])
                
                if assistant_response.get("key_points"):
                    formatted_response.append("\nKey Points:")
                    formatted_response.extend([f"• {point}" for point in assistant_response["key_points"]])
                
                if assistant_response.get("follow_up"):
                    formatted_response.append("\nFollow-up Questions:")
                    formatted_response.extend([f"• {q}" for q in assistant_response["follow_up"]])
                
                # Add assistant response to chat
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "\n".join(formatted_response)
                })
                
                # Clear input
                st.experimental_rerun()

    # Disclaimer
    with st.expander("ℹ️ Disclaimer"):
        st.markdown("""
        - This is an informational tool only and does not provide legal advice
        - Please consult with immigration attorneys for legal counsel
        - We do not store or save any chat history
        - Your data is not used for training or shared with third parties
        """)

if __name__ == "__main__":
    main() 