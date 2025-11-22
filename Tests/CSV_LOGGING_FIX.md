# CSV Logging Fix for my_test_100.py

## Problem Identified

When running `python Tests/my_test_100.py`, only 15 cases are being logged to `tool_performance.csv` instead of all 100 cases.

## Root Cause Analysis

### Current Flow

1. **agent_loop2.py** logs to CSV when `test_id is not None` (line 205-229)
2. **my_test_100.py** checks if record is already logged (line 349-362)
3. If duplicate found, skips backup logging (line 357-360)
4. If not found, performs backup logging (line 364-449)

### Potential Issues

1. **agent_loop2.py may not log all cases**:
   - If exception occurs before CSV logging (line 205)
   - If test_id is None (shouldn't happen, but possible)
   - If CSV write fails silently

2. **Duplicate check may be too aggressive**:
   - Reading CSV file may not reflect latest writes
   - File buffering/caching issues
   - Timing issues between agent_loop logging and duplicate check

3. **Exception handling may skip logging**:
   - If exception occurs in agent_loop, CSV logging may not happen
   - Backup logging should catch this, but may also fail

## Fix Applied

### Changes Made

1. **Improved duplicate detection**:
   - Better error handling in duplicate check
   - More explicit logging messages

2. **Enhanced backup logging**:
   - Always attempts to log if not found in CSV
   - Better error messages to identify when logging happens

3. **Added debug output**:
   - Shows when test is already logged
   - Shows when test is being logged (backup)
   - Helps identify which tests are missing

### Verification Steps

After running `python Tests/my_test_100.py`:

1. **Check CSV file**:
   ```powershell
   # Count records
   python -c "import csv; f = open('data/tool_performance.csv', 'r', encoding='utf-8'); reader = csv.DictReader(f); rows = list(reader); print(f'Total records: {len(rows)}'); test_ids = [int(r.get('Test_Id', 0)) for r in rows if r.get('Test_Id', '').isdigit()]; print(f'Test IDs: {min(test_ids)} to {max(test_ids)}' if test_ids else 'No test IDs')"
   ```

2. **Check for gaps**:
   ```powershell
   # Find missing test IDs
   python -c "import csv; f = open('data/tool_performance.csv', 'r', encoding='utf-8'); reader = csv.DictReader(f); rows = list(reader); test_ids = sorted([int(r.get('Test_Id', 0)) for r in rows if r.get('Test_Id', '').isdigit()]); all_ids = set(range(1, 101)); found_ids = set(test_ids); missing = sorted(all_ids - found_ids); print(f'Found: {len(found_ids)}/100'); print(f'Missing: {missing[:20]}...' if len(missing) > 20 else f'Missing: {missing}')"
   ```

3. **Check query_text.csv**:
   ```powershell
   # Count queries
   python -c "import csv; f = open('data/query_text.csv', 'r', encoding='utf-8'); reader = csv.DictReader(f); rows = list(reader); print(f'Total queries: {len(rows)}')"
   ```

## Expected Behavior

After fix:
- **All 100 tests should be logged** to `tool_performance.csv`
- **All 100 queries should be logged** to `query_text.csv`
- **No duplicates** (each test_id appears once)
- **Clear logging messages** showing which tests are logged

## If Still Only 15 Cases

If you still only see 15 cases after the fix:

1. **Check if tests are actually running**:
   - Look for "[Running Agent...]" messages
   - Check if tests are completing or failing early

2. **Check for exceptions**:
   - Look for "[ERROR]" or "[WARNING]" messages
   - Check if tests are crashing before CSV logging

3. **Check CSV file permissions**:
   - Ensure file is not locked
   - Check if file is being written to

4. **Check agent_loop2.py logging**:
   - Verify `test_id is not None` for all tests
   - Check if CSV logging is being called

5. **Run with debug output**:
   - The fix adds more logging messages
   - Watch for "[CSV] Test X already logged" vs "[CSV] Test X NOT found in CSV"

## Additional Debugging

Add this to see what's happening:

```python
# In my_test_100.py, after line 350:
print(f"[DEBUG] Checking CSV for Test {test_id}: {len(existing_records)} existing records")
print(f"[DEBUG] Looking for Test_Id={test_id}, Query_Text='{query_text[:50]}...'")
```

This will show:
- How many records are in CSV
- What we're looking for
- Whether duplicate check is working correctly

