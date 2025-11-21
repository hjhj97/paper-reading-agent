from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import (
    UploadResponse,
    SummarizeRequest,
    SummarizeResponse,
    AskRequest,
    AskResponse,
    RateRequest,
    RateResponse,
    ModelInfo
)
from app.services.pdf_parser import PDFParser
from app.services.session_manager import session_manager
from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from typing import List

router = APIRouter()
pdf_parser = PDFParser()


@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file and extract text
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Read file content
        content = await file.read()
        
        # Extract text from PDF
        text = await pdf_parser.extract_text_from_pdf(content)
        
        # Clean the text
        cleaned_text = pdf_parser.clean_text(text)
        
        # Create session
        session_id = session_manager.create_session(file.filename, cleaned_text)
        
        # Index document for RAG
        num_chunks = await rag_service.index_document(session_id, cleaned_text)
        
        return UploadResponse(
            session_id=session_id,
            filename=file.filename,
            text_length=len(cleaned_text),
            message=f"PDF uploaded successfully. Indexed {num_chunks} chunks."
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_paper(request: SummarizeRequest):
    """
    Summarize the paper from a session
    """
    # Check if session exists
    session = session_manager.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Get the paper text
        paper_text = session.text
        
        # Generate summary
        summary = await llm_service.summarize_paper(
            paper_text=paper_text,
            custom_prompt=request.custom_prompt,
            model=request.model
        )
        
        # Update session with summary
        session_manager.update_summary(request.session_id, summary)
        
        model_used = request.model or llm_service.default_model
        
        return SummarizeResponse(
            session_id=request.session_id,
            summary=summary,
            model=model_used
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    Ask a question about the paper using RAG
    """
    # Check if session exists
    session = session_manager.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Query relevant context using RAG
        context, sources = await rag_service.query_document(
            session_id=request.session_id,
            question=request.question,
            top_k=3
        )
        
        if not context:
            raise HTTPException(
                status_code=404,
                detail="No relevant context found for the question"
            )
        
        # Generate answer using LLM
        answer = await llm_service.answer_question(
            question=request.question,
            context=context,
            model=request.model
        )
        
        return AskResponse(
            session_id=request.session_id,
            question=request.question,
            answer=answer,
            sources=sources
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rate", response_model=RateResponse)
async def rate_summary(request: RateRequest):
    """
    Rate the summary (thumbs up or thumbs down)
    """
    # Check if session exists
    if not session_manager.session_exists(request.session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Validate rating
    if request.rating not in ["thumbs_up", "thumbs_down"]:
        raise HTTPException(
            status_code=400,
            detail="Rating must be 'thumbs_up' or 'thumbs_down'"
        )
    
    try:
        # Update rating
        success = session_manager.update_rating(request.session_id, request.rating)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update rating")
        
        return RateResponse(
            session_id=request.session_id,
            rating=request.rating,
            message="Rating saved successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models", response_model=List[ModelInfo])
async def get_models():
    """
    Get list of available LLM models
    """
    models = llm_service.get_available_models()
    return [ModelInfo(**model) for model in models]

