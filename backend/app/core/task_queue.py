"""
Task Queue System for Agent Orchestration
Manages agent tasks with priorities, dependencies, and retry logic

Location: /backend/app/core/task_queue.py
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, field
from uuid import uuid4
import heapq

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"          # Waiting for execution
    READY = "ready"             # Dependencies satisfied, ready to execute
    RUNNING = "running"         # Currently executing
    COMPLETED = "completed"     # Successfully completed
    FAILED = "failed"           # Failed (may retry)
    CANCELLED = "cancelled"     # Manually cancelled
    SKIPPED = "skipped"         # Skipped (e.g., optional task)


class TaskPriority(Enum):
    """Task priority levels (higher = more important)"""
    LOW = 1
    NORMAL = 5
    HIGH = 8
    CRITICAL = 10


@dataclass
class Task:
    """
    Task object representing work for an agent
    """
    task_id: str = field(default_factory=lambda: str(uuid4()))
    agent_type: str = None  # AgentType.value
    description: str = ""
    input_data: Dict[str, Any] = field(default_factory=dict)
    
    # Priority and dependencies
    priority: TaskPriority = TaskPriority.NORMAL
    dependencies: List[str] = field(default_factory=list)  # Task IDs
    blocking: bool = True  # If False, can be skipped on failure
    
    # Execution
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    
    # Retry logic
    retry_count: int = 0
    max_retries: int = 2
    retry_delay: float = 1.0  # seconds
    
    # Timing
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Metadata
    execution_id: Optional[str] = None  # Link to orchestrator execution
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __lt__(self, other):
        """For heapq comparison - higher priority comes first"""
        return self.priority.value > other.priority.value
    
    def duration(self) -> Optional[float]:
        """Get task duration in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def can_retry(self) -> bool:
        """Check if task can be retried"""
        return (
            self.status == TaskStatus.FAILED and
            self.retry_count < self.max_retries
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "task_id": self.task_id,
            "agent_type": self.agent_type,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "dependencies": self.dependencies,
            "blocking": self.blocking,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "error": self.error,
            "duration": self.duration(),
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "tags": self.tags,
            "metadata": self.metadata
        }


class TaskQueue:
    """
    Task queue with priority, dependency resolution, and retry logic
    """
    
    def __init__(self):
        # All tasks by ID
        self._tasks: Dict[str, Task] = {}
        
        # Priority queue of ready tasks (heapq)
        self._ready_queue: List[Task] = []
        
        # Tasks by status
        self._pending_tasks: Set[str] = set()
        self._running_tasks: Set[str] = set()
        self._completed_tasks: Set[str] = set()
        self._failed_tasks: Set[str] = set()
        
        # Dependency graph: task_id -> set of task_ids that depend on it
        self._dependents: Dict[str, Set[str]] = {}
        
        # Statistics
        self._stats = {
            "total_enqueued": 0,
            "total_completed": 0,
            "total_failed": 0,
            "total_retries": 0
        }
        
        logger.info("📋 Task Queue initialized")
    
    async def enqueue(self, task: Task) -> None:
        """
        Add task to queue
        Automatically checks if ready to execute
        """
        # Validate task
        if not task.agent_type:
            raise ValueError("Task must have agent_type")
        
        # Add to tasks dict
        self._tasks[task.task_id] = task
        
        # Update statistics
        self._stats["total_enqueued"] += 1
        
        # Set status based on dependencies
        if task.dependencies:
            task.status = TaskStatus.PENDING
            self._pending_tasks.add(task.task_id)
            
            # Register as dependent
            for dep_id in task.dependencies:
                if dep_id not in self._dependents:
                    self._dependents[dep_id] = set()
                self._dependents[dep_id].add(task.task_id)
        else:
            # No dependencies - ready to execute
            task.status = TaskStatus.READY
            heapq.heappush(self._ready_queue, task)
        
        logger.info(
            f"📝 Task enqueued: {task.agent_type} "
            f"(priority={task.priority.value}, deps={len(task.dependencies)})"
        )
    
    async def dequeue(self, timeout: Optional[float] = None) -> Optional[Task]:
        """
        Get next ready task (highest priority)
        Returns None if no tasks available
        """
        start_time = datetime.now(timezone.utc)
        
        while True:
            # Check if we have ready tasks
            if self._ready_queue:
                task = heapq.heappop(self._ready_queue)
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.now(timezone.utc)
                
                self._running_tasks.add(task.task_id)
                
                logger.info(
                    f"🎯 Task dequeued: {task.agent_type} "
                    f"(priority={task.priority.value})"
                )
                return task
            
            # Check timeout
            if timeout is not None:
                elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
                if elapsed >= timeout:
                    return None
            
            # Wait a bit and try again
            await asyncio.sleep(0.1)
    
    async def mark_completed(self, task_id: str, result: Any = None) -> None:
        """
        Mark task as completed
        Checks for dependent tasks that can now run
        """
        if task_id not in self._tasks:
            logger.warning(f"⚠️ Task {task_id} not found")
            return
        
        task = self._tasks[task_id]
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now(timezone.utc)
        task.result = result
        
        # Update sets
        self._running_tasks.discard(task_id)
        self._completed_tasks.add(task_id)
        
        # Update statistics
        self._stats["total_completed"] += 1
        
        logger.info(
            f"✅ Task completed: {task.agent_type} "
            f"(duration={task.duration():.2f}s)"
        )
        
        # Check dependent tasks
        await self._check_dependents(task_id)
    
    async def mark_failed(self, task_id: str, error: str) -> None:
        """
        Mark task as failed
        May retry if retries available
        """
        if task_id not in self._tasks:
            logger.warning(f"⚠️ Task {task_id} not found")
            return
        
        task = self._tasks[task_id]
        task.error = error
        
        # Check if can retry
        if task.can_retry():
            task.retry_count += 1
            task.status = TaskStatus.READY
            
            # Re-queue with delay
            self._stats["total_retries"] += 1
            
            logger.warning(
                f"🔄 Task failed, retrying ({task.retry_count}/{task.max_retries}): "
                f"{task.agent_type}"
            )
            
            # Add back to queue after delay
            await asyncio.sleep(task.retry_delay * task.retry_count)
            heapq.heappush(self._ready_queue, task)
        else:
            # No more retries
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now(timezone.utc)
            
            # Update sets
            self._running_tasks.discard(task_id)
            self._failed_tasks.add(task_id)
            
            # Update statistics
            self._stats["total_failed"] += 1
            
            logger.error(f"❌ Task failed permanently: {task.agent_type} - {error}")
            
            # Handle dependent tasks
            await self._handle_failed_task_dependents(task_id)
    
    async def _check_dependents(self, completed_task_id: str) -> None:
        """
        Check if any dependent tasks can now run
        """
        if completed_task_id not in self._dependents:
            return
        
        # Get tasks that depend on this one
        dependent_ids = self._dependents[completed_task_id].copy()
        
        for dep_id in dependent_ids:
            if dep_id not in self._tasks:
                continue
            
            dep_task = self._tasks[dep_id]
            
            # Check if all dependencies are completed
            if self._are_dependencies_satisfied(dep_task):
                # Move to ready queue
                dep_task.status = TaskStatus.READY
                self._pending_tasks.discard(dep_id)
                heapq.heappush(self._ready_queue, dep_task)
                
                logger.info(
                    f"🎯 Task now ready: {dep_task.agent_type} "
                    f"(dependencies satisfied)"
                )
    
    async def _handle_failed_task_dependents(self, failed_task_id: str) -> None:
        """
        Handle tasks that depend on a failed task
        Skip non-blocking dependents, fail blocking ones
        """
        if failed_task_id not in self._dependents:
            return
        
        dependent_ids = self._dependents[failed_task_id].copy()
        
        for dep_id in dependent_ids:
            if dep_id not in self._tasks:
                continue
            
            dep_task = self._tasks[dep_id]
            
            if dep_task.blocking:
                # Blocking task - fail it too
                dep_task.status = TaskStatus.FAILED
                dep_task.error = f"Dependency {failed_task_id} failed"
                dep_task.completed_at = datetime.now(timezone.utc)
                
                self._pending_tasks.discard(dep_id)
                self._failed_tasks.add(dep_id)
                
                logger.warning(
                    f"⛔ Task failed due to dependency: {dep_task.agent_type}"
                )
                
                # Recursively handle its dependents
                await self._handle_failed_task_dependents(dep_id)
            else:
                # Non-blocking - skip it
                dep_task.status = TaskStatus.SKIPPED
                dep_task.completed_at = datetime.now(timezone.utc)
                
                self._pending_tasks.discard(dep_id)
                
                logger.info(
                    f"⏭️ Task skipped (non-blocking): {dep_task.agent_type}"
                )
                
                # Check if its dependents can run
                await self._check_dependents(dep_id)
    
    def _are_dependencies_satisfied(self, task: Task) -> bool:
        """Check if all task dependencies are completed"""
        for dep_id in task.dependencies:
            if dep_id not in self._tasks:
                return False
            
            dep_task = self._tasks[dep_id]
            
            # Dependency must be completed or skipped
            if dep_task.status not in [TaskStatus.COMPLETED, TaskStatus.SKIPPED]:
                return False
        
        return True
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self._tasks.get(task_id)
    
    def get_ready_tasks(self) -> List[Task]:
        """Get all ready tasks (sorted by priority)"""
        return sorted(self._ready_queue, key=lambda t: t.priority.value, reverse=True)
    
    def get_running_tasks(self) -> List[Task]:
        """Get all currently running tasks"""
        return [self._tasks[tid] for tid in self._running_tasks]
    
    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks (waiting for dependencies)"""
        return [self._tasks[tid] for tid in self._pending_tasks]
    
    def get_completed_tasks(self) -> List[Task]:
        """Get all completed tasks"""
        return [self._tasks[tid] for tid in self._completed_tasks]
    
    def get_failed_tasks(self) -> List[Task]:
        """Get all failed tasks"""
        return [self._tasks[tid] for tid in self._failed_tasks]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get queue statistics"""
        return {
            "total_tasks": len(self._tasks),
            "ready": len(self._ready_queue),
            "running": len(self._running_tasks),
            "pending": len(self._pending_tasks),
            "completed": len(self._completed_tasks),
            "failed": len(self._failed_tasks),
            "enqueued": self._stats["total_enqueued"],
            "total_completed": self._stats["total_completed"],
            "total_failed": self._stats["total_failed"],
            "total_retries": self._stats["total_retries"],
            "success_rate": (
                self._stats["total_completed"] / self._stats["total_enqueued"]
                if self._stats["total_enqueued"] > 0 else 0
            )
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get detailed queue status"""
        return {
            "statistics": self.get_statistics(),
            "ready_tasks": [t.to_dict() for t in self.get_ready_tasks()],
            "running_tasks": [t.to_dict() for t in self.get_running_tasks()],
            "pending_tasks": [t.to_dict() for t in self.get_pending_tasks()],
            "failed_tasks": [t.to_dict() for t in self.get_failed_tasks()]
        }
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or ready task"""
        if task_id not in self._tasks:
            return False
        
        task = self._tasks[task_id]
        
        # Can only cancel pending or ready tasks
        if task.status not in [TaskStatus.PENDING, TaskStatus.READY]:
            logger.warning(
                f"⚠️ Cannot cancel task with status {task.status.value}"
            )
            return False
        
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now(timezone.utc)
        
        # Remove from queues
        self._pending_tasks.discard(task_id)
        if task in self._ready_queue:
            self._ready_queue.remove(task)
            heapq.heapify(self._ready_queue)
        
        logger.info(f"🚫 Task cancelled: {task.agent_type}")
        return True
    
    def clear(self) -> None:
        """Clear all tasks (for testing)"""
        self._tasks.clear()
        self._ready_queue.clear()
        self._pending_tasks.clear()
        self._running_tasks.clear()
        self._completed_tasks.clear()
        self._failed_tasks.clear()
        self._dependents.clear()
        self._stats = {
            "total_enqueued": 0,
            "total_completed": 0,
            "total_failed": 0,
            "total_retries": 0
        }
        logger.info("🧹 Task Queue cleared")


# Global queue instance
_queue: Optional[TaskQueue] = None


def get_task_queue() -> TaskQueue:
    """Get or create global task queue instance"""
    global _queue
    if _queue is None:
        _queue = TaskQueue()
    return _queue


def reset_task_queue() -> None:
    """Reset global queue (for testing)"""
    global _queue
    if _queue:
        _queue.clear()
    _queue = None
