# User Plan Storage Usage Guide

## Overview

When a user provides a plan/answer during human-in-loop (e.g., JSON format), it is:
1. **Stored temporarily** in session memory
2. **Used in the next lifeline/retry** automatically
3. **Marked as FAILED** (not success) in Query_Status
4. **Stored in CSV/logs** after user input
5. **Removed from memory** after session finishes

## User Input Format

Users can provide plans in JSON format:

```json
{
  "original_goal_achieved": true,
  "final_answer": "Search on official website https://www.camellias.co.in/",
  "confidence": "0.8",
  "reasoning_note": "User provided final answer",
  "solution_summary": "Search on official website https://www.camellias.co.in/"
}
```

## Flow

### 1. User Provides Plan

When human-in-loop is triggered:
```
Options:
  1. Accept suggested plan (press Enter)
  2. Modify plan (type 'modify' then enter new plan steps, one per line)
  3. Provide custom plan (type 'custom' then enter plan steps, one per line)
  4. Provide JSON plan (type 'json' then paste JSON with final_answer, etc.)
```

User types: `json` and pastes JSON plan.

### 2. Plan Storage

- Plan is **parsed and validated**
- Stored in `UserPlanStorage` with session_id as key
- **NOT stored in CSV yet** - waits for session to finish

### 3. Next Lifeline/Retry

When next lifeline/retry occurs:
- System checks for stored user plan
- If found, **automatically uses it** (no user input needed)
- Prints: `[USING STORED PLAN] Using user-provided plan from previous lifeline...`

### 4. Result Status

When user provides answer:
- `original_goal_achieved` = `False` (always)
- `result_status` = `"failure"` (always)
- Reason: User-provided answers indicate agent couldn't solve it

### 5. CSV Logging

After session finishes:
- User plan is included in `final_state` JSON
- Logged to `tool_performance.csv`
- `Result_Status` = `"failure"`

### 6. Memory Cleanup

After CSV logging:
- Stored plan is **removed from memory**
- Session memory is cleaned up
- No persistent storage (temporary only)

## Example Flow

```
Step 1: Tool fails
  → Human-in-loop triggered
  → User provides JSON plan
  → Plan stored in UserPlanStorage (session_id)

Step 2: Retry (next lifeline)
  → Check UserPlanStorage
  → Found stored plan
  → Use stored plan automatically
  → Mark as FAILED
  → Continue execution

Step 3: Session finishes
  → Log to CSV (with user plan in final_state)
  → Clear UserPlanStorage
  → Done
```

## Key Points

1. **Temporary Storage**: Plans are stored temporarily (session-level)
2. **Automatic Reuse**: Stored plans are used automatically in next lifeline
3. **Always Failed**: User-provided answers always result in `result_status = "failure"`
4. **CSV Logging**: Plans are logged to CSV after user input (not before)
5. **Memory Cleanup**: Plans are removed after session finishes

## Code Structure

### `core/user_plan_storage.py`
- `UserPlanStorage` class for temporary storage
- `store_user_plan()` - Store plan
- `get_user_plan()` - Retrieve plan
- `clear_user_plan()` - Cleanup

### `core/human_in_loop.py`
- `ask_user_for_plan()` - Accepts JSON input
- Parses JSON and stores in UserPlanStorage

### `agent/agent_loop2.py`
- Checks for stored plans before asking user
- Uses stored plans automatically
- Marks as failed when user provides answer
- Cleans up after session

## CSV Output

When user provides plan, CSV will show:
- `Result_Status`: `"failure"`
- `Query_Answer`: User's final_answer
- `Final_State`: Contains `user_provided_plan` field with full JSON

