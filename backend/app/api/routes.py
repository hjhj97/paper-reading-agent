from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from app.models.schemas import (
    UploadResponse,
    SummarizeRequest,
    SummarizeResponse,
    StorylineRequest,
    StorylineResponse,
    AskRequest,
    AskResponse,
    RateRequest,
    RateResponse,
    ModelInfo,
    SessionDetailResponse,
    EvaluateRequest,
    EvaluateResponse,
    EvaluationScores
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
        
        # Create session with PDF content
        session_id = session_manager.create_session(
            filename=file.filename,
            text=cleaned_text,
            pdf_content=content  # Save PDF file
        )
        
        # Extract metadata (title, authors, year)
        metadata = await llm_service.extract_metadata(cleaned_text)
        session_manager.update_metadata(
            session_id,
            title=metadata["title"],
            authors=metadata["authors"],
            year=metadata["year"]
        )
        
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
    Automatically evaluates the summary and logs to Langfuse
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

        # Automatically evaluate the summary and log to Langfuse
        try:
            evaluation = await llm_service.evaluate_summary(
                original_text=paper_text,
                summary=summary,
                model=model_used,
                session_id=request.session_id
            )
            print(f"✅ Summary evaluated - Overall Score: {evaluation['overall_score']}/10")
            print(f"   Scores: F={evaluation['faithfulness']}, C={evaluation['completeness']}, "
                  f"Co={evaluation['conciseness']}, Ch={evaluation['coherence']}, Cl={evaluation['clarity']}")
        except Exception as eval_error:
            # Don't fail the summarization if evaluation fails
            print(f"⚠️  Summary evaluation failed (non-critical): {eval_error}")

        return SummarizeResponse(
            session_id=request.session_id,
            summary=summary,
            model=model_used
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/storyline", response_model=StorylineResponse)
async def analyze_storyline(request: StorylineRequest):
    """
    Analyze the paper's storyline/narrative flow
    """
    # Check if session exists
    session = session_manager.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Get the paper text
        paper_text = session.text
        
        # Generate storyline analysis
        storyline = await llm_service.analyze_storyline(
            paper_text=paper_text,
            model=request.model,
            language=request.language or "en"
        )
        
        # Update session with storyline
        session_manager.update_storyline(request.session_id, storyline)
        
        model_used = request.model or llm_service.default_model
        
        return StorylineResponse(
            session_id=request.session_id,
            storyline=storyline,
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


@router.post("/ask/stream")
async def ask_question_stream(request: AskRequest):
    """
    Ask a question about the paper using RAG with streaming response
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
        
        # Stream answer using LLM
        def generate():
            try:
                # Send sources first
                import json
                yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"
                
                # Then stream the answer
                for chunk in llm_service.answer_question_stream(
                    question=request.question,
                    context=context,
                    model=request.model
                ):
                    yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
                
                # Send done signal
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
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


@router.get("/sessions")
async def get_all_sessions():
    """
    Get all paper sessions (history)
    """
    sessions = session_manager.get_all_sessions()
    
    return [
        {
            "session_id": session.session_id,
            "filename": session.filename,
            "has_pdf": session.pdf_path is not None,
            "has_summary": session.summary is not None,
            "title": session.title,
            "authors": session.authors,
            "year": session.year,
            "created_at": session.created_at.isoformat(),
            "text_length": len(session.text)
        }
        for session in sessions
    ]


@router.get("/session/{session_id}", response_model=SessionDetailResponse)
async def get_session_detail(session_id: str):
    """
    Get session detail including PDF text content
    """
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    has_pdf = session.pdf_path is not None and session_manager.get_pdf_path(session_id) is not None
    
    return SessionDetailResponse(
        session_id=session.session_id,
        filename=session.filename,
        text=session.text,
        has_pdf=has_pdf,
        title=session.title,
        authors=session.authors,
        year=session.year,
        summary=session.summary,
        storyline=session.storyline,
        rating=session.rating,
        created_at=session.created_at.isoformat()
    )


@router.get("/session/{session_id}/pdf")
async def get_session_pdf(session_id: str):
    """
    Get PDF file for a session
    """
    pdf_path = session_manager.get_pdf_path(session_id)
    if not pdf_path:
        raise HTTPException(status_code=404, detail="PDF not found")

    session = session_manager.get_session(session_id)
    filename = session.filename if session else "paper.pdf"

    from starlette.responses import Response
    import os

    # Read the PDF file
    with open(pdf_path, "rb") as f:
        pdf_content = f.read()

    # Return PDF with inline disposition
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{filename}"'
        }
    )


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_summary(request: EvaluateRequest):
    """
    Evaluate summary quality using LLM-as-a-judge approach
    All evaluations are automatically logged to Langfuse with session tracking
    """
    # Check if session exists
    session = session_manager.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Check if summary exists
    if not session.summary:
        raise HTTPException(
            status_code=400,
            detail="No summary found for this session. Please generate a summary first."
        )

    try:
        # Evaluate the summary with Langfuse tracing
        evaluation = await llm_service.evaluate_summary(
            original_text=session.text,
            summary=session.summary,
            model=request.model,
            session_id=request.session_id  # This enables Langfuse session tracking
        )

        model_used = request.model or llm_service.default_model

        # Create response with evaluation scores
        evaluation_scores = EvaluationScores(**evaluation)

        return EvaluateResponse(
            session_id=request.session_id,
            evaluation=evaluation_scores,
            model=model_used
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
