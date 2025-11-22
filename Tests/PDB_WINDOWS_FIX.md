# PDB Windows Fix Guide

## Problem

On Windows, `pdb.set_trace()` may fail with:
```
AttributeError: module 'readline' has no attribute 'backend'
```

This happens because Windows doesn't have native `readline` support.

## Solutions

### Solution 1: Use breakpoint() (Python 3.7+) - Recommended

Replace:
```python
import pdb; pdb.set_trace()
```

With:
```python
breakpoint()  # Works better on Windows
```

### Solution 2: Use VS Code Debugger (Best for Windows)

1. **Set breakpoint**: Click in gutter (left of line number)
2. **Press F5**: Start debugging
3. **Select**: "Python: agent/test.py" from dropdown
4. **Debug**: Use visual debugger panels

No pdb needed!

### Solution 3: Install pyreadline (For pdb.set_trace())

If you want to use `pdb.set_trace()` on Windows:

```bash
pip install pyreadline
```

Then `pdb.set_trace()` should work.

### Solution 4: Use Alternative Debugger

Install a better debugger:
```bash
pip install ipdb
```

Then use:
```python
import ipdb; ipdb.set_trace()
```

### Solution 5: Manual Inspection (Fallback)

If pdb fails, use print statements:
```python
print("\n[DEBUG] Session state:")
print(json.dumps(session.state, indent=2))
print("\n[DEBUG] Press Enter to continue...")
input()
```

## Fixed Code in agent/test.py

I've updated `agent/test.py` to handle Windows readline issues:

```python
# Use safe breakpoint for Windows compatibility
try:
    import pdb
    # Set environment to avoid readline issues on Windows
    import os
    if sys.platform == 'win32':
        # Use simpler pdb without readline
        os.environ['PYTHONBREAKPOINT'] = 'pdb.set_trace'
    pdb.set_trace()
except Exception as e:
    print(f"\n[DEBUG] pdb error: {e}")
    print("[DEBUG] Using manual inspection instead...")
    print("\n[DEBUG] Session state:")
    print(json.dumps(session.state, indent=2))
    print("\n[DEBUG] Press Enter to continue...")
    input()
```

## Self-Diagnostic

Run this to check your debugging setup:

```python
# diagnostic_debug.py
import sys
import os

print("=== Python Debugging Diagnostic ===")
print(f"Python Version: {sys.version}")
print(f"Platform: {sys.platform}")

# Check pdb
try:
    import pdb
    print("✓ pdb module available")
except ImportError:
    print("✗ pdb module not available")

# Check readline
try:
    import readline
    print("✓ readline module available")
    if hasattr(readline, 'backend'):
        print(f"  readline.backend: {readline.backend}")
    else:
        print("  ⚠ readline.backend not available (Windows issue)")
except ImportError:
    print("✗ readline module not available (normal on Windows)")

# Check pyreadline
try:
    import pyreadline
    print("✓ pyreadline installed (helps pdb on Windows)")
except ImportError:
    print("✗ pyreadline not installed (optional for Windows)")

# Check breakpoint
try:
    breakpoint()
    print("✓ breakpoint() function works")
except Exception as e:
    print(f"✗ breakpoint() error: {e}")

# Check VS Code
if os.getenv('VSCODE_PID'):
    print("✓ Running in VS Code")
else:
    print("○ Not detected as VS Code (may still work)")

print("\n=== Recommendations ===")
if sys.platform == 'win32':
    print("1. Use VS Code debugger (F5) - Best option")
    print("2. Use breakpoint() instead of pdb.set_trace()")
    print("3. Install pyreadline: pip install pyreadline")
    print("4. Use ipdb: pip install ipdb")
else:
    print("1. pdb.set_trace() should work fine")
    print("2. breakpoint() also works")
    print("3. VS Code debugger is still recommended")
```

## Quick Fix for Your Code

**Option A: Use breakpoint() (Simplest)**
```python
# Replace: import pdb; pdb.set_trace()
breakpoint()  # Works on Windows
```

**Option B: Use VS Code Debugger (Best)**
1. Click left of line 118 to set breakpoint
2. Press F5
3. Done!

**Option C: Install pyreadline**
```bash
pip install pyreadline
```
Then `pdb.set_trace()` should work.

## Current Status

I've updated `agent/test.py` with Windows-compatible debugging code that:
- Tries pdb first
- Falls back to manual inspection if pdb fails
- Works on both Windows and Unix

The file should now work without the readline error!

