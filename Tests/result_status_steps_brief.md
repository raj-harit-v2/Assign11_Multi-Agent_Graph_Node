# Result Status Logic - Steps Overview (Brief)

## Key Steps Involved

```mermaid
graph TB
    Start[1. Agent Loop Starts] --> CheckGoal[2. Check if Goal Achieved]
    
    CheckGoal -->|Yes| Success[3. Mark as Success<br/>result_status = 'success']
    CheckGoal -->|No| CheckLimits[4. Check Limits]
    
    CheckLimits -->|MAX_STEPS| StepLimit[5. Step Limit Reached]
    CheckLimits -->|MAX_RETRIES| RetryLimit[5. Retry Limit Reached]
    CheckLimits -->|Continue| Execute[6. Execute Step]
    
    StepLimit --> HumanLoop1[7. Human-in-Loop<br/>Ask for Plan]
    RetryLimit --> HumanLoop2[7. Human-in-Loop<br/>Ask for Result]
    
    HumanLoop1 --> UserInput1{8. User Input?}
    HumanLoop2 --> UserInput2{8. User Input?}
    
    UserInput1 -->|'Conclude with...'| CheckAnswer[9. Check Answer Content]
    UserInput1 -->|New Plan| Execute
    UserInput2 -->|Result| Execute
    
    Execute --> Evaluate[10. Evaluate Step Result]
    Evaluate --> CheckGoal
    
    CheckAnswer -->|Contains 'Conclude'| MarkFailed[11. Mark as Failed<br/>result_status = 'failure']
    CheckAnswer -->|Actual Answer| MarkSuccess2[11. Mark as Success<br/>result_status = 'success']
    
    Success --> LogCSV[12. Log to CSV]
    MarkFailed --> LogCSV
    MarkSuccess2 --> LogCSV
    
    style MarkFailed fill:#ffcccc
    style MarkSuccess2 fill:#ccffcc
    style Success fill:#ccffcc
    style StepLimit fill:#ffe6cc
    style RetryLimit fill:#ffe6cc
```

## Decision Points

### Step 9: Check Answer Content (NEW LOGIC)

```python
if answer contains "Conclude with current results":
    → result_status = "failure"  # Didn't achieve goal
else:
    → result_status = "success"  # Actually achieved goal
```

## Three Scenarios

### Scenario A: Goal Actually Achieved
```
1. Execute steps
2. Goal achieved = True
3. Final answer = "The result is 42"
4. Result Status = "success" ✅
```

### Scenario B: Step Limit Reached, Concluding
```
1. Execute steps
2. MAX_STEPS reached
3. User: "Conclude with current results"
4. Goal achieved = False (FIXED)
5. Final answer = "Conclude with current results"
6. Result Status = "failure" ✅
```

### Scenario C: Retry Limit Reached, Tool Failed
```
1. Execute step
2. Tool fails
3. MAX_RETRIES reached
4. User provides result (or default)
5. Goal achieved = False
6. Result Status = "failure" ✅
```

## Files Modified

1. **agent/agent_loop2.py**
   - Step limit handling (lines 90-112)
   - Result status determination (lines 125-137)
   - evaluate_step method (lines 321-350)

2. **Tests/my_test_100.py**
   - CSV logging logic (line 373)

## Result

✅ Queries ending with "Conclude with current results" → `result_status = "failure"`  
✅ Queries actually achieving goal → `result_status = "success"`  
✅ Accurate statistics in `tool_performance.csv`

