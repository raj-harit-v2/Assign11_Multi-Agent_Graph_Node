# Result Status Logic Flow

## Current Flow (BEFORE FIX)

```mermaid
flowchart TD
    Start[Agent Loop Starts] --> CheckGoal{Goal Achieved?}
    
    CheckGoal -->|Yes| Success[Mark Success<br/>result_status = 'success']
    CheckGoal -->|No| CheckSteps{Steps < MAX_STEPS?}
    
    CheckSteps -->|Yes| ExecuteStep[Execute Step]
    CheckSteps -->|No| LimitReached[Step Limit Reached]
    
    ExecuteStep --> CheckRetries{Retries < MAX_RETRIES?}
    CheckRetries -->|Yes| Retry[Retry Tool]
    CheckRetries -->|No| ToolFailed[Tool Failed<br/>Human-in-Loop]
    
    Retry --> ExecuteStep
    ToolFailed --> GetUserResult[User Provides Result]
    GetUserResult --> EvaluateStep[Evaluate Step Result]
    
    LimitReached --> HumanLoop[Human-in-Loop<br/>Plan Failure]
    HumanLoop --> UserPlan{User Plan?}
    
    UserPlan -->|Conclude| SetGoalTrue[Set original_goal_achieved = TRUE<br/>❌ WRONG!]
    UserPlan -->|New Plan| ExecuteStep
    
    EvaluateStep --> CheckLocalGoal{Local Goal Achieved?}
    CheckLocalGoal -->|Yes| CheckSteps
    CheckLocalGoal -->|No| PlanFailed[Plan Failed]
    
    PlanFailed --> HumanLoop
    
    SetGoalTrue --> DetermineStatus[Determine result_status]
    EvaluateStep --> DetermineStatus
    Success --> DetermineStatus
    
    DetermineStatus --> CheckState{original_goal_achieved == True?}
    CheckState -->|Yes| MarkSuccess[result_status = 'success'<br/>❌ WRONG for 'Conclude with current results']
    CheckState -->|No| MarkFailure[result_status = 'failure']
    
    MarkSuccess --> LogCSV[Log to CSV]
    MarkFailure --> LogCSV
    
    style SetGoalTrue fill:#ffcccc
    style MarkSuccess fill:#ffcccc
    style LimitReached fill:#ffe6cc
    style PlanFailed fill:#ffe6cc
```

## Problem

1. **Step Limit Reached**: When MAX_STEPS is reached, code sets `original_goal_achieved=True` (line 103) even though goal wasn't achieved
2. **Plan Failed**: When plan fails and user provides "Conclude with current results", it's marked as success
3. **Result Status**: Always checks `original_goal_achieved` but doesn't check if we're concluding due to failure

## Fixed Flow (AFTER FIX)

```mermaid
flowchart TD
    Start[Agent Loop Starts] --> CheckGoal{Goal Achieved?}
    
    CheckGoal -->|Yes| Success[Mark Success<br/>result_status = 'success']
    CheckGoal -->|No| CheckSteps{Steps < MAX_STEPS?}
    
    CheckSteps -->|Yes| ExecuteStep[Execute Step]
    CheckSteps -->|No| LimitReached[Step Limit Reached]
    
    ExecuteStep --> CheckRetries{Retries < MAX_RETRIES?}
    CheckRetries -->|Yes| Retry[Retry Tool]
    CheckRetries -->|No| ToolFailed[Tool Failed<br/>Human-in-Loop]
    
    Retry --> ExecuteStep
    ToolFailed --> GetUserResult[User Provides Result]
    GetUserResult --> EvaluateStep[Evaluate Step Result]
    
    LimitReached --> HumanLoop[Human-in-Loop<br/>Plan Failure]
    HumanLoop --> UserPlan{User Plan?}
    
    UserPlan -->|'Conclude with current results'| CheckActualGoal{Actual Goal Achieved?}
    UserPlan -->|New Plan| ExecuteStep
    
    CheckActualGoal -->|No| SetGoalFalse[Set original_goal_achieved = FALSE<br/>✅ CORRECT]
    CheckActualGoal -->|Yes| SetGoalTrue[Set original_goal_achieved = TRUE]
    
    EvaluateStep --> CheckLocalGoal{Local Goal Achieved?}
    CheckLocalGoal -->|Yes| CheckSteps
    CheckLocalGoal -->|No| PlanFailed[Plan Failed]
    
    PlanFailed --> HumanLoop
    
    SetGoalFalse --> DetermineStatus[Determine result_status]
    SetGoalTrue --> DetermineStatus
    EvaluateStep --> DetermineStatus
    Success --> DetermineStatus
    
    DetermineStatus --> CheckState{original_goal_achieved == True?}
    CheckState -->|Yes| CheckAnswer{Answer is 'Conclude...'?}
    CheckState -->|No| MarkFailure[result_status = 'failure'<br/>✅ CORRECT]
    
    CheckAnswer -->|Yes| MarkFailure
    CheckAnswer -->|No| MarkSuccess[result_status = 'success'<br/>✅ CORRECT]
    
    MarkSuccess --> LogCSV[Log to CSV]
    MarkFailure --> LogCSV
    
    style SetGoalFalse fill:#ccffcc
    style MarkFailure fill:#ccffcc
    style MarkSuccess fill:#ccffcc
    style LimitReached fill:#ffe6cc
    style PlanFailed fill:#ffe6cc
```

## Key Changes

1. **Detect Conclusion Due to Failure**: Check if final answer contains "Conclude with current results" or similar
2. **Don't Set Goal Achieved on Limit**: When step limit is reached, only set `original_goal_achieved=True` if goal was actually achieved
3. **Check Answer Content**: Even if `original_goal_achieved=True`, check if answer indicates failure
4. **Proper Status**: Mark as "failure" when concluding due to limits/failures

## Decision Logic

```python
# Pseudo-code for fixed logic
if original_goal_achieved == True:
    # Check if we're concluding due to failure
    if final_answer contains "Conclude with current results":
        result_status = "failure"  # Didn't actually achieve goal
    else:
        result_status = "success"  # Actually achieved goal
else:
    result_status = "failure"  # Goal not achieved
```

