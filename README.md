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

An intelligent assistant designed to help answer questions about US immigration and visa processes, powered by AI and RAG (Retrieval-Augmented Generation) technology.

## Project Structure

```
immi-ai/
├── immi-ai-app/        # Main Next.js application
│   ├── src/           # Source code
│   │   ├── app/       # Next.js app directory
│   │   │   ├── api/   # API routes
│   │   │   └── page.tsx  # Main chat interface
│   │   └── components/  # React components
│   └── public/        # Static files
├── data/              # Immigration documents
│   └── documents/     # Source documents for RAG
└── scripts/           # Utility scripts
    └── rebuild_indexes.py  # Rebuild Pinecone indexes
```

## Tech Stack

- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **Backend**: Next.js API Routes (Edge Runtime)
- **AI/ML**: OpenAI API (GPT-4, Embeddings)
- **Vector Store**: Pinecone
- **Deployment**: Vercel

## Features

- 🤖 AI-powered immigration assistance
- 💬 Real-time chat interface
- 📚 Comprehensive visa information
- ⚡ Fast, serverless architecture
- 🎯 Accurate, context-aware responses

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/Rana-X/immi-ai.git
   cd immi-ai/immi-ai-app
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env.local
   # Add your API keys to .env.local
   ```

4. Run the development server:
   ```bash
   npm run dev
   ```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Environment Variables

Required environment variables:
- `OPENAI_API_KEY` - Your OpenAI API key
- `PINECONE_API_KEY` - Your Pinecone API key
- `PINECONE_ENVIRONMENT` - Pinecone environment
- `PINECONE_INDEX_NAME` - Name of your Pinecone index

## Deployment

The application is deployed on Vercel:

1. Push to GitHub
2. Connect to Vercel
3. Set environment variables
4. Deploy!

## Scripts

- `rebuild_indexes.py`: Rebuilds the Pinecone vector indexes with the latest documents
- `test_flow.py`: Tests the complete chat flow

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