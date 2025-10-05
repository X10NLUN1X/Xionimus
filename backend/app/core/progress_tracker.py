"""
Progress Tracker für Xionimus AI
Zeigt detaillierte Fortschritts-Updates während der Verarbeitung
"""
import logging
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class ProgressStep:
    """Represents a single progress step"""
    def __init__(
        self,
        id: str,
        title: str,
        description: str = "",
        status: str = "pending"  # pending, running, completed, error
    ):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error
        }

class ProgressTracker:
    """
    Tracks and reports progress of multi-step operations
    """
    
    def __init__(self):
        self.steps: List[ProgressStep] = []
        self.current_step_index = -1
        self.callback: Optional[Callable] = None
    
    def add_step(self, id: str, title: str, description: str = "") -> ProgressStep:
        """Add a new step to track"""
        step = ProgressStep(id, title, description)
        self.steps.append(step)
        return step
    
    def start_step(self, step_id: str) -> bool:
        """Mark a step as started"""
        for i, step in enumerate(self.steps):
            if step.id == step_id:
                step.status = "running"
                step.started_at = datetime.now()
                self.current_step_index = i
                logger.info(f"🔄 Step started: {step.title}")
                self._notify_update()
                return True
        return False
    
    def complete_step(self, step_id: str, result: Optional[str] = None) -> bool:
        """Mark a step as completed"""
        for step in self.steps:
            if step.id == step_id:
                step.status = "completed"
                step.completed_at = datetime.now()
                if result:
                    step.description += f" - {result}"
                logger.info(f"✅ Step completed: {step.title}")
                self._notify_update()
                return True
        return False
    
    def error_step(self, step_id: str, error: str) -> bool:
        """Mark a step as errored"""
        for step in self.steps:
            if step.id == step_id:
                step.status = "error"
                step.error = error
                step.completed_at = datetime.now()
                logger.error(f"❌ Step error: {step.title} - {error}")
                self._notify_update()
                return True
        return False
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress state"""
        total = len(self.steps)
        completed = sum(1 for s in self.steps if s.status == "completed")
        running = sum(1 for s in self.steps if s.status == "running")
        errors = sum(1 for s in self.steps if s.status == "error")
        
        return {
            "total_steps": total,
            "completed_steps": completed,
            "running_steps": running,
            "error_steps": errors,
            "progress_percent": int((completed / total * 100)) if total > 0 else 0,
            "current_step": self.steps[self.current_step_index].to_dict() if self.current_step_index >= 0 else None,
            "steps": [step.to_dict() for step in self.steps]
        }
    
    def set_callback(self, callback: Callable):
        """Set callback for progress updates"""
        self.callback = callback
    
    def _notify_update(self):
        """Notify callback of update"""
        if self.callback:
            try:
                self.callback(self.get_progress())
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")
    
    def format_for_display(self) -> str:
        """Format progress as human-readable text"""
        lines = []
        progress = self.get_progress()
        
        lines.append(f"## 📊 Fortschritt: {progress['completed_steps']}/{progress['total_steps']} Schritte ({progress['progress_percent']}%)")
        lines.append("")
        
        for step in self.steps:
            if step.status == "completed":
                icon = "✅"
            elif step.status == "running":
                icon = "🔄"
            elif step.status == "error":
                icon = "❌"
            else:
                icon = "⏳"
            
            lines.append(f"{icon} **{step.title}**")
            if step.description:
                lines.append(f"   {step.description}")
            if step.error:
                lines.append(f"   ❌ Error: {step.error}")
            lines.append("")
        
        return "\n".join(lines)

def create_research_workflow_tracker() -> ProgressTracker:
    """Create tracker for research workflow"""
    tracker = ProgressTracker()
    
    tracker.add_step(
        "research",
        "Recherche durchführen",
        "Sammle aktuelle Informationen mit Perplexity"
    )
    
    tracker.add_step(
        "clarification",
        "Klärungsfragen generieren",
        "Erstelle relevante Fragen basierend auf Research"
    )
    
    tracker.add_step(
        "auto_answer",
        "Fragen automatisch beantworten",
        "Wende Best Practices an"
    )
    
    tracker.add_step(
        "code_generation",
        "Code generieren",
        "Erstelle vollständigen, produktionsreifen Code"
    )
    
    tracker.add_step(
        "code_processing",
        "Code verarbeiten",
        "Extrahiere und speichere Code-Dateien"
    )
    
    return tracker

def create_chat_workflow_tracker() -> ProgressTracker:
    """Create tracker for normal chat workflow"""
    tracker = ProgressTracker()
    
    # Extended workflow with all agents
    tracker.add_step(
        "analyze",
        "Analysiere Anfrage",
        "Verstehe den Context und die Intention"
    )
    
    tracker.add_step(
        "generate",
        "Generiere Antwort",
        "KI erstellt die Response"
    )
    
    tracker.add_step(
        "process",
        "Verarbeite Code",
        "Extrahiere und speichere Code-Dateien"
    )
    
    tracker.add_step(
        "testing",
        "Erstelle Tests",
        "Generiere automatische Tests für den Code"
    )
    
    tracker.add_step(
        "review",
        "Code Review",
        "Prüfe Qualität, Sicherheit und Performance"
    )
    
    tracker.add_step(
        "documentation",
        "Erstelle Dokumentation",
        "Generiere README und API-Docs"
    )
    
    return tracker

# Global instance factory
def get_progress_tracker(workflow_type: str = "research") -> ProgressTracker:
    """Get a progress tracker for specific workflow"""
    if workflow_type == "research":
        return create_research_workflow_tracker()
    elif workflow_type == "chat":
        return create_chat_workflow_tracker()
    
    # Default generic tracker
    return ProgressTracker()
