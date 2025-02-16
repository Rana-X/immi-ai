import { OpenAI } from 'openai';
import { Pinecone } from '@pinecone-database/pinecone';
import { NextResponse } from 'next/server';

// Initialize OpenAI
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY!,
});

// Initialize Pinecone
const pinecone = new Pinecone({
  apiKey: process.env.PINECONE_API_KEY!,
  environment: process.env.PINECONE_ENVIRONMENT!,
});

export const runtime = 'edge';

export async function POST(req: Request) {
  try {
    const { question } = await req.json();

    // Get embeddings for the question
    const embeddings = await openai.embeddings.create({
      model: "text-embedding-ada-002",
      input: question,
    });

    // Query Pinecone
    const index = pinecone.index(process.env.PINECONE_INDEX_NAME!);
    const queryResponse = await index.query({
      vector: embeddings.data[0].embedding,
      topK: 3,
      includeMetadata: true,
    });

    // Prepare context from relevant documents
    const context = queryResponse.matches
      .map((match) => match.metadata?.text || '')
      .join('\n');

    // Generate response using OpenAI
    const completion = await openai.chat.completions.create({
      model: "gpt-4-turbo-preview",
      messages: [
        {
          role: "system",
          content: `You are an expert immigration assistant. Use this context to answer the question: ${context}`,
        },
        { role: "user", content: question },
      ],
      temperature: 0.7,
      max_tokens: 500,
    });

    // Format response
    const response = {
      response: {
        overview: completion.choices[0].message.content,
        key_points: [],
        follow_up: [],
      },
      metadata: {
        sources: queryResponse.matches.map((match) => ({
          relevance_score: match.score,
        })),
      },
    };

    return NextResponse.json(response);
  } catch (error: any) {
    console.error('Error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
} 