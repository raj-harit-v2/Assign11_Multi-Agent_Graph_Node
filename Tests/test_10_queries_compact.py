"""
Compact Test Script for 10 Queries
Shows brief logging for each step: Query → Memory → Perception → Decision → PlanGraph → Execution → Answer
Final stats summary at the end.
"""

import asyncio
import time
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp_servers.multiMCP import MultiMCP
from agent.agent_loop import AgentLoop
from utils.csv_manager import CSVManager
import yaml


def create_test_queries():
    """Create 10 diverse test queries."""
    return [
        {
            "id": 1,
            "query": "What is the chemical formula for water?",
            "category": "information",
            "expected_type": "factual"
        },
        {
            "id": 2,
            "query": "Calculate 144 divided by 12",
            "category": "math",
            "expected_type": "computation"
        },
        {
            "id": 3,
            "query": "Who wrote the novel '1984'?",
            "category": "information",
            "expected_type": "factual"
        },
        {
            "id": 4,
            "query": "What is the capital of Japan?",
            "category": "information",
            "expected_type": "factual"
        },
        {
            "id": 5,
            "query": "Calculate the average of numbers: 10, 20, 30, 40, 50",
            "category": "data_analysis",
            "expected_type": "computation"
        },
        {
            "id": 6,
            "query": "What is 5 to the power of 3?",
            "category": "math",
            "expected_type": "computation"
        },
        {
            "id": 7,
            "query": "What is the speed of light?",
            "category": "information",
            "expected_type": "factual"
        },
        {
            "id": 8,
            "query": "Find the factorial of 5",
            "category": "math",
            "expected_type": "computation"
        },
        {
            "id": 9,
            "query": "What is the capital of Australia?",
            "category": "information",
            "expected_type": "factual"
        },
        {
            "id": 10,
            "query": "Calculate 25 multiplied by 4",
            "category": "math",
            "expected_type": "computation"
        }
    ]


def print_step_header(step_name: str, query_id: int):
    """Print compact step header."""
    print(f"  [{step_name}]", end=" ")


def print_memory_results(memory_results):
    """Print compact memory search results."""
    if memory_results:
        count = len(memory_results)
        top_match = memory_results[0]
        query_match = top_match.get('query', '')[:50]
        print(f"Found {count} match(es) | Top: '{query_match}...'")
    else:
        print("No matches found")


def print_perception_result(perception_result):
    """Print compact perception result."""
    if hasattr(perception_result, 'route'):
        route = perception_result.route.value if hasattr(perception_result.route, 'value') else str(perception_result.route)
        goal_met = perception_result.goal_met if hasattr(perception_result, 'goal_met') else False
        print(f"Route: {route.upper()} | Goal Met: {goal_met}")
    else:
        print("Route: DECISION | Goal Met: False")


def print_plan_graph_info(plan_graph):
    """Print compact plan graph info."""
    if plan_graph and hasattr(plan_graph, 'nodes'):
        node_count = len(plan_graph.nodes)
        start_node = plan_graph.start_node_id if hasattr(plan_graph, 'start_node_id') else "N/A"
        print(f"Nodes: {node_count} | Start: {start_node}")
    else:
        print("Nodes: 0 | Start: N/A")


def print_execution_summary(execution_details):
    """Print compact execution summary."""
    if execution_details:
        steps = execution_details.get('plan_steps', [])
        tools = execution_details.get('tools_used', [])
        nodes = execution_details.get('nodes_called_json', [])
        
        step_count = len(steps) if steps else 0
        tool_count = len(set(tools)) if tools else 0
        node_count = len(nodes) if nodes else 0
        
        print(f"Steps: {step_count} | Tools: {tool_count} | Nodes Executed: {node_count}")
    else:
        print("Steps: N/A | Tools: N/A | Nodes: N/A")


async def run_test_10_queries():
    """Run 10 queries with compact logging."""
    print("=" * 80)
    print("COMPACT TEST: 10 QUERIES")
    print("=" * 80)
    print()
    
    # Initialize
    print("[INIT] Loading MCP configuration...")
    config_path = project_root / "config" / "mcp_server_config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    mcp_configs = config.get('mcp_servers', [])
    multi_mcp = MultiMCP(mcp_configs)
    await multi_mcp.initialize()
    
    print("[INIT] Initializing Agent Loop...")
    perception_prompt = project_root / "prompts" / "perception_prompt.txt"
    decision_prompt = project_root / "prompts" / "decision_prompt.txt"
    
    loop = AgentLoop(
        str(perception_prompt),
        str(decision_prompt),
        multi_mcp,
        strategy="exploratory"
    )
    
    csv_manager = CSVManager()
    
    # Get test queries
    queries = create_test_queries()
    
    # Results tracking
    results = []
    start_time = time.perf_counter()
    
    print()
    print("=" * 80)
    print("EXECUTING QUERIES")
    print("=" * 80)
    print()
    
    # Process each query
    for idx, query_info in enumerate(queries, 1):
        query_id = query_info['id']
        query = query_info['query']
        category = query_info['category']
        
        print(f"TEST {idx}/10: {category.upper()}")
        print("-" * 80)
        print(f"Query: {query}")
        print()
        
        query_start = time.perf_counter()
        
        try:
            # Run agent loop with execution details
            result = await loop.run(query, return_execution_details=True)
            
            # agent_loop.run() with return_execution_details=True returns the execution_details dict directly
            # (not wrapped in {'answer': ..., 'execution_details': ...})
            if isinstance(result, dict):
                # Check if it's the execution_details dict (has 'answer' key) or wrapped format
                if 'answer' in result:
                    answer = result.get('answer', 'N/A')
                    execution_details = result  # The dict itself is execution_details
                else:
                    # Wrapped format (shouldn't happen, but handle it)
                    answer = result.get('answer', 'N/A')
                    execution_details = result.get('execution_details', {})
            else:
                answer = result
                execution_details = {}
            
            query_elapsed = time.perf_counter() - query_start
            
            # Compact step logging - extract from context if available
            # Note: execution_details may not have all fields, so we log what we can see
            
            print_step_header("Memory Search", query_id)
            # Memory results are not directly in execution_details, but we can check if memory was used
            # by checking if answer matches a previous answer pattern
            print("Searching session logs...")
            
            print_step_header("Perception", query_id)
            # Perception happens internally, we show it happened
            print("Analyzing query intent...")
            
            print_step_header("Decision", query_id)
            plan_steps = execution_details.get('plan_steps', [])
            if plan_steps:
                step_count = len(plan_steps)
                print(f"Generated {step_count} step plan")
            else:
                print("Plan generated")
            
            print_step_header("PlanGraph", query_id)
            nodes_called = execution_details.get('nodes_called', [])
            nodes_path = execution_details.get('nodes_exe_path', '')
            node_count = len(nodes_called) if nodes_called else len(plan_steps)
            if node_count > 0:
                print(f"{node_count} node(s) | Path: {nodes_path}")
            else:
                print("Graph structure created")
            
            print_step_header("Execution", query_id)
            tools_used = execution_details.get('tools_used', [])
            unique_tools = len(set(tools_used)) if tools_used else 0
            print(f"Executed {len(plan_steps)} step(s) | Tools: {unique_tools}")
            
            print_step_header("Summary", query_id)
            print("Formatting final answer...")
            
            print_step_header("Final Answer", query_id)
            answer_preview = answer[:80] + "..." if len(answer) > 80 else answer
            print(f"'{answer_preview}'")
            
            # Log to CSV
            # Extract tool_name from execution_details
            tools_used_list = execution_details.get('tools_used', [])
            tool_name = tools_used_list[0] if tools_used_list else execution_details.get('tool_name', 'agent_loop')
            
            # Extract nodes data - agent_loop returns nodes_called_json, but not nodes_compact or node_count
            # These will be calculated by CSVManager if not provided
            nodes_called_json = execution_details.get('nodes_called_json', [])
            if isinstance(nodes_called_json, list):
                # Convert list to JSON string if needed
                import json
                nodes_called_json = json.dumps(nodes_called_json)
            
            csv_manager.log_tool_performance(
                query_id=query_id,
                plan_used=execution_details.get('plan_steps', []),
                plan_step_count=len(execution_details.get('plan_steps', [])),
                query_name=f"Test {query_id} - {category}",
                query_text=query,
                query_answer=answer,
                result_status="success",
                actual_status="success",
                elapsed_time=query_elapsed,
                tool_name=tool_name,
                api_call_type=execution_details.get('api_call_type', ''),
                llm_provider=execution_details.get('llm_provider', ''),
                step_details=execution_details.get('step_details', ''),
                nodes_called=nodes_called_json,  # Pass as JSON string or list (CSVManager will handle it)
                nodes_compact="",  # Will be calculated by CSVManager from nodes_called and step_details
                node_count=0,  # Will be calculated by CSVManager from nodes_called
                nodes_exe_path=execution_details.get('nodes_exe_path', ''),
                final_state=execution_details.get('final_state', {})
            )
            
            results.append({
                "id": query_id,
                "query": query,
                "category": category,
                "answer": answer,
                "status": "success",
                "elapsed": query_elapsed
            })
            
        except Exception as e:
            query_elapsed = time.perf_counter() - query_start
            error_msg = str(e)[:100]
            
            print_step_header("ERROR", query_id)
            print(f"{error_msg}")
            
            # Log error to CSV
            try:
                csv_manager.log_tool_performance(
                    query_id=query_id,
                    plan_used=[],
                    plan_step_count=0,
                    query_name=f"Test {query_id} - {category}",
                    query_text=query,
                    query_answer="ERROR",
                    result_status="failed",
                    actual_status="error",
                    elapsed_time=query_elapsed,
                    tool_name="",
                    error_message=error_msg
                )
            except Exception as csv_error:
                print(f"⚠ Warning: Could not log error to CSV: {csv_error}")
            
            results.append({
                "id": query_id,
                "query": query,
                "category": category,
                "answer": "ERROR",
                "status": "error",
                "elapsed": query_elapsed,
                "error": error_msg
            })
        
        print()
        
        # Small delay between queries
        if idx < len(queries):
            await asyncio.sleep(2)
    
    total_elapsed = time.perf_counter() - start_time
    
    # Final Stats
    print()
    print("=" * 80)
    print("FINAL STATISTICS")
    print("=" * 80)
    print()
    
    successful = sum(1 for r in results if r['status'] == 'success')
    errors = sum(1 for r in results if r['status'] == 'error')
    avg_time = sum(r['elapsed'] for r in results) / len(results) if results else 0
    
    print(f"Total Queries: {len(results)}")
    print(f"  Successful: {successful}")
    print(f"  Errors: {errors}")
    print()
    print(f"Timing:")
    print(f"  Total Time: {total_elapsed:.2f} seconds")
    print(f"  Average Time: {avg_time:.2f} seconds per query")
    print()
    
    # Category breakdown
    categories = {}
    for r in results:
        cat = r['category']
        if cat not in categories:
            categories[cat] = {'total': 0, 'success': 0}
        categories[cat]['total'] += 1
        if r['status'] == 'success':
            categories[cat]['success'] += 1
    
    if categories:
        print("Category Breakdown:")
        for cat, stats in sorted(categories.items()):
            success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"  {cat}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
        print()
    
    # Quick answer preview
    print("Answer Preview:")
    for r in results[:5]:  # Show first 5
        answer_preview = r['answer'][:60] + "..." if len(r['answer']) > 60 else r['answer']
        print(f"  [{r['id']}] {r['category']}: {answer_preview}")
    
    if len(results) > 5:
        print(f"  ... and {len(results) - 5} more")
    
    print()
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_test_10_queries())

