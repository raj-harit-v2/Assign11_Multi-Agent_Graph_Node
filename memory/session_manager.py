"""
Session Manager for Cross-Session Context

Provides multi-turn conversation support and cross-session context management.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field


@dataclass
class SessionContext:
    """Context for a single session."""
    session_id: str
    user_id: Optional[str] = None
    query: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    context_data: Dict[str, Any] = field(default_factory=dict)
    previous_session_id: Optional[str] = None
    next_session_id: Optional[str] = None


class SessionManager:
    """
    Manages cross-session context for multi-turn conversations.
    
    Features:
    - Track active sessions per user
    - Link related sessions
    - Retrieve previous context
    - Maintain conversation history
    """
    
    def __init__(self, logs_path: str = "memory/session_logs", max_context_sessions: int = 5):
        self.logs_path = Path(logs_path)
        self.max_context_sessions = max_context_sessions
        self.active_sessions: Dict[str, SessionContext] = {}  # session_id -> context
        self.user_sessions: Dict[str, List[str]] = {}  # user_id -> [session_ids]
    
    def create_session(
        self, 
        session_id: str, 
        query: str, 
        user_id: Optional[str] = None,
        previous_session_id: Optional[str] = None
    ) -> SessionContext:
        """
        Create a new session context.
        
        Args:
            session_id: Unique session identifier
            query: User query
            user_id: Optional user identifier for multi-user support
            previous_session_id: Link to previous session for context
        
        Returns:
            SessionContext object
        """
        context = SessionContext(
            session_id=session_id,
            user_id=user_id,
            query=query,
            timestamp=datetime.now(),
            previous_session_id=previous_session_id
        )
        
        self.active_sessions[session_id] = context
        
        if user_id:
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = []
            self.user_sessions[user_id].append(session_id)
            
            # Link to previous session
            if previous_session_id:
                if previous_session_id in self.active_sessions:
                    self.active_sessions[previous_session_id].next_session_id = session_id
        
        return context
    
    def get_previous_context(
        self, 
        session_id: str, 
        user_id: Optional[str] = None,
        max_sessions: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get previous session context for the same user.
        
        Args:
            session_id: Current session ID
            user_id: User identifier (if None, uses session_id)
            max_sessions: Maximum number of previous sessions to return
        
        Returns:
            List of previous session contexts
        """
        if max_sessions is None:
            max_sessions = self.max_context_sessions
        
        # Get user's session history
        if user_id and user_id in self.user_sessions:
            session_ids = self.user_sessions[user_id]
        else:
            # Fallback: use session_id as user_id
            session_ids = [s for s in self.active_sessions.keys() if s.startswith(session_id.split("-")[0])]
        
        # Find current session index
        try:
            current_idx = session_ids.index(session_id)
        except ValueError:
            return []
        
        # Get previous sessions
        previous_ids = session_ids[:current_idx][-max_sessions:]
        
        contexts = []
        for prev_id in reversed(previous_ids):  # Most recent first
            context = self._load_session_context(prev_id)
            if context:
                contexts.append(context)
        
        return contexts
    
    def _load_session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session context from JSON file."""
        try:
            # Find session file
            session_files = list(self.logs_path.rglob(f"{session_id}.json"))
            if not session_files:
                return None
            
            with open(session_files[0], 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Extract relevant context
            return {
                "session_id": session_id,
                "query": session_data.get("query") or session_data.get("original_query", ""),
                "final_answer": session_data.get("state_snapshot", {}).get("final_answer") or session_data.get("final_answer"),
                "metadata": session_data.get("metadata", {}),
                "timestamp": session_data.get("timestamp") or session_data.get("metadata", {}).get("timestamp")
            }
        except Exception as e:
            return None
    
    def update_session_context(self, session_id: str, context_data: Dict[str, Any]):
        """Update context data for a session."""
        if session_id in self.active_sessions:
            self.active_sessions[session_id].context_data.update(context_data)
    
    def get_conversation_history(
        self, 
        user_id: str, 
        hours_back: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history for a user within specified time window.
        
        Args:
            user_id: User identifier
            hours_back: Number of hours to look back
        
        Returns:
            List of session contexts in chronological order
        """
        if user_id not in self.user_sessions:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        session_ids = self.user_sessions[user_id]
        
        history = []
        for session_id in session_ids:
            context = self._load_session_context(session_id)
            if context:
                # Check timestamp
                if context.get("timestamp"):
                    try:
                        session_time = datetime.fromisoformat(context["timestamp"].replace("Z", "+00:00"))
                        if session_time.replace(tzinfo=None) >= cutoff_time:
                            history.append(context)
                    except Exception:
                        # Include if timestamp parsing fails
                        history.append(context)
                else:
                    history.append(context)
        
        return sorted(history, key=lambda x: x.get("timestamp", ""), reverse=True)
    
    def cleanup_old_sessions(self, days_old: int = 7):
        """Remove old sessions from active memory (they're still in files)."""
        cutoff_time = datetime.now() - timedelta(days=days_old)
        
        to_remove = []
        for session_id, context in self.active_sessions.items():
            if context.timestamp < cutoff_time:
                to_remove.append(session_id)
        
        for session_id in to_remove:
            del self.active_sessions[session_id]
        
        # Clean user_sessions
        for user_id, session_ids in self.user_sessions.items():
            self.user_sessions[user_id] = [s for s in session_ids if s in self.active_sessions]
        
        return len(to_remove)

