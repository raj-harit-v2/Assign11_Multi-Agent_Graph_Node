# Python Debugging Guide for VS Code/Cursor

## Quick Answer

**pdb is built-in** - No installation needed! However, VS Code/Cursor has a better built-in debugger.

---

## Option 1: Using pdb.set_trace() (Built-in, No Installation)

### How to Use

1. **Uncomment the line** in your code:
```python
import pdb; pdb.set_trace()  # Remove the # to enable
```

2. **Run your script**:
```bash
python agent/test.py
```

3. **When execution hits the breakpoint**, you'll see:
```
> c:\path\to\file.py(117)<module>()
-> print(json.dumps(session.to_json(), indent=2))
(Pdb)
```

4. **Use pdb commands**:
   - `n` (next) - Execute next line
   - `s` (step) - Step into function
   - `c` (continue) - Continue execution
   - `l` (list) - Show current code
   - `p variable` - Print variable value
   - `pp variable` - Pretty print variable
   - `q` (quit) - Exit debugger

### Example Usage

```python
# In agent/test.py
import pdb; pdb.set_trace()  # Breakpoint here
print(json.dumps(session.to_json(), indent=2))
```

**When you run**:
```bash
python agent/test.py
```

**You'll see**:
```
> c:\...\agent\test.py(117)<module>()
-> print(json.dumps(session.to_json(), indent=2))
(Pdb) p session.session_id
'test-session-001'
(Pdb) pp session.state
{'goal_satisfied': True, 'final_answer': '...', ...}
(Pdb) n  # Continue to next line
```

---

## Option 2: VS Code/Cursor Built-in Debugger (Recommended)

VS Code/Cursor has a better visual debugger. No pdb needed!

### Step 1: Create Launch Configuration

Create `.vscode/launch.json` in your project root:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": false
        },
        {
            "name": "Python: agent/test.py",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/agent/test.py",
            "console": "integratedTerminal",
            "justMyCode": false,
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Python: my_test_10.py",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/Tests/my_test_10.py",
            "console": "integratedTerminal",
            "justMyCode": false,
            "cwd": "${workspaceFolder}"
        }
    ]
}
```

### Step 2: Install Python Extension (if not already)

1. Press `Ctrl+Shift+X`
2. Search: `Python`
3. Install: **Python** extension by Microsoft

### Step 3: Set Breakpoints

1. **Click in the gutter** (left of line numbers) to set a breakpoint
2. Or press `F9` on the line
3. Red dot appears = breakpoint set

### Step 4: Start Debugging

1. Press `F5` (or click Debug icon in sidebar)
2. Select configuration (e.g., "Python: agent/test.py")
3. Execution stops at breakpoints
4. Use debug controls:
   - `F10` - Step Over
   - `F11` - Step Into
   - `Shift+F11` - Step Out
   - `F5` - Continue
   - `Shift+F5` - Stop

### Step 5: Inspect Variables

- **Variables panel**: Shows all variables in scope
- **Watch panel**: Add expressions to watch
- **Hover**: Hover over variables to see values
- **Debug Console**: Type Python code to inspect

---

## Option 3: Using breakpoint() (Python 3.7+)

Modern Python has a built-in `breakpoint()` function:

```python
# Instead of: import pdb; pdb.set_trace()
breakpoint()  # Simpler, works the same way
```

**Usage**:
```python
# In agent/test.py
breakpoint()  # Will use pdb by default
print(json.dumps(session.to_json(), indent=2))
```

**To use a different debugger**, set environment variable:
```bash
export PYTHONBREAKPOINT=ipdb.set_trace  # If you install ipdb
```

---

## Comparison: pdb vs VS Code Debugger

| Feature | pdb (Terminal) | VS Code Debugger |
|---------|----------------|------------------|
| **Installation** | Built-in ✅ | Built-in ✅ |
| **Visual Interface** | ❌ Terminal only | ✅ GUI with panels |
| **Breakpoints** | Code-based | Click to set |
| **Variable Inspection** | `p variable` | Hover/panel |
| **Step Through** | `n`, `s` commands | `F10`, `F11` keys |
| **Call Stack** | `w` command | Visual stack view |
| **Watch Expressions** | Manual `p` | Watch panel |
| **Ease of Use** | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## Recommended Setup

### For Quick Debugging (pdb)
```python
# Add where you want to break
import pdb; pdb.set_trace()
# or
breakpoint()
```

### For Better Experience (VS Code)
1. Create `.vscode/launch.json` (see above)
2. Set breakpoints by clicking in gutter
3. Press `F5` to start debugging
4. Use debug panels to inspect

---

## Example: Debugging agent/test.py

### Using pdb:
```python
# Line 117 in agent/test.py
import pdb; pdb.set_trace()
print(json.dumps(session.to_json(), indent=2))
```

Run:
```bash
python agent/test.py
```

### Using VS Code:
1. Open `agent/test.py`
2. Click left of line 118 to set breakpoint
3. Press `F5`
4. Select "Python: agent/test.py"
5. Debugger stops at breakpoint
6. Inspect `session` variable in Variables panel

---

## Troubleshooting

### pdb Not Working?

1. **Check Python version**: `python --version` (should be 3.7+)
2. **Check if code is reached**: Add `print("Debug point reached")` before pdb
3. **Terminal issues**: Make sure you're running in a terminal that supports input

### VS Code Debugger Not Working?

1. **Install Python extension**: `Ctrl+Shift+X` → Search "Python"
2. **Select Python interpreter**: `Ctrl+Shift+P` → "Python: Select Interpreter"
3. **Check launch.json**: Ensure it's in `.vscode/launch.json`
4. **Check file path**: Ensure `program` path is correct

---

## Quick Reference

### pdb Commands
- `n` - Next line
- `s` - Step into
- `c` - Continue
- `l` - List code
- `p var` - Print variable
- `pp var` - Pretty print
- `w` - Show stack
- `q` - Quit

### VS Code Debug Keys
- `F5` - Start/Continue
- `F9` - Toggle breakpoint
- `F10` - Step Over
- `F11` - Step Into
- `Shift+F11` - Step Out
- `Shift+F5` - Stop

---

## Best Practice

**For development**: Use VS Code debugger (visual, easier)
**For quick checks**: Use `breakpoint()` or `pdb.set_trace()`
**For production**: Remove all debug statements before deploying

