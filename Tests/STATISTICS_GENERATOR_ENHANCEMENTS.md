# Statistics Generator Enhancements

## Overview

The `utils/statistics_generator.py` has been enhanced to:
1. **Create a CSV file** with statistics per unique query_text
2. **Generate graphical plots** showing success/failure rates and execution times
3. **Utilize `tool_performance.csv`** as the data source

## New Features

### 1. CSV Statistics File

**File:** `data/query_statistics.csv`

**Columns:**
- `Query_Id`: The unique query identifier (Bigint) from query_text.csv - **enables cross-referencing with tool_performance.csv and query_text.csv**
- `Query_Text`: The actual query text (truncated to 200 chars)
- `Query_Name`: The query name from the original data
- `Total_Attempts`: Number of times this query was executed
- `Successes`: Number of successful executions
- `Failures`: Number of failed executions
- `Success_Rate_Percent`: Percentage of successful executions
- `Total_Time_Seconds`: Total execution time for all attempts
- `Avg_Time_Seconds`: Average execution time per attempt
- `Min_Time_Seconds`: Minimum execution time
- `Max_Time_Seconds`: Maximum execution time

**Usage:**
```python
from utils.statistics_generator import StatisticsGenerator

generator = StatisticsGenerator()
csv_path = generator.save_statistics_csv()
```

### 2. Graphical Plots

**Location:** `data/plots/`

**Plots Generated:**

#### a) `query_success_failure_rate.png`
- Bar chart showing success and failure rates for each unique query_text
- Limited to top 20 queries by number of attempts
- Green bars = Success Rate %
- Red bars = Failure Rate %

#### b) `query_execution_time.png`
- Two-panel chart:
  - Left: Average execution time per query_text
  - Right: Total execution time per query_text
- Limited to top 20 queries

#### c) `overall_success_failure.png`
- Pie chart showing overall success/failure distribution
- Shows total number of tests and percentage breakdown

**Usage:**
```python
from utils.statistics_generator import StatisticsGenerator

generator = StatisticsGenerator()
stats = generator.generate_statistics()
generator.create_plots(stats)
```

### 3. Enhanced Statistics Generation

The `generate_statistics()` method now includes:

**New Statistics:**
- `by_query_text`: Statistics grouped by unique query_text
  - **Query_Id**: Unique identifier for cross-referencing
  - Total attempts per query
  - Successes/failures per query
  - Total, average, min, max execution times per query
- `total_time_all_queries`: Sum of all execution times

**Enhanced Markdown Output:**
- New section: "Query Text Statistics" table
- Shows top 20 queries by attempts
- Includes total time for all queries
- Shows count of unique query texts

## Data Source

**Primary Source:** `data/tool_performance.csv`

The statistics generator reads from `tool_performance.csv` via `CSVManager.get_tool_performance()`, which provides:
- All execution records
- Query text, query name, result status
- Execution times
- Tool names, retry counts
- Error messages

## Complete Usage Example

```python
from utils.statistics_generator import StatisticsGenerator

# Initialize generator
generator = StatisticsGenerator()

# Generate and save all statistics
# This will:
# 1. Create markdown report (Tests/Result_Stats.md)
# 2. Create CSV statistics (data/query_statistics.csv)
# 3. Create plots (data/plots/*.png)
formatted_stats = generator.save_statistics(
    output_path="Tests/Result_Stats.md",
    create_csv=True,
    create_plots=True
)

# Or use methods individually:
stats = generator.generate_statistics()
csv_path = generator.save_statistics_csv("data/query_statistics.csv")
generator.create_plots(stats, "data/plots")
```

## Dependencies

**Required:**
- `utils.csv_manager`: For reading `tool_performance.csv`
- Standard library: `csv`, `json`, `pathlib`, `collections`

**Optional:**
- `matplotlib>=3.8.0`: For graphical plots
  - If not installed, plots will be skipped with a warning
  - Install with: `pip install matplotlib`

## Output Files

1. **Tests/Result_Stats.md**: Markdown report with all statistics
2. **data/query_statistics.csv**: CSV file with per-query statistics
3. **data/plots/query_success_failure_rate.png**: Success/failure rates chart
4. **data/plots/query_execution_time.png**: Execution time analysis chart
5. **data/plots/overall_success_failure.png**: Overall distribution pie chart

## Key Metrics Tracked

### Per Unique Query Text:
- **Query_Id**: Unique identifier for cross-referencing with other CSV files
- Total attempts
- Success count
- Failure count
- Success rate percentage
- Total execution time
- Average execution time
- Minimum execution time
- Maximum execution time

### Overall:
- Total tests
- Total successes
- Total failures
- Overall success rate
- Average time per test
- Total time for all queries
- Unique query text count

## Notes

- Query texts are truncated in CSV (200 chars) and plots (30 chars) for readability
- Plots are limited to top 20 queries by attempts to maintain readability
- All time values are in seconds
- The generator gracefully handles missing matplotlib (plots are optional)
- CSV file is overwritten on each run

