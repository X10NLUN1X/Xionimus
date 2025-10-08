"""
RAG (Retrieval-Augmented Generation) API endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

from ..core.rag_system import RAGSystem

router = APIRouter(prefix="/api/rag", tags=["rag"])
logger = logging.getLogger(__name__)

# Initialize RAG system
rag_system = RAGSystem()

class AddMessageRequest(BaseModel):
    session_id: str
    message: str
    role: str
    metadata: Optional[Dict[str, Any]] = None

class AddDocumentRequest(BaseModel):
    content: str
    title: str
    metadata: Optional[Dict[str, Any]] = None

class SearchRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    limit: int = 5

class ContextRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    include_documents: bool = True
    max_context_length: int = 2000

@router.get("/stats")
async def get_rag_stats():
    """Get RAG system statistics"""
    return rag_system.get_stats()

@router.post("/message/add")
async def add_message(request: AddMessageRequest):
    """Add a chat message to RAG for future retrieval"""
    try:
        doc_id = rag_system.add_message_to_history(
            session_id=request.session_id,
            message=request.message,
            role=request.role,
            metadata=request.metadata
        )
        
        return {
            "status": "success",
            "doc_id": doc_id,
            "message": "Message added to RAG system"
        }
    except Exception as e:
        logger.error(f"Error adding message to RAG: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/document/add")
async def add_document(request: AddDocumentRequest):
    """Add a document to RAG"""
    try:
        doc_id = rag_system.add_document(
            content=request.content,
            title=request.title,
            metadata=request.metadata
        )
        
        return {
            "status": "success",
            "doc_id": doc_id,
            "message": "Document added to RAG system"
        }
    except Exception as e:
        logger.error(f"Error adding document to RAG: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search/messages")
async def search_messages(request: SearchRequest):
    """Search for relevant chat messages"""
    try:
        results = rag_system.search_relevant_messages(
            query=request.query,
            session_id=request.session_id,
            limit=request.limit
        )
        
        return {
            "status": "success",
            "query": request.query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Error searching messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search/documents")
async def search_documents(request: SearchRequest):
    """Search for relevant documents"""
    try:
        results = rag_system.search_documents(
            query=request.query,
            limit=request.limit
        )
        
        return {
            "status": "success",
            "query": request.query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/context")
async def get_context(request: ContextRequest):
    """Get relevant context for a query"""
    try:
        context = rag_system.get_context_for_query(
            query=request.query,
            session_id=request.session_id,
            include_documents=request.include_documents,
            max_context_length=request.max_context_length
        )
        
        return {
            "status": "success",
            "query": request.query,
            "context": context,
            "length": len(context)
        }
    except Exception as e:
        logger.error(f"Error getting context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear RAG history for a session"""
    try:
        count = rag_system.clear_session_history(session_id)
        
        return {
            "status": "success",
            "session_id": session_id,
            "messages_deleted": count
        }
    except Exception as e:
        logger.error(f"Error clearing session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset")
async def reset_rag():
    """Reset RAG system (delete all data) - USE WITH CAUTION"""
    try:
        rag_system.reset()
        
        return {
            "status": "success",
            "message": "RAG system reset - all data deleted"
        }
    except Exception as e:
        logger.error(f"Error resetting RAG: {e}")
        raise HTTPException(status_code=500, detail=str(e))
