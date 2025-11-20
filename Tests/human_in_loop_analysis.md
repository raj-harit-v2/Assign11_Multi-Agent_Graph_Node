# Human-In-Loop Implementation Analysis

## Requirement
**"If a plan fails, then add 'Human-In-Loop' and suggest a plan, and show the Agent listens"**

## Implementation Status

### ✅ **PARTIALLY IMPLEMENTED** - With Gap

### Current Implementation

#### 1. Plan Failure Detection ✅
**Location**: `agent/agent_loop2.py:334-335`
```python
else:
    print("\n🔁 Step unhelpful. Replanning.")
```
- **Status**: ✅ Implemented
- Detects when `step.perception.local_goal_achieved = False`
- Triggers replanning logic

#### 2. Human-In-Loop Trigger ⚠️
**Location**: `agent/agent_loop2.py:340-368`
```python
if is_limit_reached:
    # Human-in-loop triggered
    context = {...}
    suggested_plan = decision_output.get("plan_text", ["Conclude"])
    new_plan = ask_user_for_plan(context, suggested_plan)
```
- **Status**: ⚠️ **CONDITIONAL** - Only when step limit reached
- Human-in-loop is triggered ONLY when `current_step_index >= MAX_STEPS`
- If plan fails but step limit NOT reached, it auto-replans without human intervention

#### 3. Plan Suggestion ✅
**Location**: `agent/agent_loop2.py:349-358`
```python
decision_output = self.decision.run({
    "plan_mode": "mid_session",
    "planning_strategy": self.strategy,
    "original_query": query,
    "current_plan_version": len(session.plan_versions),
    "current_plan": session.plan_versions[-1]["plan_text"],
    "completed_steps": [...],
    "current_step": step.to_dict()
})
suggested_plan = decision_output.get("plan_text", ["Conclude"])
```
- **Status**: ✅ Implemented
- Agent generates suggested plan via Decision module
- Plan is based on current context and failed step

#### 4. Agent Listens (Uses User Input) ✅
**Location**: `agent/agent_loop2.py:359-366`
```python
new_plan = ask_user_for_plan(context, suggested_plan)

if new_plan:
    step = session.add_plan_version(new_plan, [self.create_step(decision_output)])
    print(f"\n[Decision Plan Text: V{len(session.plan_versions)}]:")
    for line in session.plan_versions[-1]["plan_text"]:
        print(f"  {line}")
    return step
```
- **Status**: ✅ Implemented
- User input from `ask_user_for_plan()` is used to create new plan version
- Agent executes the user-provided/modified plan

### Human-In-Loop Function ✅
**Location**: `core/human_in_loop.py:41-102`
- **Status**: ✅ Fully Implemented
- Displays plan failure reason
- Shows current failed plan
- Shows suggested plan
- Allows user to:
  - Accept suggested plan (Enter)
  - Modify plan (type 'modify')
  - Provide custom plan (type 'custom')
- Returns user-approved/modified plan

## Gap Analysis

### ❌ **GAP IDENTIFIED**

**Issue**: Human-in-loop is only triggered when step limit is reached, NOT on every plan failure.

**Current Flow**:
```
Plan Fails
  ↓
Check: Is step limit reached?
  ├─ YES → Human-in-loop ✅
  └─ NO → Auto-replan (no human) ❌
```

**Expected Flow** (per requirement):
```
Plan Fails
  ↓
Human-in-loop (always) ✅
  ↓
Suggest plan ✅
  ↓
Agent listens ✅
```

### Code Evidence

**Line 334-385 in agent_loop2.py**:
```python
else:
    print("\n🔁 Step unhelpful. Replanning.")
    current_step_index = session.get_next_step_index()
    is_limit_reached, limit_message = self.control_manager.check_step_limit(current_step_index)
    
    if is_limit_reached:  # ⚠️ Only triggers here
        # Human-in-loop code...
    else:  # ❌ Auto-replans without human
        decision_output = self.decision.run({...})
        step = session.add_plan_version(...)
        return step
```

## Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Plan Failure Detection | ✅ | Detects when step is unhelpful |
| Human-In-Loop Trigger | ⚠️ | Only when step limit reached |
| Plan Suggestion | ✅ | Agent generates suggested plan |
| Agent Listens | ✅ | Uses user input for new plan |
| **Always on Plan Failure** | ❌ | **Gap: Only triggers at limit** |

## Recommendation

**To fully meet requirement**: Modify `evaluate_step()` to trigger human-in-loop on EVERY plan failure, not just when step limit is reached.

**Suggested Fix**:
```python
else:
    print("\n🔁 Step unhelpful. Replanning.")
    # Always trigger human-in-loop on plan failure
    context = {
        "reason": "Plan failed - step was unhelpful",
        "current_plan": session.plan_versions[-1]["plan_text"],
        "step_count": session.get_next_step_index(),
        "max_steps": self.control_manager.get_max_steps(),
        "query": query
    }
    decision_output = self.decision.run({...})
    suggested_plan = decision_output.get("plan_text", ["Conclude"])
    new_plan = ask_user_for_plan(context, suggested_plan)  # Always ask
    
    if new_plan:
        step = session.add_plan_version(new_plan, [self.create_step(decision_output)])
        return step
    else:
        return None
```

