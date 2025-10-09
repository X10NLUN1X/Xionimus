"""
Local RAG (Retrieval-Augmented Generation) System using ChromaDB
Provides long-term memory and context for Xionimus AI
"""

import logging
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)

class RAGSystem:
    """Local RAG system using ChromaDB for document storage and retrieval"""
    
    def __init__(self, persist_directory: str = "~/.xionimus_ai/chroma_db"):
        """
        Initialize RAG system with ChromaDB
        
        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        self.persist_dir = Path(persist_directory).expanduser()
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Use sentence transformers for embeddings (local, no API needed)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"  # Small, fast, good quality
        )
        
        # Get or create collections
        self.chat_collection = self._get_or_create_collection("chat_history")
        self.docs_collection = self._get_or_create_collection("documents")
        
        logger.info(f"RAG System initialized at {self.persist_dir}")
    
    def _get_or_create_collection(self, name: str):
        """Get or create a ChromaDB collection"""
        try:
            return self.client.get_collection(
                name=name,
                embedding_function=self.embedding_function
            )
        except Exception:
            # Collection doesn't exist, create it
            return self.client.create_collection(
                name=name,
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
    
    def add_message_to_history(
        self,
        session_id: str,
        message: str,
        role: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a chat message to the RAG system for future retrieval
        
        Args:
            session_id: Session ID
            message: Message content
            role: Message role (user/assistant)
            metadata: Additional metadata
            
        Returns:
            Document ID
        """
        try:
            doc_id = str(uuid.uuid4())
            
            meta = {
                "session_id": session_id,
                "role": role,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                **(metadata or {})
            }
            
            self.chat_collection.add(
                documents=[message],
                metadatas=[meta],
                ids=[doc_id]
            )
            
            logger.info(f"Added message to RAG: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error adding message to RAG: {e}")
            return ""
    
    def add_document(
        self,
        content: str,
        title: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a document to the RAG system
        
        Args:
            content: Document content
            title: Document title
            metadata: Additional metadata
            
        Returns:
            Document ID
        """
        try:
            doc_id = str(uuid.uuid4())
            
            meta = {
                "title": title,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                **(metadata or {})
            }
            
            self.docs_collection.add(
                documents=[content],
                metadatas=[meta],
                ids=[doc_id]
            )
            
            logger.info(f"Added document to RAG: {title} ({doc_id})")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error adding document to RAG: {e}")
            return ""
    
    def search_relevant_messages(
        self,
        query: str,
        session_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant chat messages
        
        Args:
            query: Search query
            session_id: Optional session ID to filter by
            limit: Maximum results to return
            
        Returns:
            List of relevant messages with metadata
        """
        try:
            # Build where clause
            where_clause = {}
            if session_id:
                where_clause["session_id"] = session_id
            
            # Search
            results = self.chat_collection.query(
                query_texts=[query],
                n_results=limit,
                where=where_clause if where_clause else None
            )
            
            # Format results
            formatted_results = []
            if results and results['documents'] and len(results['documents']) > 0:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching messages: {e}")
            return []
    
    def search_documents(
        self,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant documents
        
        Args:
            query: Search query
            limit: Maximum results to return
            
        Returns:
            List of relevant documents with metadata
        """
        try:
            results = self.docs_collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            # Format results
            formatted_results = []
            if results and results['documents'] and len(results['documents']) > 0:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def get_context_for_query(
        self,
        query: str,
        session_id: Optional[str] = None,
        include_documents: bool = True,
        max_context_length: int = 2000
    ) -> str:
        """
        Get relevant context for a query
        
        Args:
            query: User query
            session_id: Optional session ID for chat history
            include_documents: Whether to include document search
            max_context_length: Maximum characters of context
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # Search chat history
        chat_results = self.search_relevant_messages(query, session_id, limit=3)
        if chat_results:
            context_parts.append("=== Relevant Previous Conversations ===")
            for result in chat_results:
                role = result['metadata'].get('role', 'unknown')
                content = result['content'][:500]  # Limit length
                context_parts.append(f"[{role}]: {content}")
        
        # Search documents
        if include_documents:
            doc_results = self.search_documents(query, limit=2)
            if doc_results:
                context_parts.append("\n=== Relevant Documents ===")
                for result in doc_results:
                    title = result['metadata'].get('title', 'Untitled')
                    content = result['content'][:800]  # Limit length
                    context_parts.append(f"Document: {title}\n{content}")
        
        # Combine and limit
        full_context = "\n\n".join(context_parts)
        
        if len(full_context) > max_context_length:
            full_context = full_context[:max_context_length] + "\n...[context truncated]"
        
        return full_context
    
    def clear_session_history(self, session_id: str) -> int:
        """
        Clear chat history for a session
        
        Args:
            session_id: Session ID to clear
            
        Returns:
            Number of messages deleted
        """
        try:
            # Get all IDs for this session
            results = self.chat_collection.get(
                where={"session_id": session_id}
            )
            
            if results and results['ids']:
                self.chat_collection.delete(ids=results['ids'])
                logger.info(f"Cleared {len(results['ids'])} messages for session {session_id}")
                return len(results['ids'])
            
            return 0
            
        except Exception as e:
            logger.error(f"Error clearing session history: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        try:
            chat_count = self.chat_collection.count()
            docs_count = self.docs_collection.count()
            
            return {
                'chat_messages': chat_count,
                'documents': docs_count,
                'total_items': chat_count + docs_count,
                'persist_directory': str(self.persist_dir),
                'embedding_model': 'all-MiniLM-L6-v2'
            }
        except Exception as e:
            logger.error(f"Error getting RAG stats: {e}")
            return {}
    
    def reset(self):
        """Reset the RAG system (delete all data)"""
        try:
            self.client.delete_collection("chat_history")
            self.client.delete_collection("documents")
            self.chat_collection = self._get_or_create_collection("chat_history")
            self.docs_collection = self._get_or_create_collection("documents")
            logger.warning("RAG system reset - all data deleted")
        except Exception as e:
            logger.error(f"Error resetting RAG system: {e}")
