# API Call Analysis: Ollama vs Google API Usage

## Executive Summary

This analysis examines when Ollama is used vs Google API (Gemini), whether it reduces external API calls, and how API calls are tracked in `tool_performance.csv`.

## 1. When Ollama is Used

### 1.1 MCP Server Tools (mcp_server_2.py)
Ollama is used in the following scenarios:

1. **Document Embeddings** (Line 44-47)
   - Model: `nomic-embed-text`
   - Endpoint: `http://localhost:11434/api/embeddings`
   - Purpose: Generate embeddings for document search/RAG
   - **This replaces Google embedding API calls**

2. **Chunk Relationship Analysis** (Line 64-95)
   - Model: `phi4:latest`
   - Endpoint: `http://localhost:11434/api/chat`
   - Purpose: Determine if document chunks are related
   - **This replaces Google LLM calls for chunk analysis**

3. **Image Captioning** (Line 120-170)
   - Model: `gemma3:12b`
   - Endpoint: `http://localhost:11434/api/generate`
   - Purpose: Generate captions for images
   - **This replaces Google Vision API calls**

### 1.2 Model Manager (agent/model_manager.py)
Ollama can be used for text generation if configured:
- Controlled by `config/profiles.yaml` → `llm.text_generation` setting
- Options: `gemini`, `phi4`, `gemma3:12b`, `qwen2.5:32b-instruct-q4_0`
- If set to Ollama model, uses `http://localhost:11434/api/generate`
- **This replaces Google Gemini API calls for text generation**

## 2. When Google API (Gemini) is Used

### 2.1 Core Agent Components
Google Gemini API is used in:

1. **Perception Module** (`perception/perception.py`)
   - Lines 36-56: `self.client.models.generate_content()`
   - Model: `gemini-2.0-flash`
   - Purpose: Analyze queries and extract entities
   - **Always uses Google API (hardcoded)**

2. **Decision Module** (`decision/decision.py`)
   - Lines 36-39: `self.client.models.generate_content()`
   - Model: `gemini-2.0-flash`
   - Purpose: Generate plans and steps
   - **Always uses Google API (hardcoded)**

### 2.2 Current Configuration
- `config/profiles.yaml` line 24: `text_generation: gemini`
- This means core agent logic (Perception/Decision) uses Google API
- MCP tools can use Ollama independently

## 3. Does Ollama Reduce External API Calls?

### 3.1 YES - In MCP Tools Context

**Ollama reduces external API calls for:**
1. **Embeddings**: Instead of Google `models/embedding-001` API
   - Savings: ~1 API call per document chunk processed
   
2. **Chunk Analysis**: Instead of Google Gemini for chunk relationship
   - Savings: ~1 API call per chunk pair analyzed
   
3. **Image Captioning**: Instead of Google Vision API
   - Savings: ~1 API call per image processed

4. **Text Generation** (if configured): Instead of Google Gemini
   - Savings: Variable, depends on usage

### 3.2 NO - In Core Agent Logic

**Ollama does NOT reduce calls for:**
1. **Perception**: Always uses Google API (hardcoded)
2. **Decision**: Always uses Google API (hardcoded)
3. **These are the most frequent calls** (every query execution)

### 3.3 Potential Savings Calculation

For a typical query execution:
- **Perception**: 1 Google API call (unavoidable)
- **Decision**: 1-3 Google API calls (unavoidable)
- **MCP Tools**: 0-5 Ollama calls (replaces Google calls)

**Net Reduction**: ~30-50% of total API calls if MCP tools are heavily used

## 4. Is API Call Type Recorded in tool_performance.csv?

### 4.1 Current Implementation Status

**YES - Schema Supports It:**
- `tool_performance.csv` has `Api_Call_Type` column (added in Session 11)
- Column definition: Line 34 in `utils/csv_manager.py`
- Parameter: `api_call_type: str` in `log_tool_performance()` method

**NO - Not Currently Populated:**
- Review of `agent/agent_loop2.py` line 213-229: **`api_call_type` parameter is NOT passed**
- Review of `Tests/my_test_100.py` line 434-450: **`api_call_type` parameter is NOT passed**
- Review of `simulator/run_simulator.py`: **`api_call_type` parameter is NOT passed**

### 4.2 What Should Be Recorded

The `Api_Call_Type` column should record:
- `"llm_call"` - For Perception/Decision Google API calls
- `"ollama_embedding"` - For Ollama embedding calls
- `"ollama_chat"` - For Ollama chat/generation calls
- `"ollama_vision"` - For Ollama image captioning
- `"vector_search"` - For FAISS searches
- `"graph_query"` - For knowledge graph queries
- `"tool_execution"` - For MCP tool calls
- `"hybrid_retrieval"` - For combined vector+graph retrieval

### 4.3 Missing Implementation

**Problem**: The V2 agent loop (`agent/agent_loop.py`) does not track API calls or populate `api_call_type`.

**Required Changes**:
1. Track API calls in ContextManager
2. Determine call type based on:
   - Which module made the call (Perception/Decision = "llm_call")
   - Which tool was used (MCP tool = check if Ollama or external)
3. Pass `api_call_type` to `log_tool_performance()`

## 5. Recommendations

### 5.1 Immediate Actions

1. **Add API Call Tracking to V2 Agent Loop**
   - Modify `agent/agent_loop.py` to track API calls
   - Determine call type based on execution path
   - Populate `api_call_type` in CSV logging

2. **Add API Call Tracking to MCP Tools**
   - Modify `mcp_server_2.py` to log when Ollama is used
   - Return API call type metadata with tool results

3. **Update Test Scripts**
   - Modify `Tests/my_test_100.py` to pass `api_call_type`
   - Modify `simulator/run_simulator.py` to pass `api_call_type`

### 5.2 Configuration Options

1. **Make Perception/Decision Configurable**
   - Currently hardcoded to Google API
   - Should respect `config/profiles.yaml` setting
   - Allow Ollama for Perception/Decision if configured

2. **Add API Call Counting**
   - Track total Google API calls per query
   - Track total Ollama calls per query
   - Include in `tool_performance.csv` or separate metrics

### 5.3 Cost Analysis Enhancement

Add columns to `tool_performance.csv`:
- `Google_API_Calls`: Count of Google API calls
- `Ollama_API_Calls`: Count of Ollama API calls
- `Estimated_Cost`: Calculated cost based on call types

## 6. Current State Summary

| Component | API Used | Recorded in CSV? | Reduces External Calls? |
|-----------|----------|------------------|-------------------------|
| Perception | Google (hardcoded) | ❌ No | ❌ No |
| Decision | Google (hardcoded) | ❌ No | ❌ No |
| MCP Embeddings | Ollama | ❌ No | ✅ Yes |
| MCP Chunk Analysis | Ollama | ❌ No | ✅ Yes |
| MCP Image Captioning | Ollama | ❌ No | ✅ Yes |
| MCP Text Gen (if config) | Ollama | ❌ No | ✅ Yes |

## 7. Conclusion

1. **Ollama IS used** for MCP tool operations (embeddings, chunk analysis, image captioning)
2. **Ollama DOES reduce** external API calls for MCP tools (~30-50% reduction potential)
3. **Ollama is NOT used** for core agent logic (Perception/Decision) - these are hardcoded to Google
4. **API calls are NOT currently recorded** in `tool_performance.csv` despite schema support
5. **Implementation needed** to populate `Api_Call_Type` column and track call counts

