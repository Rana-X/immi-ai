---
title: Immi.AI - Immigration Assistant
emoji: 🌎
colorFrom: blue
colorTo: purple
sdk: streamlit
app_port: 8501
pinned: false
---

# Immi.AI - Your Immigration Assistant

Immi.AI is an intelligent assistant designed to help answer questions about US immigration and visa processes. Using advanced RAG (Retrieval-Augmented Generation) technology, it provides accurate, up-to-date information about various visa types, immigration procedures, and requirements.

## Features

- 🔍 Intelligent query understanding
- 📚 Comprehensive visa information
- 💬 Interactive chat interface
- 🔒 Privacy-focused design
- 🎯 Accurate, sourced responses

## Technical Stack

- **Frontend**: Streamlit
- **Backend**: Python with RAG architecture
- **Vector Store**: Pinecone
- **LLM**: OpenAI GPT-4
- **Deployment**: Hugging Face Spaces

## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

## Important Note

This is an informational tool only and does not provide legal advice. Please consult with immigration attorneys for legal counsel.

## Feedback

Your feedback helps improve Immi.AI! Please report any issues or suggestions through the Hugging Face community forums.
