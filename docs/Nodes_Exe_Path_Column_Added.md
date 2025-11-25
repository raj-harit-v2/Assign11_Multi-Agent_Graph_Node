# Nodes_Exe_Path Column Added to tool_performance.csv

## Summary

Added a new column `Nodes_Exe_Path` to `tool_performance.csv` to display the execution path in arrow-separated format (e.g., "0->0F1->0F2->1->2->2F1").

## Changes Made

### 1. Updated `utils/csv_manager.py`

- **Added `Nodes_Exe_Path` to CSV headers** (line 34)
  - Column position: After `Node_Count`, last column
  
- **Added `_format_execution_path()` method** (lines 295-313)
  - Converts JSON array of node IDs to arrow-separated string
  - Example: `["0", "0F1", "0F2", "1", "2", "2F1"]` → `"0->0F1->0F2->1->2->2F1"`
  - Returns empty string if no nodes provided

- **Updated `log_tool_performance()` method signature** (line 335)
  - Added parameter: `nodes_exe_path: str = ""`
  - If provided, uses the provided path
  - If not provided, automatically generates from `nodes_called`

- **Updated row writing** (line 380)
  - Includes `execution_path` in the CSV row

### 2. Updated `utils/migrate_csv_v2.py`

- **Added `Nodes_Exe_Path` to migration columns** (line 42)
  - Migration script will add this column to existing CSV files
  - Populates with empty string for existing records

### 3. Updated `Tests/diagnostic_test_v2.py`

- **Updated CSV logging calls** (lines 141, 190)
  - Added `nodes_exe_path` parameter to both success and error cases
  - Example: `nodes_exe_path="0->1->2"`

## Column Format

### Format
- Arrow-separated string: `"0->0F1->0F2->1->2->2F1"`
- Shows the sequential execution order of nodes
- Includes fallback nodes (e.g., `0F1`, `0F2`, `2F1`)

### Examples

**Simple execution (no fallbacks):**
- `Nodes_Called`: `["0", "1", "2"]`
- `Nodes_Exe_Path`: `"0->1->2"`

**With fallbacks:**
- `Nodes_Called`: `["0", "0F1", "0F2", "1", "2", "2F1"]`
- `Nodes_Exe_Path`: `"0->0F1->0F2->1->2->2F1"`

**Empty/No execution:**
- `Nodes_Called`: `[]`
- `Nodes_Exe_Path`: `""`

## CSV Schema

The `tool_performance.csv` now includes:

```
Test_Id, Query_Id, Query_Name, Query_Text, Query_Answer, Plan_Used, Result_Status,
Start_Datetime, End_Datetime, Elapsed_Time, Plan_Step_Count,
Tool_Name, Retry_Count, Error_Message, Final_State,
Api_Call_Type, Step_Details, Nodes_Called, Nodes_Compact, Node_Count, Nodes_Exe_Path
```

## Usage

### Automatic Generation

If `nodes_exe_path` is not provided, it will be automatically generated from `nodes_called`:

```python
csv_manager.log_tool_performance(
    # ... other parameters ...
    nodes_called=json.dumps(["0", "1", "2"]),
    # nodes_exe_path will be automatically set to "0->1->2"
)
```

### Manual Specification

You can also provide the execution path explicitly:

```python
csv_manager.log_tool_performance(
    # ... other parameters ...
    nodes_called=json.dumps(["0", "1", "2"]),
    nodes_exe_path="0->1->2"  # Explicit path
)
```

## Migration

To migrate existing CSV files:

```powershell
python utils\migrate_csv_v2.py
```

This will:
1. Backup existing `tool_performance.csv` to `tool_performance.csv.backup_v2`
2. Add the new `Nodes_Exe_Path` column
3. Populate with empty strings for existing records (or generate from `Nodes_Called` if available)

## Testing

Test the execution path formatting:

```python
from utils.csv_manager import CSVManager
import json

cm = CSVManager()
test_path = cm._format_execution_path(json.dumps(['0', '0F1', '0F2', '1', '2', '2F1']))
print(test_path)  # Output: "0->0F1->0F2->1->2->2F1"
```

## Related Columns

- **Nodes_Called**: JSON array of node IDs `["0", "0F1", "0F2", "1", "2", "2F1"]`
- **Nodes_Compact**: Compact variant format `"F2A, A, F1A"`
- **Node_Count**: Number of nodes executed `6`
- **Nodes_Exe_Path**: Execution path string `"0->0F1->0F2->1->2->2F1"` ← **NEW**

## Backward Compatibility

- The `nodes_exe_path` parameter is optional (defaults to `""`)
- Existing code calling `log_tool_performance()` without this parameter will continue to work
- The execution path will be automatically generated from `nodes_called` if not provided

