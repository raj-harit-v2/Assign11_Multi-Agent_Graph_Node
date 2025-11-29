"""
Simulator for Session 10
Runs 100+ tests with sleep management and CSV logging.
"""

import asyncio
import yaml
from pathlib import Path
from mcp_servers.multiMCP import MultiMCP
from agent.agent_loop import AgentLoop
from simulator.sleep_manager import sleep_after_test, sleep_after_batch
from utils.csv_manager import CSVManager


async def load_queries(query_source: str = "Tests/sample_queries.txt") -> list:
    """
    Load queries from file or CSV.
    
    Args:
        query_source: Path to query file (one query per line)
    
    Returns:
        list: List of query strings
    """
    queries = []
    
    if Path(query_source).exists():
        with open(query_source, 'r', encoding='utf-8') as f:
            queries = [line.strip() for line in f if line.strip()]
    else:
        # Fallback: generate sample queries
        queries = [
            "What is 2 + 2?",
            "Calculate 10 * 5",
            "What is the capital of France?",
            "Find the square root of 16",
            "What is 100 divided by 4?"
        ]
    
    return queries


async def run_simulator(num_tests: int = 100, query_source: str = "Tests/sample_queries.txt"):
    """
    Run simulator for specified number of tests.
    
    Args:
        num_tests: Number of tests to run (default: 100)
        query_source: Path to query file
    """
    print("=" * 60)
    print("SESSION 10 SIMULATOR")
    print("=" * 60)
    print(f"Running {num_tests} tests...")
    print(f"Query source: {query_source}")
    print("=" * 60)
    
    # Load queries
    all_queries = await load_queries(query_source)
    
    if not all_queries:
        print("ERROR: No queries found. Please create Tests/sample_queries.txt")
        return
    
    # Repeat queries if needed to reach num_tests
    queries = (all_queries * ((num_tests // len(all_queries)) + 1))[:num_tests]
    
    # Initialize MCP and Agent
    print("\nInitializing MCP Servers...")
    with open("config/mcp_server_config.yaml", "r") as f:
        profile = yaml.safe_load(f)
        mcp_servers_list = profile.get("mcp_servers", [])
        configs = list(mcp_servers_list)
    
    multi_mcp = MultiMCP(server_configs=configs)
    await multi_mcp.initialize()
    
    loop = AgentLoop(
        perception_prompt_path="prompts/perception_prompt.txt",
        decision_prompt_path="prompts/decision_prompt.txt",
        multi_mcp=multi_mcp,
        strategy="exploratory"
    )
    
    csv_manager = CSVManager()
    
    # Run tests
    success_count = 0
    failure_count = 0
    
    for test_id in range(1, num_tests + 1):
        query = queries[test_id - 1]
        
        print(f"\n{'=' * 60}")
        print(f"TEST {test_id}/{num_tests}")
        print(f"{'=' * 60}")
        print(f"Query: {query}")
        
        try:
            # Run agent with query_name
            query_name = f"Test Query {test_id}"
            session = await loop.run(query, test_id=test_id, query_name=query_name)
            
            # Check result
            if session.state.get("original_goal_achieved", False):
                success_count += 1
                print(f"\n[OK] Test {test_id} SUCCESS")
            else:
                failure_count += 1
                print(f"\n[FAIL] Test {test_id} FAILED")
            
            # Sleep after test (except last one)
            if test_id < num_tests:
                sleep_time = await sleep_after_test()
                print(f"Sleeping {sleep_time:.2f} seconds...")
            
            # Longer sleep after every 10 tests
            if test_id % 10 == 0 and test_id < num_tests:
                batch_sleep = await sleep_after_batch()
                print(f"Batch sleep: {batch_sleep:.2f} seconds...")
        
        except Exception as e:
            failure_count += 1
            print(f"\n[FAIL] Test {test_id} ERROR: {e}")
            # Still log to CSV with error
            from utils.time_utils import get_current_datetime
            error_start_datetime = get_current_datetime()
            error_end_datetime = get_current_datetime()
            
            query_name = f"Test Query {test_id}"
            query_id = csv_manager.add_query(query_text=query, query_name=query_name)
            csv_manager.log_tool_performance(
                test_id=test_id,
                query_id=query_id,
                query_name=query_name,
                query_text=query,
                query_answer="",
                plan_used=[],
                result_status="failed",
                actual_status="error",
                start_datetime=error_start_datetime,
                end_datetime=error_end_datetime,
                elapsed_time="0",
                plan_step_count=0,
                tool_name="",
                retry_count=0,
                error_message=str(e),
                final_state={}
            )
    
    # Final summary
    print(f"\n{'=' * 60}")
    print("SIMULATOR COMPLETE")
    print(f"{'=' * 60}")
    print(f"Total tests: {num_tests}")
    print(f"Successes: {success_count}")
    print(f"Failures: {failure_count}")
    print(f"Success rate: {(success_count/num_tests)*100:.2f}%")
    print(f"\nResults logged to: data/tool_performance.csv")
    print(f"Queries logged to: data/query_text.csv")


if __name__ == "__main__":
    import sys
    num_tests = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    query_source = sys.argv[2] if len(sys.argv) > 2 else "Tests/sample_queries.txt"
    asyncio.run(run_simulator(num_tests, query_source))

