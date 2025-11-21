# Setup Guide for Paper Reading Agent

This guide will help you set up and run the Paper Reading Agent from scratch.

## Step 1: Prerequisites

Make sure you have the following installed:

- Python 3.8 or higher
- Node.js 18 or higher
- npm or yarn package manager

## Step 2: Get API Keys

### OpenAI API Key

1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy and save it securely

### Pinecone API Key

1. Go to https://www.pinecone.io/
2. Sign up for a free account
3. Create a new project
4. Go to API Keys section
5. Copy your API key and environment (e.g., "us-west1-gcp")

## Step 3: Backend Setup

1. Open a terminal and navigate to the project directory:

```bash
cd paper-reading-agent/backend
```

2. Create a Python virtual environment:

```bash
python3 -m venv venv
```

3. Activate the virtual environment:

- **macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```
- **Windows**:
  ```bash
  venv\Scripts\activate
  ```

4. Install Python dependencies:

```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the `backend` directory:

```bash
touch .env
```

6. Edit the `.env` file and add your API keys:

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
PINECONE_API_KEY=your-pinecone-api-key-here
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=paper-reading-agent
DEFAULT_MODEL=gpt-4o-mini
```

7. Start the backend server:

```bash
uvicorn app.main:app --reload --port 8000
```

You should see output like:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

8. Verify the backend is running by opening http://localhost:8000/docs in your browser.
   You should see the API documentation.

## Step 4: Frontend Setup

1. Open a **new terminal** window and navigate to the frontend directory:

```bash
cd paper-reading-agent/frontend
```

2. Install Node.js dependencies:

```bash
npm install
```

3. Start the frontend development server:

```bash
npm run dev
```

You should see output like:

```
- Local:        http://localhost:3000
```

4. Open http://localhost:3000 in your browser.

## Step 5: Test the Application

1. **Select a Model**: The default GPT-4o-mini should be pre-selected.

2. **Upload a PDF**:

   - Click "Choose File" and select a PDF research paper
   - Click "Upload & Process"
   - Wait for the success message

3. **Generate Summary**:

   - Optionally, enter a custom prompt (e.g., "Focus on methodology")
   - Click "Generate Summary"
   - Wait for the AI to generate the summary (may take 10-30 seconds)

4. **Rate the Summary**:

   - Click 👍 or 👎 to rate the summary quality

5. **Ask Questions**:
   - Once summary is generated, the chat interface appears
   - Type a question about the paper (e.g., "What are the main findings?")
   - Press Enter or click "Ask"
   - View the AI's answer with sources

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'app'`

- **Solution**: Make sure you're in the `backend` directory and the virtual environment is activated.

**Problem**: `pydantic_settings not found`

- **Solution**: Update pip and reinstall: `pip install --upgrade pip && pip install -r requirements.txt`

**Problem**: `Pinecone connection error`

- **Solution**: Verify your Pinecone API key and environment are correct in the `.env` file.

**Problem**: `OpenAI API key invalid`

- **Solution**: Check that your OpenAI API key is correct and has credits available.

### Frontend Issues

**Problem**: `Cannot find module '@/lib/api'`

- **Solution**: Make sure all TypeScript files are created and run `npm install` again.

**Problem**: `CORS error when calling API`

- **Solution**: Ensure the backend is running on port 8000 and the frontend on port 3000.

**Problem**: `Page not loading`

- **Solution**: Clear browser cache and restart the dev server.

### API Issues

**Problem**: Upload fails

- **Solution**: Check that the file is a valid PDF and not corrupted.

**Problem**: Summary generation takes too long

- **Solution**: This is normal for large papers. Wait up to 1-2 minutes.

**Problem**: RAG queries return no results

- **Solution**: Ensure the PDF was successfully uploaded and indexed (check console logs).

## Next Steps

Once everything is working:

1. Try uploading different research papers
2. Experiment with custom prompts for different summary styles
3. Ask various questions to test the RAG functionality
4. Provide feedback on summary quality

## Stopping the Application

To stop the servers:

1. **Backend**: Press `Ctrl+C` in the backend terminal
2. **Frontend**: Press `Ctrl+C` in the frontend terminal

To deactivate the Python virtual environment:

```bash
deactivate
```

## Getting Help

If you encounter issues not covered here:

1. Check the backend logs in the terminal
2. Check the browser console (F12) for frontend errors
3. Review the API documentation at http://localhost:8000/docs
4. Ensure all environment variables are set correctly

## Production Deployment

This is a development setup. For production:

1. Use a proper database (PostgreSQL, MongoDB)
2. Add authentication and authorization
3. Use environment-specific configurations
4. Deploy backend to a cloud service (AWS, GCP, Heroku)
5. Deploy frontend to Vercel or Netlify
6. Use production-grade Pinecone plan
7. Implement rate limiting and caching
