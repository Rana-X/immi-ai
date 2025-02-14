import streamlit as st

# Set page config (must be the first Streamlit command)
st.set_page_config(
    page_title="Immi.AI - Immigration Assistant",
    page_icon="🌎",
    layout="wide"
)

import openai
import pinecone
import logging
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI and Pinecone
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = pinecone.Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("visaindex")

def get_embeddings(text: str) -> List[float]:
    """Get embeddings for text using OpenAI"""
    response = openai_client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

def get_relevant_chunks(query: str, top_k: int = 4) -> List[Dict]:
    """Get relevant chunks using Pinecone"""
    try:
        # Get query embedding
        query_embedding = get_embeddings(query)
        
        # Query Pinecone
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Format results
        chunks = []
        for match in results['matches']:
            if match.score > 0.7:  # Similarity threshold
                chunks.append({
                    'text': match.metadata.get('text', ''),
                    'source': match.metadata.get('source', 'Unknown'),
                    'page': match.metadata.get('page', 0),
                    'similarity': match.score
                })
        
        return chunks
    except Exception as e:
        logger.error(f"Error retrieving chunks: {str(e)}")
        return []

def generate_answer(question: str, relevant_chunks: List[Dict]) -> Dict[str, Any]:
    """Generate answer using OpenAI"""
    try:
        # Prepare context from chunks
        context = "\n\n".join([
            f"[{chunk['source']}: Page {chunk['page']}]\n{chunk['text']}"
            for chunk in relevant_chunks
        ])
        
        # Generate response
        response = openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": """You are Immi.ai, a confident and warmhearted AI assistant specializing in US immigration. 
                Combine technical expertise with genuine care. Format your responses with:
                1. A clear overview
                2. 2-3 key points if relevant
                3. 2-3 follow-up questions
                
                Context: {context}""".format(context=context)},
                {"role": "user", "content": question}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Extract and structure the response
        answer_text = response.choices[0].message.content
        
        # Parse response sections
        sections = answer_text.split("\n\n")
        overview = sections[0] if sections else ""
        
        key_points = []
        follow_up = []
        
        for section in sections[1:]:
            if "Key Points:" in section:
                points = section.split("\n")[1:]
                key_points = [p.strip("• ").strip() for p in points if p.strip()]
            elif "Follow-up Questions:" in section:
                questions = section.split("\n")[1:]
                follow_up = [q.strip("• ").strip() for q in questions if q.strip()]
        
        return {
            "response": {
                "overview": overview,
                "key_points": key_points[:3],
                "follow_up": follow_up[:3]
            },
            "metadata": {
                "sources": [{"document": c["source"], "page": c["page"]} for c in relevant_chunks],
                "confidence_score": sum(c["similarity"] for c in relevant_chunks) / len(relevant_chunks) if relevant_chunks else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating answer: {str(e)}")
        return {
            "response": {
                "overview": "I apologize, but I encountered an error while processing your question.",
                "key_points": [],
                "follow_up": ["Would you like to try rephrasing your question?"]
            },
            "metadata": {
                "error": str(e),
                "confidence_score": 0
            }
        }

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
        relevant_chunks = get_relevant_chunks(question)
        answer = generate_answer(question, relevant_chunks)
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
    
    /* Chat interface styling */
    .user-message {
        background-color: #4776E6;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        max-width: 80%;
        float: right;
        clear: both;
    }
    
    .assistant-message {
        background-color: #2D2D2D;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        max-width: 80%;
        float: left;
        clear: both;
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

def main():
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