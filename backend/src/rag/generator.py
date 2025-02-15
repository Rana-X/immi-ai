from typing import List, Dict, Union, Tuple
from openai import OpenAI
import json
from datetime import datetime
from config.settings import (
    OPENAI_API_KEY,
    LLM_MODEL,
    TEMPERATURE,
    MAX_TOKENS,
    SYSTEM_PROMPT,
    STRUCTURED_OUTPUT_FORMAT,
    VALIDATION_RULES,
    HIGH_CONFIDENCE,
    MEDIUM_CONFIDENCE,
    LOW_CONFIDENCE
)
from src.utils.logger import setup_logger
from random import choice

logger = setup_logger(__name__)

class ResponseValidator:
    """Validates generated responses against defined rules"""
    
    @staticmethod
    def validate_response(response: Dict) -> Tuple[bool, List[str]]:
        """
        Validate response against rules
        
        Returns:
            Tuple of (is_valid, list of validation messages)
        """
        messages = []
        is_valid = True
        
        # Check required elements
        for element in VALIDATION_RULES["required_elements"]:
            if not response.get(element):
                messages.append(f"Missing required element: {element}")
                is_valid = False
        
        # Check minimum sources
        if len(response.get("sources", [])) < VALIDATION_RULES["min_sources"]:
            messages.append("Insufficient source citations")
            is_valid = False
        
        # Check confidence threshold
        if response.get("confidence_score", 0) < VALIDATION_RULES["confidence_threshold"]:
            messages.append("Confidence score below threshold")
            is_valid = False
        
        return is_valid, messages

class AnswerGenerator:
    """Enhanced answer generator with validation and structured output"""
    
    def __init__(self):
        """Initialize OpenAI client and validator"""
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.validator = ResponseValidator()
    
    def calculate_confidence_score(self, relevant_chunks: List[Dict]) -> float:
        """Calculate confidence score based on chunk relevance"""
        if not relevant_chunks:
            return 0.0
        
        # Average similarity scores
        avg_similarity = sum(chunk['similarity'] for chunk in relevant_chunks) / len(relevant_chunks)
        
        # Consider number of sources
        source_diversity = len(set(chunk['source'] for chunk in relevant_chunks)) / len(relevant_chunks)
        
        # Combined score
        confidence = (avg_similarity * 0.7) + (source_diversity * 0.3)
        
        return min(1.0, confidence)
    
    def format_sources(self, chunks: List[Dict]) -> List[Dict]:
        """Format source citations with metadata"""
        sources = []
        for chunk in chunks:
            source = {
                "document": chunk['source'],
                "page": chunk['page'],
                "relevance_score": chunk['similarity'],
                "timestamp": datetime.now().isoformat(),
            }
            sources.append(source)
        return sources
    
    def generate_structured_answer(self, query: str, relevant_chunks: List[Dict]) -> Dict:
        """Generate a structured answer with metadata"""
        try:
            # Calculate confidence score
            confidence_score = self.calculate_confidence_score(relevant_chunks)
            
            # Check if it's a greeting
            greeting_words = {"hi", "hello", "hey", "greetings", "hi there", "hello there"}
            is_greeting = query.lower().strip() in greeting_words
            
            # Check if it's immigration-related
            immigration_keywords = {"visa", "immigration", "green card", "citizenship", "passport", "i-20", "sevis", 
                                 "uscis", "petition", "application", "status", "h1b", "f1", "work permit", "h-1b",
                                 "f-1", "o-1", "l-1", "eb"}
            is_immigration_related = any(keyword in query.lower() for keyword in immigration_keywords)
            
            # Prepare context with source information
            context = "\n\n".join([
                f"[{chunk['source']}: Page {chunk['page']}]\n{chunk['text']}"
                for chunk in relevant_chunks
            ])
            
            # Prepare system message with format instructions
            system_message = """You are Immi.ai, a confident and warmhearted AI assistant specializing in US immigration. Combine technical expertise with genuine care.

            PERSONALITY:
            - Confident but never arrogant
            - Show sincere kindness and empathy
            - Maintain a positive, solution-oriented mindset
            - Professionally friendly - warm while maintaining boundaries

            RESPONSE GUIDELINES:
            1. For greetings: Respond warmly with:
               "Hey! I'm Immi! I'm here to help make your US immigration journey smoother. I specialize in visa processes, immigration laws, and helping make the American dream more accessible. How can I assist you today?"

            2. For immigration questions:
               - Start with a clear, direct answer
               - Provide context and explanation when needed
               - Include 2-3 key points if they add value
               - End with 2-3 relevant follow-up questions

            3. For non-immigration topics:
               Redirect warmly: "While I'd love to chat about [topic], I'm actually your go-to expert for US immigration! How about we discuss your immigration journey instead?"

            4. Always maintain a helpful, empathetic tone while being accurate and professional.

            CONTEXT: {context}
            QUERY: {query}
            """.format(context=context, query=query)
            
            # For greetings, return immediately with standard response
            if is_greeting:
                return {
                    "response": {
                        "greeting": "Hi! I'm Immi! How can I help you today? 👋",
                        "disclaimer": "This is general information, not legal advice. Please consult with an immigration attorney for legal counsel.",
                        "overview": "",
                        "key_points": [],
                        "follow_up": []
                    },
                    "metadata": {
                        "sources": [],
                        "confidence_score": 1.0,
                        "generated_at": datetime.now().isoformat(),
                        "model_version": LLM_MODEL
                    }
                }
            
            # For non-immigration topics, return a friendly redirection
            if not is_immigration_related and not is_greeting:
                topic = query.split()[0] if query else "that"
                return {
                    "response": {
                        "greeting": "Hi, I'm Immi!",
                        "disclaimer": "This is general information, not legal advice. Please consult with an immigration attorney for legal counsel.",
                        "overview": f"While I'd love to chat about {topic}, I'm actually your go-to expert for US immigration! I've been trained extensively on visa processes, immigration laws, and everything that helps make the American dream accessible. How about we discuss your immigration journey instead?",
                        "key_points": [],
                        "follow_up": [
                            "What would you like to know about US visas?",
                            "Are you interested in learning about different immigration pathways?",
                            "Do you have any specific immigration questions I can help with?"
                        ]
                    },
                    "metadata": {
                        "sources": [],
                        "confidence_score": 1.0,
                        "generated_at": datetime.now().isoformat(),
                        "model_version": LLM_MODEL
                    }
                }
            
            # Generate response with streaming
            response = self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": query}
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                stream=True
            )
            
            # Initialize response text
            answer_text = ""
            
            # Process streaming response
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end='', flush=True)
                    answer_text += content
            print("\n")
            
            # Structure the response
            structured_response = {
                "response": {
                    "greeting": "Hi, I'm Immi!",
                    "disclaimer": "This is general information, not legal advice. Please consult with an immigration attorney for legal counsel.",
                    "overview": "",
                    "key_points": [],
                    "follow_up": []
                },
                "metadata": {
                    "sources": self.format_sources(relevant_chunks),
                    "confidence_score": confidence_score,
                    "generated_at": datetime.now().isoformat(),
                    "model_version": LLM_MODEL
                }
            }
            
            # Parse the response
            parts = answer_text.split("\n\n")
            
            # Extract overview
            for part in parts:
                part = part.strip()
                if part and not part.lower().startswith(("hi", "hello", "hey")):
                    structured_response["response"]["overview"] = part
                    break
            
            # Extract key points if present
            if "Key Points:" in answer_text:
                key_points_section = answer_text.split("Key Points:")[1].split("Follow-up Questions:" if "Follow-up Questions:" in answer_text else "\n\n")[0]
                key_points = [point.strip().strip('•').strip() for point in key_points_section.split('\n') if point.strip().startswith('•')]
                if key_points:
                    structured_response["response"]["key_points"] = key_points[:3]  # Limit to 3 key points
            
            # Extract follow-up questions if present
            if "Follow-up Questions:" in answer_text:
                follow_up_section = answer_text.split("Follow-up Questions:")[1]
                follow_up = [q.strip().strip('•').strip() for q in follow_up_section.split('\n') if q.strip().startswith('•')]
                if follow_up:
                    structured_response["response"]["follow_up"] = follow_up[:3]  # Limit to 3 follow-up questions
            
            return structured_response
            
        except Exception as e:
            logger.error(f"Error generating structured answer: {str(e)}")
            raise
    
    def generate_answer(self, query: str, relevant_chunks: List[Dict], structured: bool = True) -> Union[str, Dict]:
        """
        Generate an answer with optional structured output
        
        Args:
            query: User's question
            relevant_chunks: List of relevant text chunks with metadata
            structured: Whether to return structured output
            
        Returns:
            Either structured response dict or plain text answer
        """
        try:
            if structured:
                response = self.generate_structured_answer(query, relevant_chunks)
                
                # If no relevant chunks found, generate a response with a disclaimer
                if not relevant_chunks:
                    response.update({
                        "direct_answer": "I apologize, but I couldn't find specific information about this in my knowledge base. "
                                       "However, I can provide general information based on common immigration knowledge:\n\n"
                                       + response.get("direct_answer", ""),
                        "disclaimers": ["This information is general and may not be complete. "
                                      "Please verify with official sources."]
                    })
                
                return response
            
            # Generate simple text response
            context = "\n\n".join([
                f"Source: {chunk['source']}, Page: {chunk['page']}\n{chunk['text']}"
                for chunk in relevant_chunks
            ])
            
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
            ]
            
            response = self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=messages,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise 