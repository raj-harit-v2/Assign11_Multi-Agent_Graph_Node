"""
Self-Diagnostic Script for Python Debugging Setup
Run this to check if your debugging environment is configured correctly.
"""

import sys
import os

def run_diagnostic():
    """Run comprehensive debugging diagnostic."""
    print("\n" + "=" * 60)
    print("PYTHON DEBUGGING DIAGNOSTIC")
    print("=" * 60)
    
    # System Info
    print("\n[SYSTEM INFO]")
    print(f"  Python Version: {sys.version.split()[0]}")
    print(f"  Platform: {sys.platform}")
    print(f"  Architecture: {sys.platform}-{os.sys.maxsize > 2**32 and '64bit' or '32bit'}")
    
    # Check pdb
    print("\n[PDB MODULE]")
    try:
        import pdb
        print("  [OK] pdb module available")
        print(f"    Location: {pdb.__file__}")
    except ImportError as e:
        print(f"  [ERROR] pdb module not available: {e}")
        return False
    
    # Check readline
    print("\n[READLINE MODULE]")
    try:
        import readline
        print("  [OK] readline module available")
        print(f"    Location: {readline.__file__}")
        if hasattr(readline, 'backend'):
            print(f"    Backend: {readline.backend}")
        else:
            print("    [WARNING] readline.backend not available (Windows issue)")
            print("    -> This may cause pdb.set_trace() to fail")
    except ImportError:
        print("  [INFO] readline module not available (normal on Windows)")
        print("    -> pdb.set_trace() may have issues")
    
    # Check pyreadline
    print("\n[PYREADLINE]")
    try:
        import pyreadline
        print("  [OK] pyreadline installed (helps pdb on Windows)")
        print(f"    Location: {pyreadline.__file__}")
    except ImportError:
        print("  [INFO] pyreadline not installed")
        if sys.platform == 'win32':
            print("    -> Install with: pip install pyreadline")
    
    # Check ipdb
    print("\n[IPDB]")
    try:
        import ipdb
        print("  [OK] ipdb installed (better debugger)")
        print(f"    Location: {ipdb.__file__}")
    except ImportError:
        print("  [INFO] ipdb not installed")
        print("    -> Install with: pip install ipdb")
    
    # Check breakpoint function
    print("\n[BREAKPOINT FUNCTION]")
    try:
        # Test if breakpoint() is available (Python 3.7+)
        if hasattr(__builtins__, 'breakpoint'):
            print("  [OK] breakpoint() function available (Python 3.7+)")
        else:
            print("  [INFO] breakpoint() not available (Python < 3.7)")
            print("    -> Use pdb.set_trace() instead")
    except Exception as e:
        print(f"  [ERROR] Error checking breakpoint(): {e}")
    
    # Check VS Code
    print("\n[VS CODE DEBUGGER]")
    if os.getenv('VSCODE_PID'):
        print("  [OK] Running in VS Code")
        print(f"    VSCODE_PID: {os.getenv('VSCODE_PID')}")
    elif os.getenv('VSCODE_INSPECTOR_OPTIONS'):
        print("  [OK] VS Code debugger detected")
    else:
        print("  [INFO] Not detected as VS Code")
        print("    -> VS Code debugger may still work")
    
    # Check launch.json
    print("\n[VS CODE CONFIGURATION]")
    launch_json = os.path.join(os.getcwd(), '.vscode', 'launch.json')
    if os.path.exists(launch_json):
        print(f"  [OK] launch.json found: {launch_json}")
    else:
        print(f"  [INFO] launch.json not found")
        print(f"    -> Created at: {launch_json}")
    
    # Recommendations
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    
    if sys.platform == 'win32':
        print("\n[WINDOWS SPECIFIC]")
        print("  1. [BEST] Use VS Code debugger (F5)")
        print("     - Set breakpoint by clicking in gutter")
        print("     - Press F5 to start debugging")
        print("     - No pdb needed!")
        print()
        print("  2. Use breakpoint() instead of pdb.set_trace()")
        print("     - Replace: import pdb; pdb.set_trace()")
        print("     - With: breakpoint()")
        print()
        print("  3. Install pyreadline for pdb support:")
        print("     - pip install pyreadline")
        print("     - Then pdb.set_trace() should work")
        print()
        print("  4. Install ipdb for better debugging:")
        print("     - pip install ipdb")
        print("     - Use: import ipdb; ipdb.set_trace()")
    else:
        print("\n[UNIX/LINUX/MAC]")
        print("  1. [OK] pdb.set_trace() should work fine")
        print("  2. [OK] breakpoint() also works")
        print("  3. [OK] VS Code debugger recommended for better UX")
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    run_diagnostic()

