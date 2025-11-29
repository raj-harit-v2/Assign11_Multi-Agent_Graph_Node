# Assignment 11 - Multi-Agent Graph-Node System

## Overview

Assignment 11 transforms a sequential multi-agent system into a graph-native agent system with DAG-based execution planning. The system represents execution plans as directed acyclic graphs (DAGs), where each node contains multiple code variants (A, B, C) for automatic retry and fallback mechanisms. Enhanced memory search with vector embeddings, session caching, and question word indexing enables intelligent context reuse. DuckDuckGo markdown content extraction provides full web content retrieval, while exponential backoff and Ollama support ensure robust API management. The system tracks node execution paths, variant success rates, and comprehensive execution details in enhanced CSV logging.

> 📊 **Code Comparison Report**: See [S10Share_vs_Assign11_Comparison.md](S10Share_vs_Assign11_Comparison.md) for detailed metrics showing 63.97% code replacement and architectural evolution analysis.

## Key Differences from Assign10_Multi-Agent

### 1. **Architecture Paradigm**

**Assign10:**
- Sequential multi-agent execution
- Linear plan execution (Step 1 → Step 2 → Step 3)
- Single code variant per step
- Static plan structure

**Assign11:**
- **Graph-native execution** with DAG structure
- **Parallel execution paths** via graph edges
- **Multiple code variants** per step (A, B, C variants)
- **Dynamic replanning** with fallback nodes
- **Node-based execution** with parent-child relationships

### 2. **Execution Model**

**Assign10:**
```
Query → Perception → Decision → Action → Result
```

**Assign11:**
```
Query → Memory Search → Perception → Decision → PlanGraph → Node Execution Loop
                                                              ↓
                                                    StepNode (variants A/B/C)
                                                              ↓
                                                    Fallback Nodes (on failure)
                                                              ↓
                                                    Final Answer
```

### 3. **New Core Components**

#### **PlanGraph** (`core/plan_graph.py`)
- Directed acyclic graph (DAG) representing execution plan
- Nodes: `StepNode` objects with multiple `CodeVariant` options
- Edges: Parent-child relationships for execution flow
- Topological sorting for execution order

#### **StepNode** (`core/plan_graph.py`)
- Represents a single execution step in the graph
- Contains multiple `CodeVariant` options (A, B, C)
- Tracks status: `PENDING`, `COMPLETED`, `FAILED`, `SKIPPED`
- Supports fallback nodes on failure

#### **CodeVariant** (`core/plan_graph.py`)
- Multiple code implementations per step (A, B, C)
- Automatic retry mechanism (variant A → B → C)
- Each variant can have different implementations

### 4. **Query Path & Node Execution**

#### **Query Flow:**
```
1. Memory Search
   └─> Load session logs from memory/session_logs/
   └─> Fuzzy matching + Vector embeddings
   └─> Return top_k matches

2. Perception Agent
   └─> Analyze query + memory context
   └─> Determine route (DECISION/SUMMARIZE)
   └─> Check if goal already met

3. Decision Agent
   └─> Build PlanGraph with StepNodes
   └─> Generate CodeVariants (A, B, C) for each step
   └─> Create graph edges (parent-child relationships)
   └─> Set start_node_id and execution order

4. Execution Loop
   └─> While current_node_id exists:
       ├─> Get StepNode
       ├─> Try CodeVariants (A → B → C)
       ├─> Execute code in sandbox
       ├─> Call MCP tools via MultiMCP
       ├─> Store results in ContextManager
       ├─> Perception on step output
       ├─> If goal met → Summarize & Return
       ├─> If failed → Add fallback node
       └─> Select next node (via Decision.select_next_node)

5. Formatter Agent
   └─> Extract concise answer from results
   └─> Context-aware extraction
   └─> Property categorization (BHK, amenities)
```

#### **Node Structure:**
```
PlanGraph
├─ StepNode "0"
│  ├─ CodeVariant "0A": Primary implementation
│  ├─ CodeVariant "0B": Fallback implementation
│  └─ CodeVariant "0C": Last resort implementation
├─ StepNode "1"
│  ├─ CodeVariant "1A"
│  └─ CodeVariant "1B"
└─ StepNode "1F1" (Fallback node for StepNode "1")
   └─ CodeVariant "1F1A"
```

### 5. **Enhanced Features**

#### **Memory System**
- **Session Caching**: 5-minute TTL cache for memory entries
- **Incremental Loading**: Load only last 30 days of sessions
- **Question Word Indexing**: Categorize by "what", "who", "where", "when", "why", "how"
- **Vector Embeddings**: FAISS-based semantic search
- **Memory Prioritization**: Usage-based ranking

#### **Search & Retrieval**
- **DuckDuckGo Markdown Search**: Full content extraction with ASCII spacing normalization
- **Property Parsing**: BHK categorization (1-7BHK, penthouse), amenities extraction
- **Enhanced Answer Extraction**: Context-aware, handles concatenated text, chemical formulas, author names, capital cities, numeric calculations

#### **API Management**
- **Exponential Backoff**: Fixed delay array [6, 10, 18, 60] seconds for 429 rate limit errors
- **Ollama Support**: Local LLM option (configurable via `profiles.yaml`)
- **ModelManager**: Unified LLM interface (Google Gemini + Ollama)

#### **Execution Tracking**
- **Node Execution Trace**: Track which node and variant succeeded
- **CSV Logging**: Enhanced with `Nodes_Called`, `Nodes_Exe_Path`, `Step_Details`, `Node_Count`, `Correct_Answer_Expected`
- **Session Logs**: Structured JSON storage in `memory/session_logs/YYYY/MM/DD/`

## Main Highlights

### ✅ Graph-Native Architecture
- DAG-based execution planning
- Multiple code variants per step
- Dynamic fallback mechanisms
- Parallel execution paths

### ✅ Enhanced Memory System
- Vector embeddings for semantic search
- Session caching for performance
- Question word indexing
- Memory prioritization

### ✅ Robust Execution
- Automatic variant retry (A → B → C)
- Fallback node generation on failure
- Human-in-loop for critical failures
- Comprehensive error handling

### ✅ Advanced Search
- DuckDuckGo markdown content extraction
- Property-specific parsing (BHK, amenities)
- Context-aware answer extraction
- Full content retrieval (not just snippets)

### ✅ Production-Ready Features
- Exponential backoff for API rate limits
- Ollama local LLM support
- Enhanced CSV logging with execution details
- Session persistence for memory reuse

## Project Structure

```
Assign11_Multi-Agent_Graph_Node/
├── agent/
│   ├── agent_loop.py          # Graph-native agent loop
│   └── agentSession.py         # Session data structures
├── core/
│   ├── plan_graph.py           # PlanGraph, StepNode, CodeVariant
│   ├── context_manager.py     # Global context management
│   ├── control_manager.py     # Execution limits
│   └── human_in_loop.py       # Human intervention
├── decision/
│   └── decision.py            # PlanGraph generation
├── perception/
│   └── perception.py           # Query analysis
├── action/
│   └── executor.py             # Code execution with AST transforms
├── memory/
│   ├── memory_search.py        # Enhanced memory search
│   └── session_log.py         # Session persistence
├── retrieval/
│   └── formatter_agent.py      # Answer extraction & formatting
├── mcp_servers/
│   ├── multiMCP.py             # MCP tool orchestration
│   └── mcp_server_3.py         # DuckDuckGo search with markdown
├── utils/
│   ├── model_manager.py        # Unified LLM interface
│   ├── backoff.py              # Exponential backoff utility
│   ├── csv_manager.py          # CSV logging with all columns
│   └── query_parser.py         # Property parsing (BHK, amenities)
├── config/
│   ├── profiles.yaml           # LLM provider selection
│   └── mcp_server_config.yaml  # MCP server configuration
├── Tests/
│   ├── self_diagnostic_10_queries.py           # Self-verification test
│   ├── self_diagnostic_expected_answers.txt    # Expected answers for diagnostic
│   ├── test_100_queries_with_duplicates.py    # 100 queries with duplicates
│   ├── test_100_queries_expected_answers.txt   # Expected answers for 100 queries
│   ├── test_20_queries_with_memory_tracking.py # Memory tracking test
│   ├── test_10_queries_compact.py              # Compact logging test
│   └── Test_sess11.py                          # Interactive test script
├── Arch_Asgn11.mmd             # Architecture diagrams (Mermaid)
├── Arch_Asgn11.drawio          # Architecture diagrams (Draw.io)
├── Arch_Asgn10_Asgn11.mmd      # Comparison diagrams (Mermaid)
├── Arch_Asgn10_Asgn11.drawio   # Comparison diagrams (Draw.io)
├── sess_11_arch.txt            # High-level architecture narrative
└── README_Asgn11_Nodes.md      # This file
```

## Key Files

- **`core/plan_graph.py`**: Graph data structures (PlanGraph, StepNode, CodeVariant)
- **`agent/agent_loop.py`**: Main execution loop with graph traversal
- **`decision/decision.py`**: PlanGraph generation from LLM
- **`action/executor.py`**: Code execution with variant retry
- **`memory/memory_search.py`**: Enhanced memory search with vector embeddings
- **`retrieval/formatter_agent.py`**: Advanced answer extraction with context awareness
- **`utils/backoff.py`**: Exponential backoff for API rate limits
- **`utils/model_manager.py`**: Unified LLM interface (Google/Ollama)

## Testing

- **`Tests/self_diagnostic_10_queries.py`**: Self-verification test with expected answers validation
- **`Tests/test_100_queries_with_duplicates.py`**: 100 queries with 5 duplicates for memory testing
- **`Tests/test_20_queries_with_memory_tracking.py`**: Comprehensive test with memory tracking
- **`Tests/test_10_queries_compact.py`**: Compact logging test with final statistics
- **`Tests/Test_sess11.py`**: Interactive test script for single queries
- Session logs saved to `memory/session_logs/YYYY/MM/DD/`

## Configuration

- **`config/profiles.yaml`**: LLM provider selection (Google/Ollama)
- **`config/mcp_server_config.yaml`**: MCP server configuration
- **`utils/model_manager.py`**: Unified LLM interface with backoff

## Latest Changes & New Files

### New Test Scripts
- **`Tests/self_diagnostic_10_queries.py`**: Self-diagnostic test with answer validation
- **`Tests/test_100_queries_with_duplicates.py`**: 100 queries with duplicate testing
- **`Tests/test_10_queries_compact.py`**: Compact logging format
- **`Tests/Test_sess11.py`**: Interactive query testing

### Expected Answers Files
- **`Tests/self_diagnostic_expected_answers.txt`**: Expected answers for diagnostic test
- **`Tests/test_100_queries_expected_answers.txt`**: Expected answers for 100-query test

### Architecture Documentation
- **`Arch_Asgn11.mmd`**: Mermaid architecture diagrams (conceptual, high-level, detailed)
- **`Arch_Asgn11.drawio`**: Draw.io architecture diagrams
- **`Arch_Asgn10_Asgn11.mmd`**: Comparison diagrams (Mermaid)
- **`Arch_Asgn10_Asgn11.drawio`**: Comparison diagrams (Draw.io)
- **`sess_11_arch.txt`**: High-level architecture narrative with differences from Assign10

### Enhanced Features
- **CSV Column Enhancement**: Added `Correct_Answer_Expected` column to `tool_performance.csv`
- **Answer Extraction Improvements**: Enhanced extraction for chemical formulas, author names, capital cities, numeric calculations, "how many" questions, HTTP full forms
- **Memory Search Fixes**: Corrected session log parsing for new JSON structure
- **ASCII Spacing Normalization**: Normalized markdown content to strict ASCII spacing
- **Execution Details**: Enhanced `agent_loop.run()` to return comprehensive execution details

### Code Optimizations
- Regex pattern compilation for performance
- HTTP connection pooling
- String building optimizations
- Data structure improvements
- Query result caching

---

**Evolution Summary**: Assign10 was a sequential multi-agent system. Assign11 introduces a graph-native architecture with DAG-based execution, multiple code variants, dynamic fallback, enhanced memory/search capabilities, comprehensive testing, and production-ready features.

