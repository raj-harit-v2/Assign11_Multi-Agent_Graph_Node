# Session 10 - Multi-Agent Systems and Distributed AI Coordination

## Project Overview

This project implements a multi-agent system with distributed AI coordination, featuring human-in-loop capabilities, strict execution limits, comprehensive CSV logging, and automated batch testing.

## Features

### Core Features

1. **Human-In-Loop Integration**
   - Tool failure recovery: User provides result when tools fail after all retries
   - Plan failure recovery: User modifies or approves plans when execution limits are reached

2. **Execution Limits**
   - MAX_STEPS = 3: Maximum steps per query execution
   - MAX_RETRIES = 3: Maximum retries per tool execution
   - Enforced throughout the agent loop and executor

3. **CSV Logging System**
   - `tool_performance.csv`: Comprehensive performance tracking
   - `query_text.csv`: Master query table with tracking
   - Automatic query ID generation and management

4. **Automated Simulator**
   - Runs 100+ tests automatically
   - Sleep management to prevent API rate limiting
   - Configurable test count and query sources

5. **Statistics Generation**
   - Automated performance analysis
   - Tool-specific success/failure rates
   - Failure reason analysis
   - Output to `Tests/Result_Stats.md`

## Project Structure

```
Assign10_Multi-Agent/
├── core/
│   ├── human_in_loop.py      # Human-in-loop interaction
│   └── control_manager.py    # Execution limit enforcement
├── agent/
│   ├── agent_loop2.py        # Main agent loop (enhanced)
│   └── agentSession.py       # Session management
├── perception/
│   └── perception.py         # Perception module
├── decision/
│   └── decision.py           # Decision/planning module
├── action/
│   └── executor.py            # Code execution with retries
├── utils/
│   ├── csv_manager.py        # CSV file management
│   ├── statistics_generator.py # Statistics generation
│   └── time_utils.py         # Time utilities
├── simulator/
│   ├── run_simulator.py      # Main simulator
│   └── sleep_manager.py      # Sleep interval management
├── data/
│   ├── tool_performance.csv  # Performance logs (generated)
│   └── query_text.csv        # Query master table (generated)
├── Tests/
│   ├── sample_queries.txt    # Test queries
│   ├── S10_arch.md           # Architecture documentation
│   ├── S10_init_arch01.md    # Architecture diagrams (Mermaid)
│   └── Result_Stats.md       # Statistics output (generated)
├── memory/                    # Session memory and search
├── mcp_servers/              # MCP server integration
├── config/                    # Configuration files
└── .env                       # Environment variables
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:
```env
LLM_PROVIDER=OLLAMA
MAX_STEPS=3
MAX_RETRIES=3
GEMINI_API_KEY=your_key_here  # For Google provider
```

## Usage

### Interactive Mode

Run the main agent interactively:
```bash
python main.py
```

### Simulator Mode

Run automated batch testing:
```bash
python simulator/run_simulator.py [num_tests] [query_file]
```

Example:
```bash
python simulator/run_simulator.py 100 Tests/sample_queries.txt
```

### Generate Statistics

After running tests, generate statistics:
```bash
python utils/statistics_generator.py
```

## Configuration

### Environment Variables

- `LLM_PROVIDER`: OLLAMA or GOOGLE (default: OLLAMA)
- `GEMINI_API_KEY`: Google Gemini API key (for GOOGLE provider)
- `OLLAMA_BASE_URL`: Ollama server URL (default: http://localhost:11434)
- `MAX_STEPS`: Maximum steps per query (default: 3)
- `MAX_RETRIES`: Maximum retries per tool (default: 3)
- `SIMULATOR_SLEEP_MIN/MAX`: Sleep intervals for simulator

## CSV Schema

### tool_performance.csv

| Column | Description |
|--------|-------------|
| Test_Id | Sequential test number |
| Query_Id | Reference to query_text.csv |
| Query_Text | Original query |
| Plan_Used | JSON array of plan steps |
| Result_Status | "success" or "failure" |
| Start_Datetime | Execution start time |
| End_Datetime | Execution end time |
| Elapsed_Time | Execution duration (seconds) |
| Plan_Step_Count | Number of steps in plan |
| Tool_Name | Tool used in last step |
| Retry_Count | Number of retries attempted |
| Error_Message | Error message if failed |
| Final_State | JSON object of final session state |

### query_text.csv

| Column | Description |
|--------|-------------|
| Query_Id | Unique query identifier (UUID) |
| Query_Text | The query text |
| Create_Datetime | When query was created |
| Update_Datetime | When query was last updated |
| Active_Flag | "1" for active, "0" for inactive |

## Architecture Changes from Session 09

### Major Improvements

| Area | Session 09 | Session 10 |
|------|------------|------------|
| **Architecture** | Single-Agent Heuristics | Multi-Agent Distributed Coordination |
| **Planning** | Static Heuristics | Adaptive Planning + Human-in-Loop |
| **Memory** | Basic JSON logs | Dual CSV Logging + Query Master Table |
| **Failure Recovery** | Minimal | Human-in-Loop for Tool and Plan Failures |
| **Execution** | Unlimited Steps | MAX_STEPS = 3, MAX_RETRIES = 3 |
| **Testing** | Manual | 100+ Test Simulator with Sleep Management |
| **Tools** | Single LLM | Multi-Tool Orchestration (Math/Web/Ollama/Google) |
| **Statistics** | None | Automated Tool Performance Statistics |
| **Query Management** | None | Master Query Table with Tracking |

### Detailed Changes

#### 1. Human-In-Loop Integration
- **Session 09**: No human intervention capability
- **Session 10**: Interactive fallback for tool failures and plan modifications
- **Impact**: Improved reliability and user control

#### 2. Execution Limits
- **Session 09**: No strict limits, potential for infinite loops
- **Session 10**: Enforced MAX_STEPS=3 and MAX_RETRIES=3
- **Impact**: Prevents resource exhaustion and ensures predictable behavior

#### 3. CSV Logging
- **Session 09**: JSON session logs only
- **Session 10**: Comprehensive CSV logging with performance metrics
- **Impact**: Better analytics and performance tracking

#### 4. Simulator
- **Session 09**: Manual testing only
- **Session 10**: Automated batch testing with 100+ tests
- **Impact**: Scalable testing and performance validation

#### 5. Statistics Generation
- **Session 09**: No automated statistics
- **Session 10**: Automated performance analysis and reporting
- **Impact**: Data-driven insights into system performance

#### 6. Query Management
- **Session 09**: No query tracking
- **Session 10**: Master query table with unique IDs and tracking
- **Impact**: Better query management and analytics

## Architecture Documentation

- **S10_arch.md**: Detailed architecture documentation
- **S10_init_arch01.md**: Mermaid architecture diagrams

## Testing

### Unit Tests
Test individual modules:
```bash
python -m pytest Tests/
```

### Integration Tests
Test agent loop with CSV logging:
```bash
python agent/test.py
```

### Simulator Tests
Run batch testing:
```bash
python simulator/run_simulator.py 10  # Start with 10 tests
```

## Development Notes

- **OLLAMA First**: Development starts with OLLAMA to reduce API costs
- **No Unicode**: Project uses ASCII-only characters
- **Windows 11**: Optimized for PowerShell on Windows 11
- **Sleep Management**: Prevents API rate limiting during batch testing

## License

[Add your license here]

## Author

[Add your name/contact here]

