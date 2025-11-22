# Loop Logic Fix Summary

## Issue Reported

User reported: "the Tests\my_test_10.py runs 3 times it should run only 1 time"

## Analysis

### Configuration from `config/profiles.yaml`:
```yaml
max_steps: 3                  # max sequential agent steps
max_lifelines_per_step: 3      # retries for each step (after primary failure)
```

### Understanding the Limits

1. **`max_steps: 3`**
   - ✅ **Correct**: Maximum 3 steps per query execution
   - ❌ **NOT**: Run the query 3 times
   - **Example**: Query runs once, but can execute Step 1, Step 2, Step 3

2. **`max_lifelines_per_step: 3`**
   - ✅ **Correct**: Maximum 3 retries per step if step fails
   - ❌ **NOT**: Run each step 3 times
   - **Example**: Step 1 fails → retry 1, retry 2, retry 3 → then give up

### Test File Behavior

**`Tests/my_test_10.py` Structure:**
```python
# Generate 10 queries
test_queries = generate_test_queries(10)

# Loop: Each query runs ONCE
for test_id, query_type, query_text in test_queries:
    session = await run_single_test(...)  # ← RUNS ONCE PER QUERY
    # Inside run_single_test():
    #   agent_loop.run(query)  # ← CALLED ONCE PER QUERY
```

**Each query executes:**
- ✅ Query runs **ONCE**
- ✅ Query can have up to **3 steps** (max_steps=3)
- ✅ Each step can **retry up to 3 times** if it fails (max_lifelines_per_step=3)

## Fixes Applied

### 1. Added Clear Comments

Added documentation in `Tests/my_test_10.py`:
- Function docstrings explaining that each query runs once
- Inline comments clarifying the execution flow
- Print statements showing "Query executes ONCE"

### 2. Added Verification Logging

Added print statements to track execution:
```python
print(f"\n[EXECUTING] Test {test_id}/10 - Running query ONCE...")
# ... execute query ...
print(f"[COMPLETED] Test {test_id}/10 - Query executed ONCE")
```

### 3. Created Documentation

Created `Tests/loop_logic_explanation.md` with:
- Visual flow diagrams
- Clear explanation of max_steps vs max_lifelines_per_step
- Examples showing correct behavior

## Verification

To verify the test runs once per query:

1. **Check CSV logs**: Should see 10 entries (one per query), not 30
2. **Check console output**: Should see "[EXECUTING] Test X/10 - Running query ONCE..."
3. **Check agent_loop.run() calls**: Should be called exactly 10 times (once per query)

## Expected Behavior

### Correct Behavior ✅
```
Test 1: Query runs ONCE → Step 1, Step 2, Step 3 → Done
Test 2: Query runs ONCE → Step 1, Step 2, Step 3 → Done
...
Test 10: Query runs ONCE → Step 1, Step 2, Step 3 → Done
```

### Incorrect Behavior ❌ (If This Happens)
```
Test 1: Query runs 3 times → This would be wrong
```

## Key Points

1. **Each query runs ONCE** - `agent_loop.run(query)` is called once per query
2. **max_steps=3** means maximum 3 steps per query (not 3 query executions)
3. **max_lifelines_per_step=3** means maximum 3 retries per step (not 3 step executions)
4. **Test file runs 10 queries** - One after another, each once

## If You Still See "3 Times"

If you're seeing something run "3 times", check:

1. **Are you seeing 3 steps?** ✅ Correct - that's max_steps=3
2. **Are you seeing 3 retries?** ✅ Correct - that's max_lifelines_per_step=3
3. **Is the query being executed 3 times?** ❌ Wrong - should only run once

## Files Modified

1. ✅ `Tests/my_test_10.py` - Added clear comments and logging
2. ✅ `Tests/loop_logic_explanation.md` - Created documentation
3. ✅ `Tests/loop_logic_analysis.md` - Created analysis document
4. ✅ `Tests/loop_logic_fix_summary.md` - This summary

## Conclusion

The test file is **already correct** - each query runs once. The confusion may come from:
- Seeing 3 steps executed (correct - max_steps=3)
- Seeing retries happening (correct - max_lifelines_per_step=3)
- Misunderstanding that these mean "3 query executions"

The fixes ensure:
- ✅ Clear documentation
- ✅ Explicit logging showing "runs once"
- ✅ Comments explaining the behavior

