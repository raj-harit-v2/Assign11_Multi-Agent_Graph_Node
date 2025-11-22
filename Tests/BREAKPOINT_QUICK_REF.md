# Quick Breakpoint Reference

## 🎯 Top 5 Most Useful Breakpoints

### 1. Agent Entry Point
**File:** `agent/agent_loop2.py`  
**Line:** ~51 (after session creation)
```python
session = AgentSession(session_id=str(uuid.uuid4()), original_query=query)
breakpoint()  # ← ADD HERE
session_memory= []
```

### 2. After Initial Perception
**File:** `agent/agent_loop2.py`  
**Line:** ~261 (after perception.run)
```python
perception_result = self.perception.run(perception_input)
breakpoint()  # ← ADD HERE: Check if goal_achieved, inspect perception_result
print("\n[Perception Result]:")
```

### 3. After Decision/Plan Generation
**File:** `agent/agent_loop2.py`  
**Line:** ~284 (after decision.run)
```python
decision_output = self.decision.run(decision_input)
breakpoint()  # ← ADD HERE: Inspect plan_text, step type
return decision_output
```

### 4. Before Tool Execution
**File:** `agent/agent_loop2.py`  
**Line:** ~299 (in execute_step, before run_user_code)
```python
if step.type == "CODE":
    code = step.code.tool_arguments.get("code", "") if step.code else ""
    breakpoint()  # ← ADD HERE: Inspect code, step.description
    completed_steps = session.get_completed_steps()
```

### 5. After Tool Execution
**File:** `agent/agent_loop2.py`  
**Line:** ~310 (after run_user_code)
```python
execution_result = await run_user_code(...)
breakpoint()  # ← ADD HERE: Check status, result, retry_count
step.execution_result = execution_result
```

---

## 📍 All Strategic Locations

| # | File | Line | Context | Priority |
|---|------|------|---------|----------|
| 1 | `agent/agent_loop2.py` | 51 | Session creation | ⭐⭐⭐ |
| 2 | `agent/agent_loop2.py` | 261 | After perception | ⭐⭐⭐ |
| 3 | `agent/agent_loop2.py` | 59 | Early exit check | ⭐⭐ |
| 4 | `agent/agent_loop2.py` | 284 | After decision | ⭐⭐⭐ |
| 5 | `agent/agent_loop2.py` | 299 | Before execution | ⭐⭐ |
| 6 | `agent/agent_loop2.py` | 310 | After execution | ⭐⭐ |
| 7 | `agent/agent_loop2.py` | 76 | Step limit check | ⭐⭐ |
| 8 | `agent/agent_loop2.py` | 96 | Human-in-loop trigger | ⭐⭐ |
| 9 | `agent/agent_loop2.py` | 148 | Step evaluation | ⭐⭐ |
| 10 | `agent/agent_loop2.py` | 202 | Before CSV logging | ⭐ |
| 11 | `core/human_in_loop.py` | 45 | User intervention | ⭐ |
| 12 | `action/executor.py` | 175 | Tool retry logic | ⭐ |
| 13 | `perception/perception.py` | 75 | JSON parsing | ⭐ |
| 14 | `decision/decision.py` | 75 | JSON parsing | ⭐ |

---

## 🔧 How to Add Breakpoints

### Method 1: Using `breakpoint()` (Recommended)
```python
# Add this line where you want to stop
breakpoint()
```

### Method 2: Using VS Code Debugger (Best UX)
1. Click in the **gutter** (left of line number) to set a red dot
2. Press **F5** to start debugging
3. Execution will pause at breakpoints automatically

### Method 3: Conditional Breakpoint
```python
if step.type == "CODE":
    breakpoint()  # Only breaks for CODE steps
```

---

## 💡 What to Inspect at Each Breakpoint

### Breakpoint #1 (Entry)
```python
# Inspect:
query          # Original user query
test_id        # Test ID
query_id       # Query ID
session        # Session object
```

### Breakpoint #2 (After Perception)
```python
# Inspect:
perception_result                    # Full perception output
perception_result.get("original_goal_achieved")  # Can we answer immediately?
perception_result.get("entities")    # Extracted entities
perception_result.get("confidence")  # Confidence level
```

### Breakpoint #3 (After Decision)
```python
# Inspect:
decision_output["plan_text"]         # Full plan
decision_output["step_index"]        # Step number
decision_output["type"]              # CODE, CONCLUDE, or NOP
decision_output["description"]     # Step description
decision_output["code"]              # Code to execute
```

### Breakpoint #4 (Before Execution)
```python
# Inspect:
code              # Code to execute
step.description # What this step does
completed_steps   # Previous step results
step.type         # Should be "CODE"
```

### Breakpoint #5 (After Execution)
```python
# Inspect:
execution_result["status"]      # "success" or "error"
execution_result["result"]     # Tool output
execution_result["retry_count"] # Number of retries
execution_result.get("error")   # Error message if failed
```

---

## 🚨 Common Debugging Scenarios

### "Agent not answering correctly"
→ Use breakpoints #2, #3, #4, #5

### "Tool keeps failing"
→ Use breakpoints #4, #5, #12

### "Plan generation wrong"
→ Use breakpoints #2, #3

### "Human-in-loop not triggering"
→ Use breakpoints #7, #8, #9

### "CSV logging incorrect"
→ Use breakpoints #10

---

## 📝 Quick Copy-Paste Templates

### Template 1: Entry Point
```python
# agent/agent_loop2.py line ~51
session = AgentSession(session_id=str(uuid.uuid4()), original_query=query)
breakpoint()  # Entry point - inspect query, session
```

### Template 2: Perception Check
```python
# agent/agent_loop2.py line ~261
perception_result = self.perception.run(perception_input)
breakpoint()  # Check perception - goal_achieved, entities, confidence
```

### Template 3: Plan Generation
```python
# agent/agent_loop2.py line ~284
decision_output = self.decision.run(decision_input)
breakpoint()  # Check plan - plan_text, step type, code
```

### Template 4: Tool Execution
```python
# agent/agent_loop2.py line ~299
if step.type == "CODE":
    code = step.code.tool_arguments.get("code", "") if step.code else ""
    breakpoint()  # Before execution - inspect code, step
```

### Template 5: Execution Result
```python
# agent/agent_loop2.py line ~310
execution_result = await run_user_code(...)
breakpoint()  # After execution - check status, result, retries
```

---

## 🎓 Pro Tips

1. **Use VS Code's Watch Panel**: Add variables to watch panel for continuous monitoring
2. **Use Call Stack**: See how you got to the breakpoint
3. **Step Over (F10)**: Execute current line, don't enter functions
4. **Step Into (F11)**: Enter function calls
5. **Step Out (Shift+F11)**: Exit current function
6. **Continue (F5)**: Resume execution until next breakpoint

---

## 🔍 Debugging Checklist

- [ ] Added breakpoint at entry point
- [ ] Added breakpoint after perception
- [ ] Added breakpoint after decision
- [ ] Added breakpoint before tool execution
- [ ] Added breakpoint after tool execution
- [ ] Know what variables to inspect
- [ ] VS Code debugger configured (F5 works)
- [ ] Can step through code line by line

---

For detailed explanations, see `Tests/BREAKPOINT_GUIDE.md`

