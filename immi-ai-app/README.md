# Immi.AI - Immigration Assistant

An intelligent assistant designed to help answer questions about US immigration and visa processes, powered by AI.

## Features

- 🤖 AI-powered immigration assistance
- 💬 Real-time chat interface
- 📚 Comprehensive visa information
- ⚡ Fast, serverless architecture
- 🎯 Accurate, context-aware responses

## Tech Stack

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- OpenAI API
- Pinecone Vector Database
- Vercel Edge Functions

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/immi-ai.git
   cd immi-ai
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

The application is deployed on Vercel. Each push to the main branch triggers an automatic deployment.

## Important Note

This is an informational tool only and does not provide legal advice. Please consult with immigration attorneys for legal counsel. 