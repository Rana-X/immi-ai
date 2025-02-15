---
title: Immi.AI - Immigration Assistant
emoji: 🌎
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.31.0
app_file: app.py
pinned: false
---

# Immi.AI - Immigration Assistant

An intelligent assistant designed to help answer questions about US immigration and visa processes. Using advanced RAG (Retrieval-Augmented Generation) technology, it provides accurate, up-to-date information about various visa types, immigration procedures, and requirements.

## Project Structure

```
project-root/
├── backend/          # FastAPI backend
│   ├── src/         # Source code
│   ├── main.py      # Main FastAPI application
│   └── requirements.txt
└── frontend/        # Next.js frontend
    ├── src/         # Source code
    └── package.json
```

## Setup Instructions

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. Run the backend:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your settings
   ```

4. Run the development server:
   ```bash
   npm run dev
   ```

## Important Note

This is an informational tool only and does not provide legal advice. Please consult with immigration attorneys for legal counsel.

## Features

- 🔍 Intelligent query understanding
- 📚 Comprehensive visa information
- 💬 Interactive chat interface
- 🔒 Privacy-focused design
- 🎯 Accurate, sourced responses

## Tech Stack

- Backend: FastAPI + Python
- Frontend: Next.js + TypeScript
- Vector Store: Pinecone
- LLM: OpenAI GPT-4

## Local Development

1. Install dependencies:
   ```