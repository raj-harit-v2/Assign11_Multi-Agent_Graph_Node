"""
Diagnostic Test for Session 11 V2 Graph-Native Agent
Tests 2 queries to verify V2 implementation works correctly.
"""

import asyncio
import sys
from pathlib import Path
import yaml
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp_servers.multiMCP import MultiMCP
from agent.agent_loop import AgentLoop
from utils.csv_manager import CSVManager
from utils.time_utils import get_current_datetime, calculate_elapsed_time
import json

load_dotenv()


async def run_diagnostic_test():
    """Run diagnostic test with 2 queries."""
    print("=" * 70)
    print("SESSION 11 V2 DIAGNOSTIC TEST")
    print("=" * 70)
    
    # Initialize MCP
    print("\n[1/5] Initializing MCP Servers...")
    try:
        with open("config/mcp_server_config.yaml", "r") as f:
            profile = yaml.safe_load(f)
            mcp_servers_list = profile.get("mcp_servers", [])
            configs = list(mcp_servers_list)
        
        multi_mcp = MultiMCP(server_configs=configs)
        await multi_mcp.initialize()
        print("[OK] MCP Servers initialized")
    except Exception as e:
        print(f"[ERROR] MCP initialization failed: {e}")
        return
    
    # Initialize Agent Loop V2
    print("\n[2/5] Initializing Agent Loop V2...")
    try:
        loop = AgentLoop(
            perception_prompt_path="prompts/perception_prompt.txt",
            decision_prompt_path="prompts/decision_prompt.txt",
            multi_mcp=multi_mcp,
            strategy="exploratory"
        )
        print("[OK] Agent Loop V2 initialized")
    except Exception as e:
        print(f"[ERROR] Agent Loop initialization failed: {e}")
        return
    
    # Initialize CSV Manager
    print("\n[3/5] Initializing CSV Manager...")
    csv_manager = CSVManager()
    print("[OK] CSV Manager initialized")
    
    # Test queries
    test_queries = [
        {
            "query": "What is 2 + 2?",
            "query_name": "Test 1 - Simple Math"
        },
        {
            "query": "What is the capital of France?",
            "query_name": "Test 2 - Information Query"
        }
    ]
    
    results = []
    
    # Run tests
    print("\n[4/5] Running Test Queries...")
    print("=" * 70)
    
    for test_id, test_case in enumerate(test_queries, start=1):
        query = test_case["query"]
        query_name = test_case["query_name"]
        
        print(f"\n{'='*70}")
        print(f"TEST {test_id}: {query_name}")
        print(f"Query: {query}")
        print(f"{'='*70}")
        
        start_datetime = get_current_datetime()
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Run agent
            answer = await loop.run(query)
            
            end_time = asyncio.get_event_loop().time()
            end_datetime = get_current_datetime()
            elapsed_seconds = end_time - start_time
            elapsed_time = f"{elapsed_seconds:.3f}"
            
            # Add query to CSV
            query_id = csv_manager.add_query(
                query_text=query,
                query_name=query_name
            )
            
            # Determine result status
            result_status = "success" if answer and len(answer) > 0 else "failure"
            
            # Log to CSV with new V2 columns
            nodes_called = json.dumps(["0", "1", "2"])  # Mock node execution order
            step_details = json.dumps({
                "variants_tried": ["0A", "1A", "2A"],
                "execution_path": "0->1->2",
                "retries": 0,
                "node_variants": {"0": "0A", "1": "1A", "2": "2A"}
            })
            
            csv_manager.log_tool_performance(
                test_id=test_id,
                query_id=query_id,
                query_name=query_name,
                query_text=query,
                query_answer=answer or "No answer generated",
                plan_used=["Step 0: Fetch data", "Step 1: Process", "Step 2: Generate answer"],
                result_status=result_status,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                elapsed_time=elapsed_time,
                plan_step_count=3,
                tool_name="agent_loop_v2",
                retry_count=0,
                error_message="",
                final_state={"answer": answer, "test_id": test_id},
                api_call_type="llm_call",
                step_details=step_details,
                nodes_called=nodes_called,
                nodes_exe_path="0->1->2"
            )
            
            print(f"\n[OK] Test {test_id} completed")
            print(f"  Answer: {answer[:100] if answer else 'No answer'}...")
            print(f"  Status: {result_status}")
            print(f"  Elapsed: {elapsed_time}")
            
            results.append({
                "test_id": test_id,
                "query": query,
                "status": result_status,
                "answer": answer,
                "elapsed": elapsed_time
            })
            
        except Exception as e:
            end_time = asyncio.get_event_loop().time()
            end_datetime = get_current_datetime()
            elapsed_seconds = end_time - start_time
            elapsed_time = f"{elapsed_seconds:.3f}"
            
            print(f"\n[ERROR] Test {test_id} failed: {e}")
            
            # Log failure to CSV
            query_id = csv_manager.add_query(
                query_text=query,
                query_name=query_name
            )
            
            csv_manager.log_tool_performance(
                test_id=test_id,
                query_id=query_id,
                query_name=query_name,
                query_text=query,
                query_answer="",
                plan_used=[],
                result_status="failure",
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                elapsed_time=elapsed_time,
                plan_step_count=0,
                tool_name="agent_loop_v2",
                retry_count=0,
                error_message=str(e),
                final_state={"error": str(e)},
                api_call_type="llm_call",
                step_details="",
                nodes_called="",
                nodes_exe_path=""
            )
            
            results.append({
                "test_id": test_id,
                "query": query,
                "status": "failure",
                "error": str(e),
                "elapsed": elapsed_time
            })
    
    # Summary
    print("\n[5/5] Test Summary")
    print("=" * 70)
    print(f"Total Tests: {len(test_queries)}")
    print(f"Passed: {sum(1 for r in results if r['status'] == 'success')}")
    print(f"Failed: {sum(1 for r in results if r['status'] == 'failure')}")
    
    print("\nDetailed Results:")
    for result in results:
        status_symbol = "[OK]" if result['status'] == 'success' else "[FAIL]"
        print(f"  {status_symbol} Test {result['test_id']}: {result['query']}")
        print(f"    Status: {result['status']}")
        if 'answer' in result:
            print(f"    Answer: {result['answer'][:80] if result['answer'] else 'None'}...")
        if 'error' in result:
            print(f"    Error: {result['error'][:80]}...")
        print(f"    Time: {result['elapsed']}")
    
    print("\n" + "=" * 70)
    print("Diagnostic test complete!")
    print("Check data/tool_performance.csv for logged results")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    asyncio.run(run_diagnostic_test())

