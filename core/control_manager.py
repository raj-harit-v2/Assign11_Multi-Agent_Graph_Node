"""
Control Manager for Session 10
Centralized enforcement of MAX_STEPS and MAX_RETRIES limits.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Load limits from environment or use defaults
MAX_STEPS = int(os.getenv("MAX_STEPS", "3"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))


class ControlManager:
    """Manages execution limits and control flow."""
    
    def __init__(self, max_steps: int = None, max_retries: int = None):
        self.max_steps = max_steps or MAX_STEPS
        self.max_retries = max_retries or MAX_RETRIES
    
    def check_step_limit(self, current_step_index: int) -> tuple[bool, str]:
        """
        Check if step limit has been reached.
        
        Args:
            current_step_index: Current step index (0-based)
        
        Returns:
            tuple: (is_limit_reached: bool, message: str)
        """
        if current_step_index >= self.max_steps:
            return True, f"Max steps limit ({self.max_steps}) reached at step {current_step_index}"
        return False, ""
    
    def check_retry_limit(self, retry_count: int) -> tuple[bool, str]:
        """
        Check if retry limit has been reached.
        
        Args:
            retry_count: Current retry count
        
        Returns:
            tuple: (is_limit_reached: bool, message: str)
        """
        if retry_count >= self.max_retries:
            return True, f"Max retries limit ({self.max_retries}) reached at retry {retry_count}"
        return False, ""
    
    def get_max_steps(self) -> int:
        """Get the maximum allowed steps."""
        return self.max_steps
    
    def get_max_retries(self) -> int:
        """Get the maximum allowed retries."""
        return self.max_retries

