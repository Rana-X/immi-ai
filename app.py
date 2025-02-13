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
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Custom CSS
    st.markdown("""
        <style>
        /* Global styles */
        .stApp {
            background-color: #000000;
        }
        
        /* Hide Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Logo */
        .logo-container {
            position: fixed;
            top: 20px;
            left: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
            z-index: 1000;
        }
        
        .logo-icon {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #8B5CF6, #6366F1);
            border-radius: 12px;
        }
        
        .logo-text {
            color: white;
            font-size: 24px;
            font-weight: 600;
        }
        
        /* Main content */
        .main-container {
            max-width: 800px;
            margin: 120px auto 0;
            padding: 0 20px;
        }
        
        .main-heading {
            font-size: 48px;
            font-weight: bold;
            color: white;
            text-align: center;
            margin-bottom: 40px;
        }
        
        .brand-name {
            color: #8B5CF6;
        }
        
        /* Input field */
        .stTextInput > div > div > input {
            background-color: #1A1A1A;
            color: white;
            border: none;
            border-radius: 12px;
            padding: 16px;
            font-size: 16px;
            margin-bottom: 1rem;
        }
        
        .stTextInput > div > div > input::placeholder {
            color: #666;
        }
        
        /* Disclaimer modal */
        .modal {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 32px;
            border-radius: 16px;
            max-width: 500px;
            width: 90%;
            z-index: 1000;
        }
        
        .modal-title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 16px;
            color: #1A1A1A;
        }
        
        .modal-text {
            color: #666;
            margin-bottom: 24px;
            line-height: 1.5;
        }
        
        .modal-buttons {
            display: flex;
            gap: 16px;
            justify-content: flex-end;
        }
        
        .btn {
            padding: 8px 24px;
            border-radius: 24px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .btn-secondary {
            background: #E5E7EB;
            color: #1A1A1A;
        }
        
        .btn-primary {
            background: #4CAF50;
            color: white;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        /* Overlay */
        .overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            z-index: 999;
        }
        </style>
    """, unsafe_allow_html=True)

    # Logo
    st.markdown("""
        <div class="logo-container">
            <div class="logo-icon"></div>
            <div class="logo-text">Immi.AI</div>
        </div>
    """, unsafe_allow_html=True)

    # Main content
    st.markdown("""
        <div class="main-container">
            <h1 class="main-heading">What can <span class="brand-name">Immi.AI</span> help you with?</h1>
        </div>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'disclaimer_accepted' not in st.session_state:
        st.session_state.disclaimer_accepted = False

    # Show disclaimer modal if not accepted
    if not st.session_state.disclaimer_accepted:
        st.markdown("""
            <div class="overlay"></div>
            <div class="modal">
                <h2 class="modal-title">Important Disclaimer</h2>
                <p class="modal-text">
                    Immi.AI is designed for educational purposes only. This tool does not provide legal advice, and we explicitly disclaim any assertion that it offers legal counsel.
                </p>
                <p class="modal-text">Please note:</p>
                <ul class="modal-text">
                    <li>We do not store or save any chat history</li>
                    <li>Your data is not used for training or sold to third parties</li>
                    <li>All information is cleared when you close or refresh the page</li>
                </ul>
                <p class="modal-text">Do you understand and agree to these terms?</p>
                <div class="modal-buttons">
                    <button class="btn btn-secondary" onclick="window.location.href='/'">No</button>
                    <button class="btn btn-primary" onclick="handleAccept()">Yes, I Understand</button>
                </div>
            </div>
            <script>
                function handleAccept() {
                    const element = window.parent.document.querySelector('iframe').contentWindow.document.querySelector('[data-testid="stFormSubmitButton"]');
                    if (element) {
                        element.click();
                    }
                }
            </script>
        """, unsafe_allow_html=True)

        # Hidden form to handle disclaimer acceptance
        with st.form(key='disclaimer_form', clear_on_submit=True):
            submit = st.form_submit_button('Accept', type='primary')
            if submit:
                st.session_state.disclaimer_accepted = True
                st.experimental_rerun()

    # Chat interface (only show if disclaimer accepted)
    if st.session_state.disclaimer_accepted:
        # Initialize chat history
        if 'messages' not in st.session_state:
            st.session_state.messages = []

        # Chat input with custom styling
        user_input = st.text_input(
            "",
            placeholder="Immigration question?",
            key="user_input",
            label_visibility="collapsed"
        )

        if user_input:
            # Add user message and get response
            st.session_state.messages.append({"role": "user", "content": user_input})
            # Process response (placeholder for now)
            response = "This is a placeholder response. The actual AI response will be integrated here."
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.experimental_rerun()

if __name__ == "__main__":
    main() 