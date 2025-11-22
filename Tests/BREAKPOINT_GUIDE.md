# Strategic Breakpoint Locations Guide

This guide identifies the best places to add breakpoints for debugging the multi-agent system.

## 🎯 Top Priority Breakpoints

### 1. **Agent Loop Entry Point** (Most Important)
**File:** `agent/agent_loop2.py`  
**Location:** Line ~29 (in `run` method, right after start)

```python
async def run(self, query: str, test_id: int = None, query_id: int = None, query_name: str = "Test query for diagnostic"):
    session_start_time = time.perf_counter()
    start_datetime = get_current_datetime()
    
    breakpoint()  # ← ADD HERE: Inspect query, test_id, query_id
    
    # Generate or use provided query_id
    if query_id is None:
        query_id = self.csv_manager.add_query(query_text=query, query_name=query_name)
```

**Why:** First point of entry - inspect input parameters, session initialization.

---

### 2. **After Initial Perception** (Critical Decision Point)
**File:** `agent/agent_loop2.py`  
**Location:** Line ~80-90 (after first `perception.run`)

```python
# Step 0: Initial Perception
perception_input = self.perception.build_perception_input(...)
perception_result = self.perception.run(perception_input)

breakpoint()  # ← ADD HERE: Inspect perception_result, check if goal_achieved

session.add_perception(PerceptionSnapshot(**perception_result))

# EXIT early if perception is confident
if perception_result.get("original_goal_achieved"):
    breakpoint()  # ← ADD HERE: Inspect early exit condition
    session.mark_complete(...)
    return session
```

**Why:** Determines if agent can answer immediately or needs planning.

---

### 3. **After Decision/Planning** (Plan Generation)
**File:** `agent/agent_loop2.py`  
**Location:** Line ~120-140 (after `decision.run`)

```python
# Decision: Generate plan
decision_input = {
    "plan_mode": "initial" if step_index == 0 else "mid_session",
    "planning_strategy": self.strategy,
    "original_query": query,
    "perception": perception_result,
    "completed_steps": completed_steps,
    "available_tools": available_tools
}
decision_output = self.decision.run(decision_input)

breakpoint()  # ← ADD HERE: Inspect plan_text, step_index, step type

step = Step(
    index=decision_output["step_index"],
    description=decision_output["description"],
    type=decision_output["type"],
    code=ToolCode(decision_output.get("code", "")),
    conclusion=decision_output.get("conclusion", "")
)
```

**Why:** See what plan the agent generated, what tools it chose.

---

### 4. **Before Tool Execution** (Code Execution Start)
**File:** `agent/agent_loop2.py`  
**Location:** Line ~250-270 (in `execute_step` method)

```python
async def execute_step(self, step: Step, session: AgentSession, query: str) -> dict:
    if step.type == "CODE":
        code = step.code.code if step.code else ""
        
        breakpoint()  # ← ADD HERE: Inspect code, step.description, completed_steps
        
        completed_steps = session.get_completed_steps()
        execution_result = await run_user_code(
            code=code,
            multi_mcp=self.multi_mcp,
            step_description=step.description,
            query=query,
            completed_steps=completed_steps
        )
```

**Why:** Inspect code before execution, check tool calls, parameters.

---

### 5. **After Tool Execution** (Execution Result)
**File:** `agent/agent_loop2.py`  
**Location:** Line ~270-290 (after `run_user_code`)

```python
execution_result = await run_user_code(...)

breakpoint()  # ← ADD HERE: Inspect execution_result, status, retry_count

step.execution_result = execution_result
step.status = "completed" if execution_result["status"] == "success" else "failed"
```

**Why:** Check if tool execution succeeded, inspect results, retry count.

---

### 6. **Step Evaluation** (Goal Achievement Check)
**File:** `agent/agent_loop2.py`  
**Location:** Line ~375-420 (in `evaluate_step` method)

```python
def evaluate_step(self, step, session, query):
    if step.perception and not step.perception.local_goal_achieved:
        # Plan failed - trigger human-in-loop
        breakpoint()  # ← ADD HERE: Inspect failed step, perception
        
        next_index = session.get_next_step_index()
        is_limit_reached, limit_message = self.control_manager.check_step_limit(next_index)
        
        if is_limit_reached:
            breakpoint()  # ← ADD HERE: Inspect step limit reached
            # Trigger human-in-loop
            context = {...}
            new_plan, user_plan_dict = ask_user_for_plan(context, suggested_plan, session.session_id)
```

**Why:** Debug plan failures, step limits, human-in-loop triggers.

---

### 7. **Human-in-Loop Entry** (User Intervention)
**File:** `core/human_in_loop.py`  
**Location:** Line ~45 (in `ask_user_for_plan`)

```python
def ask_user_for_plan(context: dict, suggested_plan: list, session_id: str = None) -> tuple[list, Optional[dict]]:
    print("\n" + "=" * 60)
    print("[HUMAN-IN-LOOP] Plan Failure Detected")
    print("=" * 60)
    
    breakpoint()  # ← ADD HERE: Inspect context, suggested_plan, session_id
    
    print(f"Reason: {context.get('reason', 'Unknown')}")
    print(f"Current Step: {context.get('step_count', 'N/A')}")
    print(f"Max Steps: {context.get('max_steps', 'N/A')}")
```

**Why:** Debug when and why human intervention is triggered.

---

### 8. **Tool Retry Logic** (Retry Mechanism)
**File:** `action/executor.py`  
**Location:** Line ~110-185 (in retry loop)

```python
while retry_count < max_retries:
    try:
        # ... code execution ...
        
        if hasattr(result_value, "isError") and getattr(result_value, "isError", False):
            breakpoint()  # ← ADD HERE: Inspect tool error, retry_count
            
            error_msg = result_value.content[0].text.strip()
            last_error = error_msg
            retry_count += 1
            if retry_count < max_retries:
                print(f"Tool error: {error_msg}. Retrying ({retry_count}/{max_retries})...")
                continue
            else:
                break
```

**Why:** Debug tool failures, retry logic, error handling.

---

### 9. **CSV Logging** (Data Persistence)
**File:** `agent/agent_loop2.py`  
**Location:** Line ~450-500 (before CSV logging)

```python
# Determine result status
original_goal_achieved = session.state.get("original_goal_achieved", False)
final_answer = session.state.get("final_answer") or session.state.get("solution_summary") or ""

breakpoint()  # ← ADD HERE: Inspect final state, result_status logic

is_conclusion_due_to_failure = (
    "conclude with current results" in final_answer.lower() or
    ("conclude" in final_answer.lower() and "current results" in final_answer.lower())
)

if original_goal_achieved and not is_conclusion_due_to_failure:
    result_status = "success"
else:
    result_status = "failure"

# Log to CSV
self.csv_manager.log_tool_performance(...)
```

**Why:** Verify CSV data before logging, check result_status logic.

---

### 10. **Perception JSON Parsing** (Error Handling)
**File:** `perception/perception.py`  
**Location:** Line ~70-95 (JSON parsing)

```python
raw_text = response.text.strip()

try:
    json_block = raw_text.split("```json")[1].split("```")[0].strip()
    output = json.loads(json_block)
    
    breakpoint()  # ← ADD HERE: Inspect parsed JSON, check required fields
    
    # Patch missing fields
    required_fields = {...}
    for key, default in required_fields.items():
        output.setdefault(key, default)
    
    return output

except Exception as e:
    breakpoint()  # ← ADD HERE: Inspect raw_text, error details
    print("❌ EXCEPTION IN PERCEPTION:", e)
    return {...}
```

**Why:** Debug LLM response parsing, JSON extraction errors.

---

### 11. **Decision JSON Parsing** (Error Handling)
**File:** `decision/decision.py`  
**Location:** Line ~70-100 (JSON parsing)

```python
raw_text = response.text.strip()

try:
    json_block = raw_text.split("```json")[1].split("```")[0].strip()
    output = json.loads(json_block)
    
    breakpoint()  # ← ADD HERE: Inspect decision output, plan_text
    
    # Patch missing fields
    required_fields = {...}
    for key, default in required_fields.items():
        output.setdefault(key, default)
    
    return output

except Exception as e:
    breakpoint()  # ← ADD HERE: Inspect raw_text, parsing error
    print("❌ Unrecoverable exception while parsing LLM response:", str(e))
    return {...}
```

**Why:** Debug plan generation, JSON parsing failures.

---

## 🔍 Debugging Scenarios

### Scenario 1: Agent Not Answering Correctly
**Breakpoints:**
- #2 (After Initial Perception) - Check if perception understands query
- #3 (After Decision/Planning) - Check if plan is correct
- #4 (Before Tool Execution) - Check if tools are called correctly
- #5 (After Tool Execution) - Check if tools return correct results

### Scenario 2: Tool Failures
**Breakpoints:**
- #4 (Before Tool Execution) - Inspect code/tool calls
- #8 (Tool Retry Logic) - Debug retry mechanism
- #5 (After Tool Execution) - Check error messages

### Scenario 3: Plan Failures
**Breakpoints:**
- #6 (Step Evaluation) - Check why plan failed
- #7 (Human-in-Loop Entry) - Debug intervention triggers
- #3 (After Decision/Planning) - Check plan generation

### Scenario 4: CSV Logging Issues
**Breakpoints:**
- #9 (CSV Logging) - Inspect data before logging
- #1 (Agent Loop Entry) - Check query_id generation

### Scenario 5: LLM Response Parsing Errors
**Breakpoints:**
- #10 (Perception JSON Parsing) - Debug perception parsing
- #11 (Decision JSON Parsing) - Debug decision parsing

---

## 📝 Quick Reference: Breakpoint Locations

| Priority | File | Line | Purpose |
|----------|------|------|---------|
| ⭐⭐⭐ | `agent/agent_loop2.py` | ~29 | Entry point |
| ⭐⭐⭐ | `agent/agent_loop2.py` | ~80 | After perception |
| ⭐⭐⭐ | `agent/agent_loop2.py` | ~130 | After decision |
| ⭐⭐ | `agent/agent_loop2.py` | ~260 | Before execution |
| ⭐⭐ | `agent/agent_loop2.py` | ~280 | After execution |
| ⭐⭐ | `agent/agent_loop2.py` | ~380 | Step evaluation |
| ⭐ | `core/human_in_loop.py` | ~45 | Human intervention |
| ⭐ | `action/executor.py` | ~175 | Tool retry |
| ⭐ | `agent/agent_loop2.py` | ~460 | CSV logging |
| ⭐ | `perception/perception.py` | ~75 | Perception parsing |
| ⭐ | `decision/decision.py` | ~75 | Decision parsing |

---

## 💡 Tips

1. **Use Conditional Breakpoints:**
   ```python
   if step.type == "CODE":
       breakpoint()  # Only break for CODE steps
   ```

2. **Inspect Key Variables:**
   - `query` - Original user query
   - `session.state` - Current session state
   - `step` - Current step being executed
   - `execution_result` - Tool execution results
   - `perception_result` - Perception analysis

3. **Use VS Code Debugger:**
   - Set breakpoints by clicking in gutter (left of line number)
   - Press F5 to start debugging
   - Use debug panel to inspect variables

4. **Temporary Debug Prints:**
   ```python
   print(f"[DEBUG] Step: {step.description}")
   print(f"[DEBUG] Result: {execution_result}")
   breakpoint()
   ```

---

## 🚀 Quick Setup

Add this to your code temporarily:

```python
# At top of file
DEBUG = True  # Set to False to disable all breakpoints

# In code
if DEBUG:
    breakpoint()
```

Or use environment variable:

```python
import os
if os.getenv('DEBUG') == '1':
    breakpoint()
```

Then run: `DEBUG=1 python agent/test.py` (Unix) or `$env:DEBUG="1"; python agent/test.py` (PowerShell)

