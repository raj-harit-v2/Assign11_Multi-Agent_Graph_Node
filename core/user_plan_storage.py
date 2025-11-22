"""
User Plan Storage for Session 10
Temporarily stores user-provided plans/answers for use in next lifeline.
Plans are stored per session and cleaned up after session finishes.
"""

from typing import Optional, Dict, Any
import json


class UserPlanStorage:
    """Temporary storage for user-provided plans per session."""
    
    # Session-level storage: {session_id: user_plan_data}
    _session_plans: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def store_user_plan(cls, session_id: str, user_plan_data: Dict[str, Any]) -> None:
        """
        Store user-provided plan for a session.
        
        Args:
            session_id: Session identifier
            user_plan_data: Dictionary containing:
                - original_goal_achieved: bool
                - final_answer: str
                - confidence: str
                - reasoning_note: str
                - solution_summary: str
        """
        cls._session_plans[session_id] = user_plan_data.copy()
        print(f"\n[STORED] User plan stored for session {session_id[:8]}...")
        print(f"  Final Answer: {user_plan_data.get('final_answer', 'N/A')[:100]}")
    
    @classmethod
    def get_user_plan(cls, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get stored user plan for a session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            User plan data or None if not found
        """
        return cls._session_plans.get(session_id)
    
    @classmethod
    def has_user_plan(cls, session_id: str) -> bool:
        """Check if session has a stored user plan."""
        return session_id in cls._session_plans
    
    @classmethod
    def clear_user_plan(cls, session_id: str) -> None:
        """
        Remove stored user plan for a session (cleanup after session finishes).
        
        Args:
            session_id: Session identifier
        """
        if session_id in cls._session_plans:
            del cls._session_plans[session_id]
            print(f"\n[CLEANED] User plan removed from memory for session {session_id[:8]}...")
    
    @classmethod
    def parse_user_input(cls, user_input: str) -> Optional[Dict[str, Any]]:
        """
        Parse user input that might be JSON format.
        
        Args:
            user_input: User input string (might be JSON or plain text)
        
        Returns:
            Parsed dictionary if JSON, None if plain text
        """
        user_input = user_input.strip()
        
        # Try to parse as JSON
        if user_input.startswith('{') and user_input.endswith('}'):
            try:
                parsed = json.loads(user_input)
                # Validate required fields
                if isinstance(parsed, dict) and 'final_answer' in parsed:
                    return parsed
            except json.JSONDecodeError:
                pass
        
        # Not JSON, return None (will be treated as plain text plan)
        return None

