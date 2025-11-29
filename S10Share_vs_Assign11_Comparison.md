# Code Comparison Report: S10Share vs Assign11

**Generated:** 2025-11-29 00:54:36

## Executive Summary

- **S10Share Commit:** `a8d2db7` (Session 10 baseline)
- **Assign11 Branch:** `main` (Current main)
- **Code Churn:** **362.98%** (total insertions + deletions vs original)
- **Code Growth:** **235.04%** (net additions vs original)
- **Code Modification:** **299.01%** (conservative estimate)
- **Code Replacement:** **63.97%** (original code removed/replaced)
- **Core Code Change:** **63.97%** (core functionality changed)
- **Code Similarity:** **36.03%** (original code that remains)
- **Net Change:** +8,069 lines of code
- **Total Changes:** 12,461 lines (10,265 insertions, 2,196 deletions)

## Change Statistics

| Metric | Value |
|--------|-------|
| **Files Changed** | 63 |
| **Files Added** | 31 |
| **Files Modified** | 21 |
| **Files Deleted** | 11 |
| **Lines Inserted** | 10,265 |
| **Lines Deleted** | 2,196 |
| **Net Change** | +8,069 lines |
| **Original Code Size (S10Share)** | 3,433 lines |
| **Code Churn** | **362.98%** (insertions + deletions) |
| **Code Growth** | **235.04%** (net additions) |
| **Code Modification** | **299.01%** (conservative) |
| **Code Replacement** | **63.97%** (original code removed/replaced) |
| **Core Code Change** | **63.97%** (core functionality changed) |
| **Code Similarity** | **36.03%** (original code that remains) |
| **50% Change Metric** | **63.97%** (replacement rate - key indicator) |
| **Commits Between** | 13 |

## Architectural Evolution

### S10Share (Sequential Multi-Agent)
- Linear execution: Query → Perception → Decision → Action → Result
- Single code variant per step
- Basic memory search (fuzzy matching)
- Simple formatter
- Basic CSV logging

### Assign11 (Graph-Node System)
- DAG-based execution: Query → Memory → Perception → Decision → PlanGraph → Node Execution
- Multiple code variants per step (A, B, C)
- Enhanced memory (FAISS vectors, question word index, caching)
- FormatterAgent with context-aware extraction
- Enhanced CSV logging (Actual_Status, Nodes_Exe_Path, execution tracking)

## Key Files Added

### Core Graph System
- `core/plan_graph.py` - DAG structure (123 lines)
- `core/context_manager.py` - Enhanced context management
- `core/user_plan_storage.py` - Plan storage system

### Retrieval Agents
- `retrieval/formatter_agent.py` - Advanced answer extraction (1,731 lines)
- `retrieval/critic_agent.py` - Answer validation (73 lines)
- `retrieval/graph_agent.py` - Graph-based retrieval (80 lines)
- `retrieval/retriever_agent.py` - Enhanced retrieval (110 lines)
- `retrieval/triplet_agent.py` - Triplet extraction (51 lines)

### Enhanced Utilities
- `utils/generate_result_stats.py` - Statistics generator (314 lines)
- `utils/backoff.py` - Exponential backoff for API errors (277 lines)
- `utils/model_manager.py` - Unified model management (148 lines)
- `utils/query_parser.py` - Query parsing (479 lines)
- `memory/session_manager.py` - Session management (211 lines)

## Key Files Modified

### Major Enhancements
- `agent/agent_loop.py`: 226 → 584 lines (+358 lines) -----> +158.41%
- `decision/decision.py`: 92 → 707 lines (+615 lines) -----> +668.48%
- `action/executor.py`: 162 → 377 lines (+215 lines) -----> +132.72%
- `memory/memory_search.py`: 101 → 372 lines (+271 lines) -----> +268.32%
- `retrieval/formatter_agent.py`: 0 → 1539 lines (+1539 lines) -----> N/A (new file)

## Key Files Deleted

### Replaced Components
- `agent/agent_loop2.py` - Replaced by enhanced agent_loop.py
- `agent/context.py` - Replaced by core/context_manager.py
- `agent/model_manager.py` - Replaced by utils/model_manager.py
- `heuristics/heuristics.py` - Removed (161 lines)

### Old Test Files
- `Tests/S10_arch.md` - Replaced by Arch_Asgn11.md
- `Tests/diagnostic_test.py` - Replaced by new test suites

## Commits Between Versions

13 commits from S10Share to Assign11:

1. 9ff9f22 Remove deleted test files
2. e546873 Add Actual_Status column and align test logging for correctness
3. 2fa0ef5 Update project files and generated statistics
4. 4f0ddb0 Add statistics generator: Generate markdown and CSV statistics from tool_performance.csv
5. a657846 Add submission files
6. ce7aa6f Initial commit: Assign11 Multi-Agent Graph Node System - Complete codebase with all features
7. e01eed2 Fix PowerShell prompt to display C:\Asgn11> and add documentation
8. fd3720b Add Nodes_Exe_Path column to tool_performance.csv and PowerShell prompt customization
9. ad6fd53 Update .gitignore to exclude Excel temp files and backup CSV files
10. 069bff3 Update query_statistics.xlsx and remove temporary Excel lock file
11. 02fb30c Add Query_Id to statistics generator, enhance CSV logging, and update documentation
12. a03ef88 Fix Unicode encoding errors, update Gemini model to 2.0-flash, add my_test_10.py with detailed execution traces, fix AgentSession attribute access, remove .venv directory
13. 43d95ab Update executor and agent_loop2 with retry logic and human-in-loop integration

## Detailed File Changes

### Files Added (31)

**Scripts/**
- `Scripts/clear_all_data.py`

**Submissions/**
- `Submissions/Sess11_Conceptual.png`
- `Submissions/Sess11_Detail.png`
- `Submissions/Sess11_Hlevel.png`

**Tests/**
- `Tests/test_100_queries_expected_answers.txt`
- `Tests/test_100_queries_with_duplicates.py`
- `Tests/test_10_queries_compact.py`

**core/**
- `core/context_manager.py`
- `core/plan_graph.py`
- `core/user_plan_storage.py`

**data/**
- `data/Result_Stats.md`
- `data/query_statistics.csv`
- `data/query_statistics.xlsx`
- `data/tool_performance.xlsx`

**memory/**
- `memory/session_manager.py`

**retrieval/**
- `retrieval/__init__.py`
- `retrieval/critic_agent.py`
- `retrieval/formatter_agent.py`
- `retrieval/graph_agent.py`
- `retrieval/retriever_agent.py`
- `retrieval/triplet_agent.py`

**root/**
- `Arch_Asgn11.md`
- `Arch_Asgn11_DrawIO.mmd`
- `generate_stats.bat`
- `generate_stats.ps1`
- `requirements.txt`

**utils/**
- `utils/backoff.py`
- `utils/generate_result_stats.py`
- `utils/migrate_csv_v2.py`
- `utils/model_manager.py`
- `utils/query_parser.py`

### Files Modified (21)

**action/**
- `action/executor.py`

**agent/**
- `agent/agent_loop.py`

**config/**
- `config/mcp_server_config.yaml`

**core/**
- `core/human_in_loop.py`

**data/**
- `data/query_text.csv`
- `data/tool_performance.csv`

**decision/**
- `decision/decision.py`

**mcp_servers/**
- `mcp_servers/mcp_server_2.py`
- `mcp_servers/mcp_server_3.py`
- `mcp_servers/multiMCP.py`

**memory/**
- `memory/memory_search.py`
- `memory/session_log.py`

**perception/**
- `perception/perception.py`

**prompts/**
- `prompts/decision_prompt.txt`
- `prompts/prompt_check.py`

**root/**
- `.gitignore`
- `README.md`
- `main.py`

**simulator/**
- `simulator/run_simulator.py`

**utils/**
- `utils/csv_manager.py`
- `utils/statistics_generator.py`

### Files Deleted (11)
- `Tests/S10_arch.md`
- `Tests/S10_init_arch01.md`
- `Tests/diagnostic_test.py`
- `Tests/sample_queries.txt`
- `agent/agent_loop2.py`
- `agent/context.py`
- `agent/model_manager.py`
- `agent/test.py`
- `decision/decision_test.py`
- `heuristics/heuristics.py`
- `perception/perception_test.py`

## Conclusion

The codebase has evolved significantly from S10Share to Assign11:

- **299.01% of the original codebase has been modified**
- **63.97% of the original code was replaced/removed** (key change indicator)
- **63.97% core code change** (core functionality transformation)
- **36.03% of original code remains** (code similarity metric)
- **235.04% growth in codebase size** (net additions)
- **362.98% total code churn** (all insertions and deletions)

### 50% Change Analysis

The **Code Replacement** metric (63.97%) indicates that approximately **63.97% of the original S10Share codebase was removed or replaced** during the evolution to Assign11. This represents a significant architectural transformation where:

- Core components were refactored or replaced
- New graph-node architecture replaced sequential execution
- Enhanced memory and retrieval systems replaced basic implementations
- The codebase grew by 235.04% while replacing 63.97% of the original

**Interpretation:** With 63.97% code replacement, this represents a **major architectural evolution** rather than incremental changes. The codebase has been fundamentally transformed from a sequential multi-agent system to a graph-native architecture.
- Architecture transformed from sequential to graph-native
- Enhanced capabilities in memory, retrieval, and execution tracking
- Production-ready features added (exponential backoff, statistics, enhanced logging)

This represents a major architectural evolution while maintaining backward compatibility where possible.

---
*Report generated by generate_comparison_report.py*
