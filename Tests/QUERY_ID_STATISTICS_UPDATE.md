# Query_Id Added to Statistics Generator

## Summary

`Query_Id` has been added to `utils/statistics_generator.py` to enable better tracking and cross-referencing of statistics for each unique query_text.

## Changes Made

### 1. Statistics Generation (`generate_statistics()`)

- Added `query_id` field to the `by_query_text` data structure
- Extracts `Query_Id` from each record in `tool_performance.csv`
- Stores the `Query_Id` for each unique `query_text` (uses first encountered Query_Id)

### 2. CSV Output (`save_statistics_csv()`)

- Added `Query_Id` as the **first column** in `data/query_statistics.csv`
- Enables easy cross-referencing with:
  - `data/tool_performance.csv` (via Query_Id)
  - `data/query_text.csv` (via Query_Id)

**New CSV Structure:**
```
Query_Id, Query_Text, Query_Name, Total_Attempts, Successes, Failures, 
Success_Rate_Percent, Total_Time_Seconds, Avg_Time_Seconds, 
Min_Time_Seconds, Max_Time_Seconds
```

### 3. Markdown Output (`format_statistics()`)

- Added `Query_Id` column to the "Query Text Statistics" table
- Shows Query_Id for each query in the top 20 queries by attempts

## Benefits

1. **Cross-Referencing**: Query_Id enables linking statistics back to:
   - Original query records in `query_text.csv`
   - Performance records in `tool_performance.csv`
   - Specific test runs and their details

2. **Better Tracking**: Each unique query_text can now be uniquely identified across all CSV files

3. **Data Integrity**: Query_Id provides a reliable way to join data from different sources

## Verification

Tested with 100 queries - all queries have Query_Id successfully extracted and included in statistics.

**Test Results:**
- ✅ 100/100 queries have Query_Id
- ✅ Query_Id appears as first column in CSV
- ✅ Query_Id appears in markdown table
- ✅ Query_Id values match those in tool_performance.csv

## Usage Example

```python
from utils.statistics_generator import StatisticsGenerator

generator = StatisticsGenerator()

# Generate statistics (includes Query_Id)
stats = generator.generate_statistics()

# Save CSV with Query_Id
csv_path = generator.save_statistics_csv()

# Access Query_Id for a specific query
for query_text, data in stats["by_query_text"].items():
    query_id = data["query_id"]
    print(f"Query_Id: {query_id}, Query: {query_text[:50]}")
```

## Cross-Reference Example

With Query_Id, you can now:

1. **Find all performance records for a query:**
   ```python
   # In tool_performance.csv, filter by Query_Id = 5
   # to see all test runs for that query
   ```

2. **Link to query master table:**
   ```python
   # In query_text.csv, find Query_Id = 5
   # to see the original query details
   ```

3. **Join statistics with performance data:**
   ```python
   # Use Query_Id to join query_statistics.csv with tool_performance.csv
   # for comprehensive analysis
   ```

## Files Modified

- `utils/statistics_generator.py`: Added Query_Id extraction and inclusion
- `data/query_statistics.csv`: Will include Query_Id when regenerated
- `Tests/Result_Stats.md`: Will include Query_Id in table when regenerated

