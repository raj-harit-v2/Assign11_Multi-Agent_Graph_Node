# Step Analysis for Session 10 Agent

## Maximum Steps Per Query

### Hard Limit
- **MAX_STEPS = 3** (enforced by ControlManager)
- Step index is 0-based
- Limit checked: `current_step_index >= MAX_STEPS`

### Step Flow Scenarios

#### Scenario 1: Early Exit (0 Steps)
- **Perception answers query** (original_goal_achieved = True)
- **Steps executed**: 0
- **Exit point**: After initial perception

#### Scenario 2: Single Step Success (1 Step)
- Initial decision creates plan
- Step 0 executes successfully
- Perception evaluates: original_goal_achieved = True
- **Steps executed**: 1
- **Exit point**: After step 0 evaluation

#### Scenario 3: Multi-Step Success (2-3 Steps)
- Step 0: Executes, local_goal_achieved = True
- Step 1: Executes, local_goal_achieved = True
- Step 2: Executes, original_goal_achieved = True
- **Steps executed**: 2-3
- **Exit point**: When original_goal_achieved = True

#### Scenario 4: Replanning (Still Max 3 Steps)
- Step 0: Fails or unhelpful
- Replan: Creates new plan version
- Step 1: Executes (from new plan)
- Step 2: Executes
- **Steps executed**: Up to 3 total (across all plan versions)
- **Exit point**: When goal achieved or limit reached

#### Scenario 5: Step Limit Reached (3 Steps + Human Intervention)
- Step 0: Executes
- Step 1: Executes
- Step 2: Executes
- Step 3: Limit check triggers human-in-loop
- Human provides CONCLUDE step
- **Steps executed**: 3 + 1 CONCLUDE = 4 total (but CONCLUDE is termination)
- **Exit point**: After human-provided CONCLUDE

### Step Counting Logic

The `get_next_step_index()` method counts:
- All steps across all plan versions
- Each executed step increments the counter
- Replanning doesn't reset the counter

### Step Types

1. **CODE**: Executes tool/code, can be retried (MAX_RETRIES = 3)
2. **CONCLUDE**: Terminates execution immediately
3. **NOP**: Terminates execution (clarification needed)

### Early Termination Conditions

1. **Perception answers query** (before any steps)
2. **Step achieves original goal** (original_goal_achieved = True)
3. **CONCLUDE step executed**
4. **NOP step executed**
5. **MAX_STEPS limit reached** (triggers human-in-loop, then CONCLUDE)

### Summary

| Scenario | Min Steps | Max Steps | Notes |
|----------|-----------|-----------|-------|
| Early exit | 0 | 0 | Perception answers |
| Single step | 1 | 1 | First step succeeds |
| Multi-step | 2 | 3 | Normal execution |
| With replanning | 1 | 3 | Failed steps trigger replan |
| Limit reached | 3 | 3 | Human-in-loop triggered |
| Human intervention | 3 | 4 | 3 steps + 1 CONCLUDE |

**Key Points:**
- Maximum steps without human: **3**
- Maximum steps with human: **3 execution steps + 1 CONCLUDE step**
- Each step can have up to **3 retries** (MAX_RETRIES)
- Replanning creates new plan versions but doesn't increase step count beyond limit

