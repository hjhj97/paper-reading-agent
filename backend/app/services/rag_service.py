from typing import List, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone, ServerlessSpec
from app.config import settings
import time


class RAGService:
    """Service for RAG (Retrieval-Augmented Generation) using Pinecone"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key
        )
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=settings.pinecone_api_key)
        self.index_name = settings.pinecone_index_name
        
        # Create index if it doesn't exist
        self._ensure_index_exists()
        
        # Get the index
        self.index = self.pc.Index(self.index_name)
        
        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def _ensure_index_exists(self):
        """Ensure Pinecone index exists, create if not"""
        try:
            existing_indexes = [index['name'] for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                self.pc.create_index(
                    name=self.index_name,
                    dimension=1536,  # OpenAI embeddings dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=settings.pinecone_environment
                    )
                )
                # Wait for index to be ready
                time.sleep(1)
        except Exception as e:
            print(f"Warning: Could not ensure index exists: {str(e)}")
    
    async def index_document(self, session_id: str, text: str) -> int:
        """
        Split document into chunks and index them in Pinecone
        
        Args:
            session_id: Session identifier to namespace the vectors
            text: Full text of the document
            
        Returns:
            Number of chunks indexed
        """
        # Split text into chunks
        chunks = self.text_splitter.split_text(text)
        
        # Generate embeddings for each chunk
        vectors_to_upsert = []
        
        for i, chunk in enumerate(chunks):
            # Generate embedding
            embedding = await self.embeddings.aembed_query(chunk)
            
            # Create vector ID with session prefix
            vector_id = f"{session_id}_{i}"
            
            # Prepare metadata
            metadata = {
                "session_id": session_id,
                "chunk_index": i,
                "text": chunk
            }
            
            vectors_to_upsert.append({
                "id": vector_id,
                "values": embedding,
                "metadata": metadata
            })
        
        # Upsert vectors to Pinecone
        if vectors_to_upsert:
            self.index.upsert(vectors=vectors_to_upsert)
        
        return len(chunks)
    
    async def query_document(
        self,
        session_id: str,
        question: str,
        top_k: int = 3
    ) -> Tuple[str, List[str]]:
        """
        Query the document using semantic search
        
        Args:
            session_id: Session identifier to filter vectors
            question: User's question
            top_k: Number of top chunks to retrieve
            
        Returns:
            Tuple of (combined context, list of source chunks)
        """
        # Check if question is about metadata (title, author, abstract)
        metadata_keywords = ['title', 'author', 'abstract', 'introduction', 'name']
        question_lower = question.lower()
        is_metadata_question = any(keyword in question_lower for keyword in metadata_keywords)
        
        context_chunks = []
        sources = []
        chunk_indices_seen = set()
        
        # If asking about metadata, include first few chunks
        if is_metadata_question:
            # Fetch first 3 chunks by chunk_index
            for chunk_idx in range(3):
                results = self.index.query(
                    vector=[0.0] * 1536,  # Dummy vector
                    top_k=10,
                    filter={
                        "session_id": session_id,
                        "chunk_index": chunk_idx
                    },
                    include_metadata=True
                )
                
                if results.matches:
                    match = results.matches[0]
                    if match.metadata and "text" in match.metadata:
                        chunk_text = match.metadata["text"]
                        context_chunks.append(chunk_text)
                        sources.append(f"Chunk {chunk_idx}")
                        chunk_indices_seen.add(chunk_idx)
        
        # Generate embedding for the question
        question_embedding = await self.embeddings.aembed_query(question)
        
        # Query Pinecone with semantic search
        results = self.index.query(
            vector=question_embedding,
            top_k=top_k,
            filter={"session_id": session_id},
            include_metadata=True
        )
        
        # Add semantic search results (avoid duplicates)
        for match in results.matches:
            if match.metadata and "text" in match.metadata:
                chunk_idx = match.metadata.get('chunk_index', -1)
                if chunk_idx not in chunk_indices_seen:
                    chunk_text = match.metadata["text"]
                    context_chunks.append(chunk_text)
                    sources.append(f"Chunk {chunk_idx}")
                    chunk_indices_seen.add(chunk_idx)
        
        # Combine chunks into context
        context = "\n\n".join(context_chunks)
        
        return context, sources
    
    def delete_session_vectors(self, session_id: str):
        """
        Delete all vectors for a session
        
        Args:
            session_id: Session identifier
        """
        # Delete by filter (if supported) or by IDs
        try:
            self.index.delete(filter={"session_id": session_id})
        except Exception as e:
            print(f"Warning: Could not delete vectors for session {session_id}: {str(e)}")


# Global RAG service instance
rag_service = RAGService()

