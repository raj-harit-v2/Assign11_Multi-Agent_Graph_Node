# Agent Listens Implementation - Plan Failure

## Changes Made

### ✅ **FULLY IMPLEMENTED** - Agent now shows it listens when plan fails

## Implementation Details

### 1. Modified `agent/agent_loop2.py` (Lines 334-375)

**Before**: Human-in-loop only triggered when step limit reached
**After**: Human-in-loop **ALWAYS** triggered when plan fails

#### Key Changes:
- Removed conditional check for step limit
- Always triggers human-in-loop on plan failure
- Added explicit "Agent is listening" messages
- Shows agent receives and implements user plan

#### Code Flow:
```python
else:  # Plan failed
    print("\n🔁 Step unhelpful. Plan failed. Requesting human guidance...")
    
    # Always trigger human-in-loop (not conditional)
    context = {...}
    suggested_plan = decision_output.get("plan_text", ["Conclude"])
    
    # Show agent is listening
    print("\n👂 Agent is listening for your guidance...")
    new_plan = ask_user_for_plan(context, suggested_plan)
    
    # Agent uses user's plan (shows agent listens)
    if new_plan:
        print("\n✅ Agent received your plan. Implementing...")
        step = session.add_plan_version(new_plan, ...)
        print(f"\n[Decision Plan Text: V{len(session.plan_versions)}] (User-guided):")
        return step
```

### 2. Enhanced `core/human_in_loop.py` (Lines 71-74)

**Added visual indicators**:
- `🤖 Agent's suggested new plan:` - Shows agent's suggestion
- `👂 Agent is listening for your input...` - Shows agent is waiting

## Behavior Now

### When Plan Fails:

1. **Agent detects failure** → "Step unhelpful. Plan failed."
2. **Agent generates suggestion** → Decision module creates new plan
3. **Agent shows it's listening** → "👂 Agent is listening for your guidance..."
4. **Human-in-loop triggered** → User sees:
   - Failed plan
   - Agent's suggested plan
   - Options to accept/modify/customize
5. **Agent receives input** → "✅ Agent received your plan. Implementing..."
6. **Agent implements user plan** → Creates new plan version marked "(User-guided)"

## User Experience Flow

```
Plan Fails
  ↓
🔁 Step unhelpful. Plan failed. Requesting human guidance...
  ↓
👂 Agent is listening for your guidance...
  ↓
============================================================
HUMAN-IN-LOOP: Plan Failure
============================================================
Reason: Plan failed - step was unhelpful
Current plan that failed:
  1. Step 1
  2. Step 2

🤖 Agent's suggested new plan:
  1. Alternative Step 1
  2. Alternative Step 2

👂 Agent is listening for your input...

Options:
  1. Accept suggested plan (press Enter)
  2. Modify plan (type 'modify'...)
  3. Provide custom plan (type 'custom'...)
------------------------------------------------------------
Your choice: [user input]
  ↓
✅ Agent received your plan. Implementing...
  ↓
[Decision Plan Text: V2] (User-guided):
  1. User's plan step 1
  2. User's plan step 2
```

## Verification

✅ **Syntax Check**: Passed
✅ **Linter Check**: No errors
✅ **Implementation**: Complete

## Summary

The agent now **always** shows it listens when a plan fails by:
1. Explicitly triggering human-in-loop on every plan failure
2. Displaying "Agent is listening" messages
3. Showing it received and implements the user's plan
4. Marking user-guided plans in the output

**Status**: ✅ **FULLY IMPLEMENTED**

