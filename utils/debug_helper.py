"""
Debug Helper for Windows Compatibility
Provides cross-platform debugging support that works on Windows.
"""

import sys
import os


def safe_breakpoint():
    """
    Cross-platform breakpoint that works on Windows.
    Uses VS Code debugger if available, otherwise falls back to pdb.
    """
    # Check if we're in VS Code debugger
    if os.getenv('VSCODE_PID') or os.getenv('PYTHONBREAKPOINT'):
        # Use the configured breakpoint handler
        breakpoint()
        return
    
    # For Windows, use a simpler pdb approach
    if sys.platform == 'win32':
        try:
            # Try using built-in breakpoint (Python 3.7+)
            # This should handle Windows readline issues better
            breakpoint()
        except Exception as e:
            print(f"\n[DEBUG] Breakpoint error: {e}")
            print("[DEBUG] Falling back to manual inspection...")
            print("[DEBUG] Execution paused. Check variables above.")
            input("[DEBUG] Press Enter to continue...")
    else:
        # On Unix-like systems, use standard breakpoint
        breakpoint()


def debug_print(*args, **kwargs):
    """
    Print with debug prefix for easy identification.
    """
    print("[DEBUG]", *args, **kwargs)


def inspect_variable(var_name, var_value, max_length=500):
    """
    Safely inspect a variable, handling large objects.
    """
    try:
        var_str = str(var_value)
        if len(var_str) > max_length:
            var_str = var_str[:max_length] + f"... (truncated, total length: {len(var_str)})"
        debug_print(f"{var_name} = {var_str}")
        return var_str
    except Exception as e:
        debug_print(f"Error inspecting {var_name}: {e}")
        return None

