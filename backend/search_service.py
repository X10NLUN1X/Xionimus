#!/usr/bin/env python3
"""
Enhanced Search Service for XIONIMUS AI v2.1
Provides full-text search capabilities across all projects and sessions
"""

import logging
import asyncio
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
import json
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

@dataclass
class SearchResult:
    """Represents a search result item"""
    id: str
    title: str
    content: str
    type: str  # 'project', 'session', 'file', 'chat'
    score: float
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    highlighted_content: str = ""

class SearchType(Enum):
    """Search type enumeration"""
    ALL = "all"
    PROJECTS = "projects"
    SESSIONS = "sessions"
    FILES = "files"
    CHAT = "chat"

class EnhancedSearchService:
    """
    Enhanced search service providing full-text search capabilities
    across all projects, sessions, files, and chat history
    """
    
    def __init__(self, db_client=None):
        self.db = db_client
        self.logger = logging.getLogger("search_service")
        self.search_indices = {}
        self._initialize_search_indices()
    
    def _initialize_search_indices(self):
        """Initialize search indices for different content types"""
        self.search_indices = {
            'projects': {},
            'sessions': {},
            'files': {},
            'chat': {}
        }
        self.logger.info("🔍 Enhanced Search Service initialized")
    
    async def search(self, 
                    query: str, 
                    search_type: SearchType = SearchType.ALL,
                    limit: int = 50,
                    offset: int = 0,
                    filters: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """
        Perform enhanced search across specified content types
        
        Args:
            query: Search query string
            search_type: Type of content to search
            limit: Maximum number of results
            offset: Pagination offset
            filters: Additional filters (project_id, date_range, etc.)
        
        Returns:
            List of SearchResult objects
        """
        try:
            self.logger.info(f"🔍 Searching for '{query}' in {search_type.value}")
            
            if not query or len(query.strip()) < 2:
                return []
            
            # Normalize query
            normalized_query = self._normalize_query(query)
            
            # Perform search based on type
            if search_type == SearchType.ALL:
                results = await self._search_all_content(normalized_query, limit, offset, filters)
            elif search_type == SearchType.PROJECTS:
                results = await self._search_projects(normalized_query, limit, offset, filters)
            elif search_type == SearchType.SESSIONS:
                results = await self._search_sessions(normalized_query, limit, offset, filters)
            elif search_type == SearchType.FILES:
                results = await self._search_files(normalized_query, limit, offset, filters)
            elif search_type == SearchType.CHAT:
                results = await self._search_chat_history(normalized_query, limit, offset, filters)
            else:
                results = []
            
            # Sort by relevance score
            results.sort(key=lambda x: x.score, reverse=True)
            
            self.logger.info(f"✅ Found {len(results)} search results")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Search error: {str(e)}")
            return []
    
    def _normalize_query(self, query: str) -> str:
        """Normalize search query for better matching"""
        # Convert to lowercase and clean up
        query = query.lower().strip()
        
        # Remove special characters but keep spaces
        query = re.sub(r'[^\w\s]', ' ', query)
        
        # Remove extra whitespace
        query = re.sub(r'\s+', ' ', query).strip()
        
        return query
    
    async def _search_all_content(self, query: str, limit: int, offset: int, filters: Optional[Dict]) -> List[SearchResult]:
        """Search across all content types"""
        all_results = []
        
        # Search each content type
        project_results = await self._search_projects(query, limit//4, 0, filters)
        session_results = await self._search_sessions(query, limit//4, 0, filters)
        file_results = await self._search_files(query, limit//4, 0, filters)
        chat_results = await self._search_chat_history(query, limit//4, 0, filters)
        
        # Combine and boost scores based on content type importance
        for result in project_results:
            result.score *= 1.2  # Boost project results
            all_results.append(result)
        
        for result in session_results:
            result.score *= 1.1  # Boost session results
            all_results.append(result)
        
        all_results.extend(file_results)
        all_results.extend(chat_results)
        
        return all_results[offset:offset + limit]
    
    async def _search_projects(self, query: str, limit: int, offset: int, filters: Optional[Dict]) -> List[SearchResult]:
        """Search in projects collection"""
        results = []
        
        if not self.db:
            return results
        
        try:
            # Build search filter
            search_filter = self._build_mongo_text_filter(query)
            if filters and 'project_id' in filters:
                search_filter['_id'] = filters['project_id']
            
            # Search in projects collection
            async for project in self.db.projects.find(search_filter).limit(limit).skip(offset):
                score = self._calculate_relevance_score(query, [
                    project.get('name', ''),
                    project.get('description', ''),
                    project.get('tags', [])
                ])
                
                if score > 0:
                    result = SearchResult(
                        id=str(project['_id']),
                        title=project.get('name', 'Untitled Project'),
                        content=project.get('description', ''),
                        type='project',
                        score=score,
                        metadata={
                            'tags': project.get('tags', []),
                            'language': project.get('language', ''),
                            'status': project.get('status', '')
                        },
                        created_at=project.get('created_at', datetime.now(timezone.utc)),
                        updated_at=project.get('updated_at', datetime.now(timezone.utc)),
                        highlighted_content=self._highlight_matches(query, project.get('description', ''))
                    )
                    results.append(result)
        
        except Exception as e:
            self.logger.error(f"❌ Project search error: {str(e)}")
        
        return results
    
    async def _search_sessions(self, query: str, limit: int, offset: int, filters: Optional[Dict]) -> List[SearchResult]:
        """Search in sessions collection"""
        results = []
        
        if not self.db:
            return results
        
        try:
            # Build search filter
            search_filter = self._build_mongo_text_filter(query)
            
            # Search in sessions collection
            async for session in self.db.sessions.find(search_filter).limit(limit).skip(offset):
                session_data = session.get('session_data', {})
                conversation = session_data.get('conversation', [])
                
                # Calculate score based on conversation content
                conversation_text = ' '.join([
                    msg.get('content', '') for msg in conversation if isinstance(msg.get('content'), str)
                ])
                
                score = self._calculate_relevance_score(query, [
                    session.get('name', ''),
                    conversation_text
                ])
                
                if score > 0:
                    result = SearchResult(
                        id=str(session['_id']),
                        title=session.get('name', 'Untitled Session'),
                        content=conversation_text[:500] + '...' if len(conversation_text) > 500 else conversation_text,
                        type='session',
                        score=score,
                        metadata={
                            'message_count': len(conversation),
                            'project_id': session.get('project_id', ''),
                            'status': session.get('status', 'active')
                        },
                        created_at=session.get('created_at', datetime.now(timezone.utc)),
                        updated_at=session.get('updated_at', datetime.now(timezone.utc)),
                        highlighted_content=self._highlight_matches(query, conversation_text[:200])
                    )
                    results.append(result)
        
        except Exception as e:
            self.logger.error(f"❌ Session search error: {str(e)}")
        
        return results
    
    async def _search_files(self, query: str, limit: int, offset: int, filters: Optional[Dict]) -> List[SearchResult]:
        """Search in files collection"""
        results = []
        
        if not self.db:
            return results
        
        try:
            # Build search filter
            search_filter = self._build_mongo_text_filter(query)
            
            # Search in files collection
            async for file_doc in self.db.files.find(search_filter).limit(limit).skip(offset):
                file_content = file_doc.get('content', '')
                
                score = self._calculate_relevance_score(query, [
                    file_doc.get('name', ''),
                    file_doc.get('path', ''),
                    file_content
                ])
                
                if score > 0:
                    result = SearchResult(
                        id=str(file_doc['_id']),
                        title=file_doc.get('name', 'Untitled File'),
                        content=file_content[:300] + '...' if len(file_content) > 300 else file_content,
                        type='file',
                        score=score,
                        metadata={
                            'path': file_doc.get('path', ''),
                            'language': file_doc.get('language', ''),
                            'size': file_doc.get('size', 0),
                            'project_id': file_doc.get('project_id', '')
                        },
                        created_at=file_doc.get('created_at', datetime.now(timezone.utc)),
                        updated_at=file_doc.get('updated_at', datetime.now(timezone.utc)),
                        highlighted_content=self._highlight_matches(query, file_content[:200])
                    )
                    results.append(result)
        
        except Exception as e:
            self.logger.error(f"❌ File search error: {str(e)}")
        
        return results
    
    async def _search_chat_history(self, query: str, limit: int, offset: int, filters: Optional[Dict]) -> List[SearchResult]:
        """Search in chat history"""
        results = []
        
        if not self.db:
            return results
        
        try:
            # Build search filter for chat messages
            search_filter = self._build_mongo_text_filter(query)
            
            # Search in chat_history collection (assuming this exists)
            if hasattr(self.db, 'chat_history'):
                async for chat in self.db.chat_history.find(search_filter).limit(limit).skip(offset):
                    message = chat.get('message', '')
                    response = chat.get('response', '')
                    
                    score = self._calculate_relevance_score(query, [message, response])
                    
                    if score > 0:
                        result = SearchResult(
                            id=str(chat['_id']),
                            title=f"Chat: {message[:50]}...",
                            content=f"Q: {message}\nA: {response}",
                            type='chat',
                            score=score,
                            metadata={
                                'agent': chat.get('agent', ''),
                                'session_id': chat.get('session_id', ''),
                                'project_id': chat.get('project_id', '')
                            },
                            created_at=chat.get('created_at', datetime.now(timezone.utc)),
                            updated_at=chat.get('updated_at', datetime.now(timezone.utc)),
                            highlighted_content=self._highlight_matches(query, message + ' ' + response)
                        )
                        results.append(result)
        
        except Exception as e:
            self.logger.error(f"❌ Chat history search error: {str(e)}")
        
        return results
    
    def _build_mongo_text_filter(self, query: str) -> Dict[str, Any]:
        """Build MongoDB text search filter"""
        # Use regex for flexible matching
        pattern = re.compile(query, re.IGNORECASE)
        return {
            '$or': [
                {'name': pattern},
                {'description': pattern},
                {'content': pattern},
                {'message': pattern},
                {'response': pattern}
            ]
        }
    
    def _calculate_relevance_score(self, query: str, texts: List[str]) -> float:
        """Calculate relevance score based on query matches in texts"""
        query_terms = query.split()
        total_score = 0.0
        
        for text in texts:
            if not text:
                continue
                
            if isinstance(text, list):
                text = ' '.join(str(item) for item in text)
            
            text_lower = str(text).lower()
            
            # Exact phrase match gets highest score
            if query in text_lower:
                total_score += 10.0
            
            # Calculate term-based score
            term_score = 0.0
            for term in query_terms:
                if term in text_lower:
                    # More frequent terms get higher scores
                    frequency = text_lower.count(term)
                    term_score += frequency * 2.0
            
            total_score += term_score
        
        # Normalize score (0-100)
        return min(total_score, 100.0)
    
    def _highlight_matches(self, query: str, text: str, max_length: int = 200) -> str:
        """Highlight query matches in text for display"""
        if not text or not query:
            return text[:max_length]
        
        # Simple highlighting - wrap matches in markdown bold
        highlighted = text
        query_terms = query.split()
        
        for term in query_terms:
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            highlighted = pattern.sub(f"**{term}**", highlighted)
        
        # Truncate if too long
        if len(highlighted) > max_length:
            highlighted = highlighted[:max_length] + "..."
        
        return highlighted
    
    async def get_search_suggestions(self, partial_query: str, limit: int = 10) -> List[str]:
        """Get search suggestions based on partial query"""
        suggestions = []
        
        if not partial_query or len(partial_query) < 2:
            return suggestions
        
        try:
            # Get suggestions from existing content
            pattern = re.compile(f"^{re.escape(partial_query)}", re.IGNORECASE)
            
            # Collect unique terms that start with the partial query
            suggestion_set = set()
            
            if self.db:
                # From projects
                async for project in self.db.projects.find({'name': pattern}).limit(5):
                    if project.get('name'):
                        suggestion_set.add(project['name'])
                
                # From files
                async for file_doc in self.db.files.find({'name': pattern}).limit(5):
                    if file_doc.get('name'):
                        suggestion_set.add(file_doc['name'])
            
            suggestions = list(suggestion_set)[:limit]
            
        except Exception as e:
            self.logger.error(f"❌ Search suggestions error: {str(e)}")
        
        return suggestions
    
    async def get_search_stats(self) -> Dict[str, Any]:
        """Get search statistics"""
        stats = {
            'total_projects': 0,
            'total_sessions': 0,
            'total_files': 0,
            'total_chat_messages': 0,
            'last_indexed': datetime.now(timezone.utc),
            'search_performance': 'good'
        }
        
        try:
            if self.db:
                stats['total_projects'] = await self.db.projects.count_documents({})
                stats['total_sessions'] = await self.db.sessions.count_documents({})
                stats['total_files'] = await self.db.files.count_documents({})
                
                if hasattr(self.db, 'chat_history'):
                    stats['total_chat_messages'] = await self.db.chat_history.count_documents({})
        
        except Exception as e:
            self.logger.error(f"❌ Search stats error: {str(e)}")
            stats['search_performance'] = 'degraded'
        
        return stats