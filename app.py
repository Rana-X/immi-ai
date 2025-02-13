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
        page_icon="🌎",
        layout="wide"
    )

    # Custom CSS for dark theme and modern UI
    st.markdown("""
        <style>
        /* Main container */
        .stApp {
            background-color: #0A0A0F;
            color: white;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        /* Header */
        .main-header {
            text-align: center;
            padding: 2rem 0;
            margin-bottom: 2rem;
        }
        
        .main-header h1 {
            font-size: 3.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
            background: linear-gradient(120deg, #4CAF50, #2196F3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .main-header p {
            font-size: 1.2rem;
            color: #B0BEC5;
        }
        
        /* Chat input */
        .stTextInput > div > div > input {
            background-color: #1E1E1E;
            color: white;
            border: 1px solid #333;
            border-radius: 10px;
            padding: 1rem;
            font-size: 1.1rem;
            margin-bottom: 1rem;
        }
        
        /* Send button */
        .stButton > button {
            background: linear-gradient(90deg, #4CAF50, #2196F3);
            color: white;
            border: none;
            border-radius: 25px;
            padding: 0.8rem 2rem;
            font-size: 1.1rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
        }
        
        /* Chat messages */
        .chat-message {
            padding: 1rem 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            animation: fadeIn 0.5s ease;
        }
        
        .user-message {
            background-color: #2C3E50;
            margin-left: 20%;
            border-top-right-radius: 5px;
        }
        
        .assistant-message {
            background-color: #1E1E1E;
            margin-right: 20%;
            border-top-left-radius: 5px;
        }
        
        /* Disclaimer */
        .disclaimer {
            background-color: #1E1E1E;
            border-radius: 10px;
            padding: 1rem;
            margin-top: 2rem;
            border: 1px solid #333;
        }
        
        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
        <div class="main-header">
            <h1>Welcome to Immi.AI 👋</h1>
            <p>Your intelligent assistant for US immigration and visa inquiries.</p>
        </div>
    """, unsafe_allow_html=True)

    # Create two columns for better layout
    col1, col2 = st.columns([2, 1])

    with col1:
        # Chat interface
        if 'messages' not in st.session_state:
            st.session_state.messages = []

        # Display chat history
        for message in st.session_state.messages:
            message_class = "user-message" if message["role"] == "user" else "assistant-message"
            st.markdown(
                f'<div class="chat-message {message_class}">{message["content"]}</div>',
                unsafe_allow_html=True
            )

        # Chat input
        user_input = st.text_input(
            "",
            placeholder="Type your immigration or visa related question here...",
            key="user_input"
        )

        # Send button
        if st.button("Send", key="send_button"):
            if user_input:
                # Add user message
                st.session_state.messages.append({
                    "role": "user",
                    "content": user_input
                })

                # Simulate assistant response
                response = {
                    "response": {
                        "greeting": "Hi! 👋",
                        "overview": "I'm here to help with your immigration questions.",
                        "key_points": [
                            "I can provide information about various visa types",
                            "I can explain immigration processes",
                            "I can help clarify documentation requirements"
                        ],
                        "follow_up": [
                            "What specific visa type are you interested in?",
                            "Would you like to know about application timelines?",
                            "Do you have questions about eligibility criteria?"
                        ]
                    }
                }

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

                # Add assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "\n".join(formatted_response)
                })

                # Clear input and rerun
                st.experimental_rerun()

    with col2:
        # Disclaimer in a card-like container
        st.markdown("""
            <div class="disclaimer">
                <h3>ℹ️ Disclaimer</h3>
                <ul style="list-style-type: none; padding-left: 0;">
                    <li>• This is an informational tool only</li>
                    <li>• Does not provide legal advice</li>
                    <li>• Please consult immigration attorneys for legal counsel</li>
                    <li>• We do not store or save any chat history</li>
                    <li>• Your data is not used for training or shared with third parties</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 