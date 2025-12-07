import uuid
import os
from datetime import datetime
from typing import Dict, Optional
from app.models.schemas import SessionData

# Upload directory for PDF files
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")


class SessionManager:
    """In-memory session manager for storing paper data"""
    
    def __init__(self):
        self._sessions: Dict[str, SessionData] = {}
        # Ensure upload directory exists
        os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    def create_session(self, filename: str, text: str, pdf_content: Optional[bytes] = None) -> str:
        """
        Create a new session
        
        Args:
            filename: Name of the uploaded PDF file
            text: Extracted text from the PDF
            pdf_content: Raw PDF file content (optional)
            
        Returns:
            Generated session ID
        """
        session_id = str(uuid.uuid4())
        
        # Save PDF file if content provided
        pdf_path = None
        if pdf_content:
            pdf_path = self._save_pdf(session_id, pdf_content)
        
        session_data = SessionData(
            session_id=session_id,
            filename=filename,
            text=text,
            pdf_path=pdf_path,
            created_at=datetime.now()
        )
        self._sessions[session_id] = session_data
        return session_id
    
    def _save_pdf(self, session_id: str, content: bytes) -> str:
        """
        Save PDF file to disk
        
        Args:
            session_id: Session identifier
            content: PDF file content
            
        Returns:
            Path to saved PDF file
        """
        pdf_filename = f"{session_id}.pdf"
        pdf_path = os.path.join(UPLOAD_DIR, pdf_filename)
        
        with open(pdf_path, "wb") as f:
            f.write(content)
        
        return pdf_path
    
    def get_session(self, session_id: str) -> Optional[SessionData]:
        """
        Get session data by ID
        
        Args:
            session_id: Session identifier
            
        Returns:
            SessionData if found, None otherwise
        """
        return self._sessions.get(session_id)
    
    def get_all_sessions(self) -> list[SessionData]:
        """
        Get all sessions sorted by creation date (newest first)
        
        Returns:
            List of all SessionData objects
        """
        sessions = list(self._sessions.values())
        sessions.sort(key=lambda x: x.created_at, reverse=True)
        return sessions
    
    def get_pdf_path(self, session_id: str) -> Optional[str]:
        """
        Get PDF file path for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            PDF file path if exists, None otherwise
        """
        session = self._sessions.get(session_id)
        if session and session.pdf_path and os.path.exists(session.pdf_path):
            return session.pdf_path
        return None
    
    def update_summary(self, session_id: str, summary: str) -> bool:
        """
        Update summary for a session
        
        Args:
            session_id: Session identifier
            summary: Generated summary text
            
        Returns:
            True if successful, False if session not found
        """
        session = self._sessions.get(session_id)
        if session:
            session.summary = summary
            return True
        return False
    
    def update_storyline(self, session_id: str, storyline: str) -> bool:
        """
        Update storyline analysis for a session
        
        Args:
            session_id: Session identifier
            storyline: Generated storyline analysis
            
        Returns:
            True if successful, False if session not found
        """
        session = self._sessions.get(session_id)
        if session:
            session.storyline = storyline
            return True
        return False
    
    def update_metadata(self, session_id: str, title: str, authors: str, year: str) -> bool:
        """
        Update metadata (title, authors, year) for a session
        
        Args:
            session_id: Session identifier
            title: Paper title
            authors: Paper authors
            year: Publication year
            
        Returns:
            True if successful, False if session not found
        """
        session = self._sessions.get(session_id)
        if session:
            session.title = title
            session.authors = authors
            session.year = year
            return True
        return False
    
    def update_rating(self, session_id: str, rating: str) -> bool:
        """
        Update rating for a session
        
        Args:
            session_id: Session identifier
            rating: Rating value (thumbs_up or thumbs_down)
            
        Returns:
            True if successful, False if session not found
        """
        session = self._sessions.get(session_id)
        if session:
            session.rating = rating
            return True
        return False
    
    def session_exists(self, session_id: str) -> bool:
        """
        Check if session exists
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session exists, False otherwise
        """
        return session_id in self._sessions
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and its PDF file
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful, False if session not found
        """
        if session_id in self._sessions:
            session = self._sessions[session_id]
            # Delete PDF file if exists
            if session.pdf_path and os.path.exists(session.pdf_path):
                try:
                    os.remove(session.pdf_path)
                except Exception:
                    pass
            del self._sessions[session_id]
            return True
        return False


# Global session manager instance
session_manager = SessionManager()
