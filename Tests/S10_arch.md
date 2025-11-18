# Session 10 Architecture Documentation

## Overview

Session 10 implements a Multi-Agent System with Distributed AI Coordination, featuring human-in-loop capabilities, strict execution limits, comprehensive logging, and automated testing.

## Architecture Components

### 1. Core Modules

#### `core/human_in_loop.py`
- **Purpose**: Handles user interaction when tools fail or plans need modification
- **Functions**:
  - `ask_user_for_tool_result()`: Prompts user when tool execution fails
  - `ask_user_for_plan()`: Prompts user to modify or approve plans when plan execution fails
- **Integration**: Called from `action/executor.py` and `agent/agent_loop2.py`

#### `core/control_manager.py`
- **Purpose**: Centralized enforcement of execution limits
- **Features**:
  - MAX_STEPS enforcement (default: 3)
  - MAX_RETRIES enforcement (default: 3)
  - Configurable via environment variables
- **Usage**: Used throughout agent loop and executor

### 2. Agent Loop

#### `agent/agent_loop2.py` (Main Agent Loop)
- **Enhanced Features**:
  - CSV logging integration
  - Step limit enforcement
  - Human-in-loop integration for plan failures
  - Query tracking via Query_Id
- **Flow**:
  1. Initialize session with query
  2. Search memory
  3. Run perception
  4. Make decision and create plan
  5. Execute steps (with limit checking)
  6. Log results to CSV
  7. Return session

### 3. Execution Layer

#### `action/executor.py`
- **Enhanced Features**:
  - Retry logic with MAX_RETRIES
  - Human-in-loop on final failure
  - Structured error reporting
  - Retry count tracking
- **Flow**:
  1. Attempt execution
  2. On error, retry up to MAX_RETRIES
  3. If all retries fail, trigger human-in-loop
  4. Return result (success or user-provided)

### 4. Data Management

#### `utils/csv_manager.py`
- **Purpose**: Manages CSV file operations
- **Files**:
  - `data/tool_performance.csv`: Performance tracking
  - `data/query_text.csv`: Query master table
- **Features**:
  - Automatic file initialization
  - Query ID generation
  - Performance logging with full context

#### `utils/time_utils.py`
- **Purpose**: Time calculation utilities
- **Functions**:
  - `get_current_datetime()`: Get formatted timestamp
  - `calculate_elapsed_time()`: Calculate execution time
  - `format_timedelta()`: Format time as human-readable string

### 5. Simulator

#### `simulator/run_simulator.py`
- **Purpose**: Batch testing system
- **Features**:
  - Runs 100+ tests automatically
  - Loads queries from file
  - Integrates with CSV logging
  - Sleep management to prevent API rate limits

#### `simulator/sleep_manager.py`
- **Purpose**: Manages sleep intervals
- **Features**:
  - Random sleep after each test (1-3 seconds)
  - Longer sleep after every 10 tests (3-10 seconds)
  - Configurable via environment variables

### 6. Statistics

#### `utils/statistics_generator.py`
- **Purpose**: Generate performance statistics
- **Features**:
  - Reads from `tool_performance.csv`
  - Calculates success/failure rates
  - Tool-specific statistics
  - Failure reason analysis
  - Outputs to `Tests/Result_Stats.md`

## Data Flow

### Query Processing Flow

1. **Input**: User query
2. **Query Registration**: Query added to `query_text.csv` with Query_Id
3. **Agent Execution**:
   - Perception → Decision → Action → Evaluation
   - Step limit checking at each iteration
   - Retry logic in executor
4. **Result Logging**: Performance data logged to `tool_performance.csv`
5. **Output**: Session with final state

### Tool Failure Flow

1. Tool execution fails
2. Retry up to MAX_RETRIES times
3. If all retries fail:
   - Trigger human-in-loop
   - User provides result
   - Continue with user-provided result
4. Log failure and retry count to CSV

### Plan Failure Flow

1. Step limit reached or plan fails
2. Check if MAX_STEPS exceeded
3. If exceeded:
   - Trigger human-in-loop
   - Present current plan and suggested plan
   - User modifies or approves plan
   - Continue with user plan
4. Log plan modification to CSV

## Execution Limits

### MAX_STEPS = 3
- Enforced in `agent/agent_loop2.py`
- Checked before each step execution
- Triggers human-in-loop when limit reached

### MAX_RETRIES = 3
- Enforced in `action/executor.py`
- Applied per tool execution
- Tracks retry count in execution result

## CSV Schema

### tool_performance.csv
- Test_Id: Sequential test number
- Query_Id: Reference to query_text.csv
- Query_Text: Original query
- Plan_Used: JSON array of plan steps
- Result_Status: "success" or "failure"
- Start_Datetime: Execution start time
- End_Datetime: Execution end time
- Elapsed_Time: Execution duration in seconds
- Plan_Step_Count: Number of steps in plan
- Tool_Name: Tool used in last step
- Retry_Count: Number of retries attempted
- Error_Message: Error message if failed
- Final_State: JSON object of final session state

### query_text.csv
- Query_Id: Unique query identifier (UUID)
- Query_Text: The query text
- Create_Datetime: When query was created
- Update_Datetime: When query was last updated
- Active_Flag: "1" for active, "0" for inactive

## Configuration

### Environment Variables (.env)
- `LLM_PROVIDER`: OLLAMA or GOOGLE
- `GEMINI_API_KEY`: For Google provider
- `OLLAMA_BASE_URL`: Ollama server URL
- `MAX_STEPS`: Maximum steps per query (default: 3)
- `MAX_RETRIES`: Maximum retries per tool (default: 3)
- `SIMULATOR_SLEEP_MIN/MAX`: Sleep intervals for simulator

## Testing Strategy

1. **Unit Tests**: Test individual modules
2. **Integration Tests**: Test agent loop with CSV logging
3. **Simulator Tests**: Run 10 queries initially
4. **Full Simulator**: Run 100+ queries with OLLAMA
5. **Provider Switch**: Test with Google API

## Key Improvements from Session 09

1. **Human-in-Loop**: Added for both tool and plan failures
2. **Execution Limits**: Strict enforcement of MAX_STEPS and MAX_RETRIES
3. **CSV Logging**: Comprehensive performance tracking
4. **Simulator**: Automated batch testing
5. **Statistics**: Automated performance analysis
6. **Query Management**: Master query table with tracking

## Design Decisions

1. **CSV over Database**: Chosen for simplicity and portability
2. **Human-in-Loop**: Interactive fallback for reliability
3. **Strict Limits**: Prevent infinite loops and resource exhaustion
4. **OLLAMA First**: Reduce API costs during development
5. **Sleep Management**: Prevent API rate limiting

