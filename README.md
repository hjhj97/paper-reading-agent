# 📄 Paper Reading Agent

AI-powered paper summarization and Q&A system using GPT-4o-mini, RAG (Retrieval-Augmented Generation), and Pinecone vector database.

## ✨ Features

### Core Features

- 📤 **PDF Upload & Processing**: Upload academic papers in PDF format with automatic text extraction
- 📊 **Metadata Extraction**: Automatically extracts paper title, authors, and publication year using LLM
- 📝 **AI Summarization**: Generate comprehensive summaries with structured sections (Overview, Methodology, Findings, etc.)
- 📖 **Storyline Analysis**: Analyze paper's narrative flow (problem statement, limitations, methodology, results)
- 💬 **RAG-based Q&A with Streaming**: Ask questions and get real-time streaming responses with contextual answers
- 🖼️ **Native PDF Viewer**: View original PDF with full formatting using react-pdf-viewer
- 📐 **LaTeX Rendering**: Display mathematical equations beautifully rendered in markdown
- 🌍 **Multi-language Support**: Choose between Korean and English for AI responses and UI

### User Experience

- 🤖 **Model Selection**: Choose from GPT-4o-mini (default) or GPT-5-mini
- 👍👎 **Feedback System**: Rate summaries to evaluate quality
- 📜 **Session History**: View all previously uploaded papers and their summaries
- 🎨 **Modern UI**: Beautiful interface with Tailwind CSS and shadcn/ui components
- ⚡ **Auto-summarization**: Papers are automatically summarized upon upload

## 🛠️ Tech Stack

### Backend

- **FastAPI**: High-performance Python web framework with async support
- **OpenAI API**: GPT-4o-mini/GPT-5-mini for summarization, Q&A, and metadata extraction
- **LangChain**: Advanced text splitting and embedding management
- **Pinecone**: Cloud-native vector database for semantic search and RAG
- **PyPDF2**: Robust PDF text extraction
- **Server-Sent Events (SSE)**: Real-time streaming responses

### Frontend

- **Next.js 14**: React framework with App Router and standalone build
- **TypeScript**: Type-safe JavaScript for better DX
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: High-quality, accessible React components
- **react-markdown**: Markdown rendering with plugin support
- **react-pdf-viewer**: Native-like PDF viewing experience
- **KaTeX**: Beautiful LaTeX math rendering
- **Axios**: HTTP client with streaming support

### DevOps & Deployment

- **Docker & Docker Compose**: Containerized deployment
- **Multi-stage builds**: Optimized production images
- **Environment-based configuration**: Easy deployment across environments

## 📁 Project Structure

```
paper-reading-agent/
├── backend/                         # FastAPI backend
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py           # API endpoints (upload, summarize, ask, storyline, etc.)
│   │   ├── services/
│   │   │   ├── pdf_parser.py       # PDF text extraction
│   │   │   ├── llm_service.py      # OpenAI integration (chat, streaming, metadata)
│   │   │   ├── rag_service.py      # RAG with Pinecone (hybrid search)
│   │   │   └── session_manager.py  # In-memory session management
│   │   ├── models/
│   │   │   └── schemas.py          # Pydantic models for requests/responses
│   │   ├── config.py               # Environment configuration
│   │   └── main.py                 # FastAPI app with CORS
│   ├── uploads/                     # Temporary PDF storage (volume mounted)
│   ├── requirements.txt
│   ├── Dockerfile                   # Backend Docker image
│   └── .dockerignore
├── frontend/                        # Next.js frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx            # Main upload page
│   │   │   ├── history/
│   │   │   │   └── page.tsx        # Session history page
│   │   │   ├── paper/[sessionId]/
│   │   │   │   └── page.tsx        # Paper detail page
│   │   │   ├── layout.tsx          # Root layout with KaTeX CSS
│   │   │   └── globals.css         # Global styles (Tailwind + custom)
│   │   ├── components/
│   │   │   ├── PdfUploader.tsx     # Drag-and-drop PDF uploader
│   │   │   ├── PdfViewer.tsx       # react-pdf-viewer integration
│   │   │   ├── ModelSelector.tsx   # Model selection dropdown
│   │   │   ├── LanguageSelector.tsx # Language selection
│   │   │   ├── SummaryDisplay.tsx  # Summary with markdown & LaTeX
│   │   │   ├── StorylineDisplay.tsx # Storyline analysis display
│   │   │   ├── ChatInterface.tsx   # RAG Q&A with streaming
│   │   │   └── ui/                 # shadcn/ui components
│   │   │       ├── button.tsx
│   │   │       ├── card.tsx
│   │   │       ├── input.tsx
│   │   │       ├── select.tsx
│   │   │       └── textarea.tsx
│   │   └── lib/
│   │       ├── api.ts              # API client with streaming support
│   │       ├── mathUtils.ts        # LaTeX conversion utilities
│   │       └── utils.ts            # shadcn/ui utilities
│   ├── Dockerfile                   # Frontend Docker image (multi-stage)
│   ├── .dockerignore
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── next.config.js              # Next.js config with standalone output
├── docker-compose.yml               # Docker orchestration
├── .env.example                     # Environment variables template
├── .gitignore
├── README.md
├── DEPLOYMENT.md                    # Detailed deployment guide
└── QUICKSTART.md                    # Quick setup guide
```

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (recommended) OR
- **Python 3.12+** and **Node.js 20+**
- OpenAI API key
- Pinecone API key and environment (with index dimension=1536)

### Option 1: Docker Deployment (Recommended)

1. Clone the repository:

```bash
git clone <your-repo-url>
cd paper-reading-agent
```

2. Create `.env` file:

```bash
cp .env.example .env
nano .env  # Add your API keys
```

3. Run with Docker Compose:

```bash
docker compose up -d --build
```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/docs

**See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions (AWS, EC2, ECS, etc.)**

### Option 2: Local Development Setup

#### Backend Setup

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

4. Create `backend/app/config.py` or set environment variables:

```bash
export OPENAI_API_KEY=your_openai_api_key_here
export PINECONE_API_KEY=your_pinecone_api_key_here
export PINECONE_ENVIRONMENT=your_pinecone_environment_here
export PINECONE_INDEX_NAME=paper-reading-agent
export DEFAULT_MODEL=gpt-4o-mini
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

## 💡 Usage

### Main Workflow

1. **Configure Settings** (Main Page)

   - Select AI model: GPT-4o-mini (default) or GPT-5-mini
   - Choose language: English or Korean (한국어)

2. **Upload PDF**

   - Drag and drop or click to upload a research paper
   - System automatically:
     - Extracts text from PDF
     - Extracts metadata (title, authors, year)
     - Creates vector embeddings for RAG
     - Stores PDF for viewing

3. **View Paper Details**

   - See paper metadata (title, authors, year)
   - View original PDF with native formatting
   - Toggle between PDF view and raw text

4. **Storyline Analysis**

   - Automatically analyzes paper's narrative flow
   - Shows: Problem statement → Limitations → Methodology → Results
   - ~600 characters structured summary

5. **Comprehensive Summary**

   - Auto-generated detailed summary with sections:
     - Overview & Research Objectives
     - Methodology & Key Findings
     - Conclusions & Implications
     - Limitations & Future Work
   - Rendered with markdown and LaTeX support
   - Rate quality with thumbs up/down

6. **Interactive Q&A**

   - Ask questions about the paper in natural language
   - Get streaming responses with typing animation
   - RAG retrieves relevant context for accurate answers
   - LaTeX equations rendered automatically
   - Examples: "What is the main contribution?", "Who are the authors?"

7. **Session History**
   - View all previously uploaded papers
   - Quick access to past summaries
   - Resume analysis from any session

## 🔌 API Endpoints

| Method | Endpoint                | Description                                     |
| ------ | ----------------------- | ----------------------------------------------- |
| `POST` | `/api/upload`           | Upload PDF, extract text, and create embeddings |
| `POST` | `/api/summarize`        | Generate comprehensive paper summary            |
| `POST` | `/api/storyline`        | Analyze paper's narrative flow                  |
| `POST` | `/api/ask`              | Ask questions using RAG (legacy)                |
| `POST` | `/api/ask/stream`       | Ask questions with streaming responses (SSE)    |
| `POST` | `/api/rate`             | Rate summary quality (thumbs up/down)           |
| `GET`  | `/api/models`           | Get available AI models                         |
| `GET`  | `/api/sessions`         | Get all session history                         |
| `GET`  | `/api/session/{id}`     | Get specific session details                    |
| `GET`  | `/api/session/{id}/pdf` | Get PDF file for viewing                        |

**Interactive API Documentation**: http://localhost:8000/docs

## 🏗️ Architecture

### Session Management

- **In-memory storage** (dictionary-based) for demo/prototype
- Each uploaded PDF gets a unique UUID session ID
- Session data includes:
  - Paper metadata (title, authors, year)
  - Extracted text and PDF file path
  - Summary and storyline analysis
  - User ratings and timestamps
- **Ready for database migration** (repository pattern design)
- PDF files stored in `uploads/` directory (Docker volume-mounted)

### RAG Implementation

#### 1. Document Processing Pipeline

```
PDF Upload → Text Extraction → Chunking → Embedding → Vector Storage
```

- PDF text split into chunks (1000 characters, 200 overlap)
- OpenAI `text-embedding-ada-002` generates embeddings (dimension=1536)
- Embeddings stored in Pinecone with session metadata
- Each chunk tagged with session ID for filtering

#### 2. Hybrid Search Strategy

- **Semantic Search**: User question embedded and matched against vectors
- **Metadata Boost**: Questions about title/authors automatically include first chunks
- Top 3 most relevant chunks retrieved
- Context passed to GPT with streaming support

#### 3. Streaming Response

```
User Question → Embedding → Vector Search → Context Building → GPT Streaming → Frontend
```

- Server-Sent Events (SSE) for real-time output
- Token-by-token rendering for better UX
- React state management prevents duplicate rendering

### LLM Integration

#### Multi-Purpose LLM Tasks

1. **Metadata Extraction**: Parse title, authors, year from paper header
2. **Comprehensive Summary**: Structured academic paper summary
3. **Storyline Analysis**: Narrative flow in ~600 characters
4. **RAG Q&A**: Context-aware question answering

#### Prompt Engineering

- System prompts optimized for each task type
- Language-specific instructions (Korean/English)
- LaTeX formatting instructions for mathematical content
- Structured output format enforcement

### Scalability & Production Readiness

#### Current Design (Demo/MVP)

- ✅ In-memory session storage
- ✅ Single-instance deployment
- ✅ Local file storage for PDFs
- ✅ CORS configured for development/production

#### Production Migration Path

- 📦 **Database**: PostgreSQL/MongoDB for session persistence
- 📦 **File Storage**: AWS S3 / Google Cloud Storage for PDFs
- 📦 **Caching**: Redis for session data and rate limiting
- 📦 **Queue**: Celery/RQ for async processing
- 📦 **Load Balancer**: Nginx + multiple backend instances
- 📦 **Monitoring**: CloudWatch, Prometheus, or Datadog

#### Stateless Design Benefits

- Horizontal scaling ready
- Docker containerization
- Environment-based configuration
- Health check endpoints

## 🔧 Development

### Local Development

**Backend** (Terminal 1):

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Frontend** (Terminal 2):

```bash
cd frontend
npm run dev
```

### Docker Development

```bash
# Build and run in development mode
docker compose up --build

# View logs
docker compose logs -f

# Restart specific service
docker compose restart backend

# Rebuild without cache
docker compose build --no-cache

# Stop all services
docker compose down
```

### Testing

**Interactive API Testing**:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Manual Testing Flow**:

1. Upload a sample PDF
2. Check `/api/sessions` to see all sessions
3. Visit paper detail page: `/paper/{session_id}`
4. Test streaming Q&A in chat interface
5. Check LaTeX rendering with mathematical papers

### Environment Variables

Create `.env` file in project root:

```bash
# OpenAI (Required)
OPENAI_API_KEY=sk-...

# Pinecone (Required)
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=gcp-starter
PINECONE_INDEX_NAME=paper-reading-agent

# Optional: Custom CORS origins
ALLOWED_ORIGINS=http://localhost:3000,http://0.0.0.0:3000

# Optional: Frontend API URL (for Docker)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Troubleshooting

**CORS Errors**:

- Check `ALLOWED_ORIGINS` in backend
- Ensure frontend is accessing correct API URL

**Module Not Found Errors**:

- Ensure `frontend/src/lib/` is committed to Git (not ignored)
- Check `.gitignore` doesn't exclude `lib/` globally

**Docker Build Errors**:

- Clear Docker cache: `docker system prune -a`
- Check `.dockerignore` files
- Ensure all source files are included in Git

## 🔮 Future Enhancements

### High Priority

- [ ] **Database Integration**: PostgreSQL/MongoDB for persistent session storage
- [ ] **User Authentication**: Multi-user support with JWT/OAuth
- [ ] **Cloud Storage**: AWS S3 / GCS for PDF files
- [ ] **Redis Caching**: Session caching and rate limiting
- [ ] **Async Processing**: Background jobs for large PDFs

### Features

- [ ] **Export Functionality**: Export summaries to PDF/Word/Markdown
- [ ] **Batch Processing**: Upload and process multiple papers simultaneously
- [ ] **Citation Extraction**: Automatic reference parsing and BibTeX generation
- [ ] **Paper Comparison**: Compare multiple papers side-by-side
- [ ] **Collaborative Annotations**: Shared notes and highlights
- [ ] **Advanced Search**: Full-text search across all uploaded papers

### Infrastructure

- [ ] **Kubernetes Deployment**: K8s manifests for production
- [ ] **CI/CD Pipeline**: GitHub Actions for automated testing and deployment
- [ ] **Monitoring & Logging**: ELK stack or CloudWatch integration
- [ ] **Performance Optimization**: Caching strategies and CDN integration
- [ ] **API Rate Limiting**: Prevent abuse and manage costs

## 🎯 Key Features Explained

### LaTeX Rendering

- Automatically detects LaTeX in AI responses
- Supports both inline `$...$` and block `$$...$$` equations
- Uses KaTeX for fast, beautiful rendering
- Example: `$$E = mc^2$$` renders as proper mathematical notation

### Streaming Responses

- Real-time token-by-token output using Server-Sent Events
- Typing animation effect for better UX
- Prevents UI blocking during long responses
- Immediate feedback for user engagement

### Hybrid RAG Search

- Semantic search for general questions
- Metadata-aware search for specific queries (title, authors)
- Automatically includes paper header for context
- Top-k retrieval with configurable parameters

### Metadata Extraction

- LLM-powered parsing of paper headers
- Extracts: title, authors, publication year
- Handles various paper formats
- Fallback to "Unknown" for missing data

## 📚 Documentation

- **[DEPLOYMENT.md](./DEPLOYMENT.md)**: Complete deployment guide for AWS EC2, ECS, Lightsail
- **[QUICKSTART.md](./QUICKSTART.md)**: Quick setup instructions for local development

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Guidelines

1. Follow existing code style (ESLint, Black)
2. Add type hints for Python code
3. Write descriptive commit messages
4. Test locally before submitting PR
5. Update documentation for new features

## 📝 License

MIT License - feel free to use this project for learning, research, or commercial purposes.

## 🙏 Acknowledgments

- **OpenAI** for powerful GPT models
- **Pinecone** for scalable vector database
- **Vercel** for Next.js framework
- **shadcn/ui** for beautiful UI components

## 📧 Support

For issues, questions, or suggestions:

- Open an issue on GitHub
- Check existing issues for similar problems
- Provide detailed error messages and logs

---

**Built with ❤️ for researchers and academics**
