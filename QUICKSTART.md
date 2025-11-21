# Quick Start Guide

Get the Paper Reading Agent up and running in 5 minutes!

## Prerequisites

- Python 3.8+
- Node.js 18+
- OpenAI API key
- Pinecone API key

## Quick Setup

### 1. Backend (Terminal 1)

```bash
# Navigate to backend
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
OPENAI_API_KEY=your_openai_key_here
PINECONE_API_KEY=your_pinecone_key_here
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=paper-reading-agent
DEFAULT_MODEL=gpt-4o-mini
EOF

# Start backend
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend (Terminal 2)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start frontend
npm run dev
```

### 3. Use the App

Open http://localhost:3000 in your browser!

1. Select a model (default: GPT-4o-mini)
2. Upload a PDF research paper
3. Generate summary
4. Ask questions about the paper

## Architecture Overview

```
User → Next.js Frontend → FastAPI Backend → OpenAI API
                                         ↓
                                    Pinecone (RAG)
```

## Key Features

- **PDF Upload**: Extract text from research papers
- **AI Summary**: Generate comprehensive summaries
- **Custom Prompts**: Guide the summarization
- **RAG Q&A**: Ask questions with context-aware answers
- **Rating System**: Evaluate summary quality

## Folder Structure

```
paper-reading-agent/
├── backend/          # FastAPI + Python
│   ├── app/
│   │   ├── api/     # Routes
│   │   ├── services/ # Business logic
│   │   └── models/   # Data models
│   └── requirements.txt
└── frontend/         # Next.js + React
    ├── src/
    │   ├── app/     # Pages
    │   └── components/ # UI components
    └── package.json
```

## Troubleshooting

**Backend not starting?**

- Check if virtual environment is activated
- Verify .env file exists with correct keys

**Frontend not loading?**

- Ensure backend is running on port 8000
- Clear browser cache

**API errors?**

- Verify API keys are valid
- Check you have OpenAI credits

## Next Steps

- Try different AI models
- Experiment with custom prompts
- Test RAG with complex questions
- Rate summaries to see the feedback system

For detailed setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)

For full documentation, see [README.md](README.md)
