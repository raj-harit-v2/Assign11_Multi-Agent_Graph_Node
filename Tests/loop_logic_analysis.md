# Loop Logic Analysis

## Current Configuration

From `config/profiles.yaml`:
```yaml
max_steps: 3                  # max sequential agent steps
max_lifelines_per_step: 3      # retries for each step (after primary failure)
```

## Understanding the Limits

### `max_steps: 3`
- **Meaning**: Maximum number of sequential steps the agent can execute for a SINGLE query
- **Scope**: Per query execution
- **Example**: If a query needs 5 steps, it will stop at step 3 and trigger human-in-loop

### `max_lifelines_per_step: 3`
- **Meaning**: Maximum number of retries for EACH step when a tool fails
- **Scope**: Per step execution (not per query)
- **Example**: If step 1 fails, it will retry up to 3 times before giving up
- **Note**: This is the same as `MAX_RETRIES` but defined in profiles.yaml

## Current Implementation Issue

**Problem**: `max_lifelines_per_step` is defined in `profiles.yaml` but **NOT actually used** in the code.

**Current Code Behavior**:
- Uses `MAX_RETRIES` from environment variables (`.env` file)
- `ControlManager` reads from `os.getenv("MAX_RETRIES", "3")`
- `profiles.yaml` values are ignored

## Test Execution Flow

### `Tests/my_test_10.py` Structure:
```
1. Generate 10 test queries
2. For each query (loop runs 10 times):
   - Run agent_loop.run(query) ONCE
   - Log result
   - Wait 10 seconds
3. Print summary
```

**Each query runs ONCE**, not 3 times.

## What "Runs 3 Times" Might Mean

If the user sees the test running 3 times, it could be:

1. **Misunderstanding**: Thinking `max_steps: 3` means query runs 3 times
   - ❌ Wrong: `max_steps: 3` means maximum 3 steps per query
   - ✅ Correct: Query runs once, but can execute up to 3 steps

2. **Retry Logic**: Seeing 3 retries per step
   - ✅ Correct: Each step can retry up to 3 times if tool fails
   - This is `max_lifelines_per_step: 3` in action

3. **Multiple Test Executions**: Test file being called 3 times
   - Need to check if test is being imported/executed multiple times

## Recommended Fix

1. **Load `max_lifelines_per_step` from profiles.yaml** and use it instead of environment variable
2. **Clarify documentation** that:
   - `max_steps` = max steps per query (not query executions)
   - `max_lifelines_per_step` = max retries per step (not query executions)
3. **Ensure test runs once** per query

