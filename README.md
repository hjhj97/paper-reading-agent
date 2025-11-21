# Paper Reading Agent

AI-powered paper summarization and Q&A system using GPT-4o-mini, RAG (Retrieval-Augmented Generation), and Pinecone vector database.

## Features

- 📤 **PDF Upload**: Upload academic papers in PDF format
- 📝 **AI Summarization**: Generate comprehensive summaries using GPT models
- 🎯 **Custom Prompts**: Customize the summarization prompt to focus on specific aspects
- 💬 **RAG-based Q&A**: Ask questions about the paper and get contextual answers
- 🤖 **Multiple Models**: Choose from GPT-4o-mini (default), GPT-4o, or GPT-3.5-turbo
- 👍👎 **Feedback System**: Rate summaries to evaluate quality

## Tech Stack

### Backend

- **FastAPI**: High-performance Python web framework
- **OpenAI API**: GPT models for summarization and Q&A
- **LangChain**: Text splitting and embedding management
- **Pinecone**: Vector database for semantic search
- **PyPDF2**: PDF text extraction

### Frontend

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Axios**: HTTP client for API calls

## Project Structure

```
paper-reading-agent/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py      # API endpoints
│   │   ├── services/
│   │   │   ├── pdf_parser.py  # PDF text extraction
│   │   │   ├── llm_service.py # OpenAI integration
│   │   │   ├── rag_service.py # RAG with Pinecone
│   │   │   └── session_manager.py # Session management
│   │   ├── models/
│   │   │   └── schemas.py     # Pydantic models
│   │   ├── config.py          # Configuration
│   │   └── main.py            # FastAPI app
│   └── requirements.txt
└── frontend/                   # Next.js frontend
    ├── src/
    │   ├── app/
    │   │   ├── page.tsx       # Main page
    │   │   ├── layout.tsx     # Root layout
    │   │   └── globals.css    # Global styles
    │   ├── components/
    │   │   ├── PdfUploader.tsx
    │   │   ├── ModelSelector.tsx
    │   │   ├── SummaryDisplay.tsx
    │   │   └── ChatInterface.tsx
    │   └── lib/
    │       └── api.ts         # API client
    ├── package.json
    └── tsconfig.json
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 18+
- OpenAI API key
- Pinecone API key and environment

### Backend Setup

1. Navigate to the backend directory:

```bash
cd backend
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the `backend` directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment_here
PINECONE_INDEX_NAME=paper-reading-agent
DEFAULT_MODEL=gpt-4o-mini
```

5. Run the backend server:

```bash
uvicorn app.main:app --reload --port 8000
```

The backend API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Run the development server:

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Usage

1. **Select Model**: Choose your preferred AI model (GPT-4o-mini is the default)

2. **Upload PDF**: Click "Upload & Process" to upload a research paper PDF

3. **Generate Summary**:

   - Optionally add a custom prompt to guide the summarization
   - Click "Generate Summary" to get an AI-generated summary
   - Rate the summary quality with thumbs up/down

4. **Ask Questions**:
   - Once the summary is generated, the Q&A interface appears
   - Type your question about the paper
   - The system uses RAG to find relevant context and provide accurate answers

## API Endpoints

- `POST /api/upload` - Upload PDF and extract text
- `POST /api/summarize` - Generate paper summary
- `POST /api/ask` - Ask questions using RAG
- `POST /api/rate` - Rate summary quality
- `GET /api/models` - Get available models

## Architecture

### Session Management

- Sessions are stored in-memory (dictionary-based)
- Each uploaded PDF gets a unique session ID
- Session data includes: filename, extracted text, summary, rating
- Ready for database migration (repository pattern)

### RAG Implementation

1. **Document Processing**:

   - PDF text is split into chunks (1000 chars, 200 overlap)
   - Each chunk is embedded using OpenAI embeddings
   - Embeddings are stored in Pinecone with session metadata

2. **Question Answering**:
   - User question is embedded
   - Top 3 similar chunks are retrieved from Pinecone
   - Retrieved context is sent to GPT along with the question
   - GPT generates an answer based on the context

### Scalability Considerations

- Session data can be moved to PostgreSQL/MongoDB
- Pinecone handles vector storage at scale
- Stateless API design allows horizontal scaling

## Development

### Backend Development

```bash
cd backend
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm run dev
```

### Testing

- Backend API docs: http://localhost:8000/docs
- Test endpoints using the interactive Swagger UI

## Future Enhancements

- [ ] Persistent database for session storage
- [ ] User authentication and multi-user support
- [ ] Paper history and saved summaries
- [ ] Export summaries to PDF/Word
- [ ] Batch processing for multiple papers
- [ ] Citation extraction and formatting
- [ ] Multi-language support

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
