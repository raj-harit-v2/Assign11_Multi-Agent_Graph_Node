# Session 10 - Multi-Agent Systems and Distributed AI Coordination

A multi-agent system with human-in-loop capabilities, execution limits, comprehensive logging, and automated testing.

## Overview

This project implements a distributed AI coordination system where multiple agents (Perception, Decision, Action) work together to solve user queries. The system features strict execution limits, human intervention capabilities, and comprehensive performance tracking.

## Key Features

### 🤖 Multi-Agent Architecture
- **Perception Module**: Analyzes queries and extracts entities
- **Decision Module**: Generates adaptive plans using LLM (Gemini 2.0 Flash)
- **Action Module**: Executes tools with retry logic and error handling

### 👤 Human-In-Loop (HIL)
- **Tool Failures**: User provides results when tools fail after max retries
- **Plan Failures**: User modifies/approves plans when execution limits are reached
- **Interactive Recovery**: Seamless intervention at critical failure points

### ⚙️ Execution Control
- **MAX_STEPS = 3**: Maximum steps per query execution
- **MAX_RETRIES = 3**: Maximum retries per tool execution
- **Centralized Management**: `ControlManager` enforces limits system-wide

### 📊 CSV Logging & Analytics
- **tool_performance.csv**: Comprehensive performance tracking with query results
- **query_text.csv**: Master query table with sequential IDs (Bigint)
- **Statistics Generation**: Automated performance analysis and reporting

### 🧪 Automated Testing
- **Batch Simulator**: Run 100+ tests automatically
- **Sleep Management**: Prevents API rate limiting
- **Diagnostic Tests**: 10, 25, and 100 query test suites

### 🔧 Additional Features
- **Query Parser**: Extracts property units (BHK) and currency (Rs/INR)
- **Memory Search**: Historical session retrieval using FAISS
- **Multi-MCP Integration**: Orchestrates multiple tool servers
- **User Plan Storage**: Temporary storage for user-provided plans

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Usage

**Interactive Mode:**
```bash
python main.py
```

**Run Tests:**
```bash
# 10 detailed test cases
python Tests/my_test_10.py

# 100 automated tests
python Tests/my_test_100.py

# Diagnostic test
python Tests/diagnostic_test.py
```

**Generate Statistics:**
```bash
python utils/statistics_generator.py
```

## Project Structure

```
Assign10_Multi-Agent/
├── agent/              # Agent loop and session management
│   ├── agent_loop2.py  # Main agent loop (enhanced)
│   └── agentSession.py # Session state management
├── core/               # Core modules
│   ├── human_in_loop.py      # Human intervention
│   ├── control_manager.py    # Execution limits
│   └── user_plan_storage.py  # User plan storage
├── perception/         # Perception module (query analysis)
├── decision/           # Decision module (planning)
├── action/             # Action module (execution)
├── utils/              # Utilities
│   ├── csv_manager.py        # CSV logging
│   ├── query_parser.py       # Query parsing
│   └── statistics_generator.py
├── simulator/          # Automated testing
├── memory/            # Memory search and logging
├── mcp_servers/       # Multi-MCP tool orchestration
├── data/              # CSV logs (generated)
│   ├── tool_performance.csv
│   └── query_text.csv
└── Tests/             # Test suites and documentation
```

## Architecture

The system follows a **Perception → Decision → Action** flow:

1. **Perception**: Analyzes query, extracts entities, checks if goal can be achieved immediately
2. **Decision**: Generates adaptive plan with tool selection
3. **Action**: Executes tools with retry logic and error handling
4. **Evaluation**: Checks goal achievement, triggers HIL if needed
5. **Logging**: Records all performance metrics to CSV

### Key Components

- **AgentLoop**: Orchestrates the entire execution flow
- **ControlManager**: Enforces MAX_STEPS and MAX_RETRIES
- **CSVManager**: Handles all CSV logging operations
- **MultiMCP**: Manages multiple MCP tool servers
- **UserPlanStorage**: Temporary storage for user interventions

## Testing

- **diagnostic_test.py**: Small diagnostic test (1 case)
- **diagnostic_test_25.py**: 25 cases with 5 query types
- **my_test_10.py**: 10 detailed test cases with execution traces
- **my_test_100.py**: 100 automated tests with CSV logging

## Documentation

- **Architecture**: `Tests/S10_complete_architecture.md`
- **Architecture Comparison**: `Tests/S10_vs_S09_architecture_comparison.md`
- **Breakpoint Guide**: `Tests/BREAKPOINT_QUICK_REF.md`
- **Debugging Guide**: `Tests/DEBUGGING_GUIDE.md`

## Key Improvements from Session 09

| Feature | Session 09 | Session 10 |
|---------|------------|-------------|
| Architecture | Single-Agent Heuristics | Multi-Agent Distributed |
| Human-in-Loop | None | Tool & Plan Failures |
| Execution Limits | Unlimited | MAX_STEPS=3, MAX_RETRIES=3 |
| Logging | JSON only | CSV + Performance Metrics |
| Testing | Manual | Automated 100+ Tests |
| Query Management | None | Master Table with Tracking |

## Environment Variables

- `LLM_PROVIDER`: OLLAMA or GOOGLE (default: OLLAMA)
- `GEMINI_API_KEY`: Google Gemini API key
- `MAX_STEPS`: Maximum steps per query (default: 3)
- `MAX_RETRIES`: Maximum retries per tool (default: 3)

## License

[Add your license here]

## Author

[Add your name/contact here]

