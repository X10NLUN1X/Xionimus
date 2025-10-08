"""
Code Review Models for SQLite
Stores review requests, findings, and agent results
"""
from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON
from datetime import datetime, timezone
from ..core.database import Base


class CodeReview(Base):
    """Main code review record"""
    __tablename__ = "code_reviews"
    
    id = Column(String, primary_key=True)  # UUID
    title = Column(String, nullable=False)
    review_type = Column(String, nullable=False)  # file_upload, github_repo, internal_project
    status = Column(String, default="pending")  # pending, in_progress, completed, failed
    
    # Input source information
    source_type = Column(String, nullable=False)  # file, github, internal
    source_path = Column(Text, nullable=True)  # file path or github URL
    source_metadata = Column(JSON, nullable=True)  # additional source info
    
    # Review configuration
    review_scope = Column(String, default="full")  # full, security, enhancement, debug
    priority = Column(String, default="medium")  # critical, high, medium, low
    
    # Results summary
    quality_score = Column(Integer, nullable=True)  # 0-100
    critical_issues = Column(Integer, default=0)
    high_issues = Column(Integer, default=0)
    medium_issues = Column(Integer, default=0)
    low_issues = Column(Integer, default=0)
    
    # Agent execution tracking
    agents_completed = Column(JSON, default=list)  # List of completed agent IDs
    agents_failed = Column(JSON, default=list)  # List of failed agent IDs
    
    # Results
    summary = Column(Text, nullable=True)
    action_plan = Column(JSON, nullable=True)  # Structured action items
    
    # Timestamps
    created_at = Column(String, default=lambda: datetime.now(timezone.utc).isoformat())
    started_at = Column(String, nullable=True)
    completed_at = Column(String, nullable=True)
    
    # User/API configuration
    api_keys_config = Column(JSON, nullable=True)  # Encrypted API keys for review


class ReviewFinding(Base):
    """Individual code review finding"""
    __tablename__ = "review_findings"
    
    id = Column(String, primary_key=True)  # UUID
    review_id = Column(String, ForeignKey("code_reviews.id"), nullable=False)
    
    # Agent that found this issue
    agent_name = Column(String, nullable=False)  # analysis, debug, enhancement, test
    
    # Finding details
    severity = Column(String, nullable=False)  # critical, high, medium, low
    category = Column(String, nullable=False)  # security, performance, quality, testing, etc.
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    
    # Location in code
    file_path = Column(String, nullable=True)
    line_number = Column(Integer, nullable=True)
    code_snippet = Column(Text, nullable=True)
    
    # Recommendations
    recommendation = Column(Text, nullable=True)
    fix_suggestion = Column(Text, nullable=True)
    fix_code = Column(Text, nullable=True)  # Suggested code fix
    
    # Metadata
    impact = Column(String, nullable=True)  # Business impact description
    effort = Column(String, nullable=True)  # Estimated fix effort (hours)
    priority_score = Column(Integer, default=0)  # Calculated priority
    
    created_at = Column(String, default=lambda: datetime.now(timezone.utc).isoformat())


class ReviewAgent(Base):
    """Agent execution tracking"""
    __tablename__ = "review_agents"
    
    id = Column(String, primary_key=True)  # UUID
    review_id = Column(String, ForeignKey("code_reviews.id"), nullable=False)
    
    agent_name = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, running, completed, failed
    
    # Execution details
    started_at = Column(String, nullable=True)
    completed_at = Column(String, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Results
    findings_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    raw_output = Column(JSON, nullable=True)  # Full agent response
    
    created_at = Column(String, default=lambda: datetime.now(timezone.utc).isoformat())
