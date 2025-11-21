import uuid
from datetime import datetime
from typing import Dict, Optional
from app.models.schemas import SessionData


class SessionManager:
    """In-memory session manager for storing paper data"""
    
    def __init__(self):
        self._sessions: Dict[str, SessionData] = {}
    
    def create_session(self, filename: str, text: str) -> str:
        """
        Create a new session
        
        Args:
            filename: Name of the uploaded PDF file
            text: Extracted text from the PDF
            
        Returns:
            Generated session ID
        """
        session_id = str(uuid.uuid4())
        session_data = SessionData(
            session_id=session_id,
            filename=filename,
            text=text,
            created_at=datetime.now()
        )
        self._sessions[session_id] = session_data
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionData]:
        """
        Get session data by ID
        
        Args:
            session_id: Session identifier
            
        Returns:
            SessionData if found, None otherwise
        """
        return self._sessions.get(session_id)
    
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
        Delete a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful, False if session not found
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False


# Global session manager instance
session_manager = SessionManager()

