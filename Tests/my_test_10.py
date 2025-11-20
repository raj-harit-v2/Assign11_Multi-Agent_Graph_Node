"""
Detailed Test for Session 10 - 10 Test Cases
Shows detailed agent execution like agent/test.py
Uses 5 different query types in random order.
"""

import sys
import random
import asyncio
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 5 Different Query Types
QUERY_TYPES = {
    "mathematical": [
        "What is 2 + 2?",
        "Calculate 10 * 5",
        "Find the square root of 16",
        "What is 100 divided by 4?",
        "Calculate 15 + 27"
    ],
    "property": [
        "Find number of BHK variants available in DLF Camelia from local sources.",
        "What are the price ranges for 3BHK apartments in DLF Camelia?",
        "List all available property types in DLF Camelia project.",
        "Find amenities available in DLF Camelia residential complex.",
        "What is the total number of units in DLF Camelia?"
    ],
    "information": [
        "What is the capital of France?",
        "Who wrote the novel '1984'?",
        "What is the chemical formula for water?",
        "When was the first computer invented?",
        "What is the largest planet in our solar system?"
    ],
    "data_analysis": [
        "Calculate the average of numbers: 10, 20, 30, 40, 50",
        "Find the sum of all even numbers from 1 to 100",
        "What is the factorial of 5?",
        "Calculate the percentage: 25 out of 80",
        "Find the greatest common divisor of 48 and 18"
    ],
    "computation": [
        "What is 3 to the power of 4?",
        "Calculate 144 divided by 12",
        "What is 7 times 8?",
        "Calculate 1000 minus 234",
        "What is the square of 9?"
    ]
}

def generate_test_queries(num_tests: int = 10) -> list:
    """
    Generate test queries using 5 different types in random order.
    
    Args:
        num_tests: Number of test cases to generate (default: 10)
    
    Returns:
        list: List of tuples (test_id, query_type, query_text)
    """
    all_queries = []
    for query_type, queries in QUERY_TYPES.items():
        for query in queries:
            all_queries.append((query_type, query))
    
    # Randomize order
    random.shuffle(all_queries)
    
    # Take first 10 (or repeat if needed)
    test_queries = []
    for i in range(num_tests):
        query_type, query = all_queries[i % len(all_queries)]
        test_queries.append((i + 1, query_type, query))
    
    return test_queries


def print_test_header(test_id: int, query_type: str, query_text: str):
    """Print detailed test header."""
    print("\n" + "=" * 80)
    print(f"TEST {test_id}/10 - [{query_type.upper()}]")
    print("=" * 80)
    print(f"Query: {query_text}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


def print_session_details(session):
    """Print detailed session information like agent/test.py."""
    from agent.agentSession import AgentSession
    from dataclasses import asdict
    import time
    
    print("\n" + "-" * 80)
    print("SESSION DETAILS")
    print("-" * 80)
    print(f"Session ID: {session.session_id}")
    print(f"Original Query: {session.original_query}")
    print(f"Plan Versions: {len(session.plan_versions)}")
    
    # Print initial perception
    if session.perception:
        init_perception = session.perception
        print("\n[Perception 0] Initial ERORLL:")
        print(f"  Entities: {init_perception.entities}")
        print(f"  Result Requirement: {init_perception.result_requirement}")
        print(f"  Original Goal Achieved: {init_perception.original_goal_achieved}")
        print(f"  Reasoning: {init_perception.reasoning}")
        print(f"  Local Goal Achieved: {init_perception.local_goal_achieved}")
        print(f"  Solution Summary: {init_perception.solution_summary}")
        print(f"  Confidence: {init_perception.confidence}")
    
    # Print plan versions and steps
    for i, version in enumerate(session.plan_versions):
        print(f"\n[Decision Plan Text: V{i+1}]:")
        for j, plan_step in enumerate(version["plan_text"]):
            print(f"  Step {j}: {plan_step}")
        
        # Print steps in this plan version
        for step in version["steps"]:
            print(f"\n[Step {step.index}] {step.description}")
            print(f"  Type: {step.type}")
            print(f"  Status: {step.status}")
            
            if step.code:
                print(f"  Tool -> {step.code.tool_name}")
                print(f"  Args -> {step.code.tool_arguments}")
            
            if step.execution_result:
                result_str = str(step.execution_result)
                if len(result_str) > 200:
                    result_str = result_str[:200] + "..."
                print(f"  Execution Result: {result_str}")
            
            if step.conclusion:
                print(f"  Conclusion: {step.conclusion}")
            
            if step.error:
                print(f"  Error: {step.error}")
            
            if step.perception:
                print("  Perception ERORLL:")
                print(f"    Entities: {step.perception.entities}")
                print(f"    Original Goal Achieved: {step.perception.original_goal_achieved}")
                print(f"    Local Goal Achieved: {step.perception.local_goal_achieved}")
                print(f"    Reasoning: {step.perception.reasoning}")
                print(f"    Solution Summary: {step.perception.solution_summary}")
                print(f"    Confidence: {step.perception.confidence}")
            
            if hasattr(step, 'attempts') and step.attempts > 1:
                print(f"  Attempts: {step.attempts}")
            
            if hasattr(step, 'was_replanned') and step.was_replanned:
                print(f"  (Replanned from Step {step.parent_index})")
    
    # Print final session state
    print("\n[Session Final State]:")
    print(f"  Original Goal Achieved: {session.state.get('original_goal_achieved', False)}")
    print(f"  Final Answer: {session.state.get('final_answer', 'N/A')}")
    print(f"  Solution Summary: {session.state.get('solution_summary', 'N/A')}")
    print(f"  Confidence: {session.state.get('confidence', 'N/A')}")
    print(f"  Reasoning Note: {session.state.get('reasoning_note', 'N/A')}")
    
    # Print session snapshot summary
    try:
        snapshot = session.get_snapshot_summary()
        print("\n[Session Snapshot Summary]:")
        print(json.dumps(snapshot, indent=2))
    except Exception as e:
        print(f"\n[Note] Could not generate snapshot: {e}")


async def run_single_test(test_id: int, query_type: str, query_text: str):
    """Run a single test case with detailed output."""
    print_test_header(test_id, query_type, query_text)
    
    try:
        import yaml
        from mcp_servers.multiMCP import MultiMCP
        from agent.agent_loop2 import AgentLoop
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # Initialize MCP Servers
        print("\n[Initializing MCP Servers...]")
        with open("config/mcp_server_config.yaml", "r") as f:
            profile = yaml.safe_load(f)
            mcp_servers_list = profile.get("mcp_servers", [])
            configs = list(mcp_servers_list)
        
        multi_mcp = MultiMCP(server_configs=configs)
        await multi_mcp.initialize()
        print("[OK] MCP Servers initialized")
        
        # Initialize Agent Loop
        print("[Initializing Agent Loop...]")
        agent_loop = AgentLoop(
            perception_prompt_path="prompts/perception_prompt.txt",
            decision_prompt_path="prompts/decision_prompt.txt",
            multi_mcp=multi_mcp,
            strategy="exploratory"
        )
        print("[OK] Agent Loop initialized")
        
        # Run agent
        print("\n[Running Agent...]")
        query_name = f"Test {test_id} - {query_type}"
        session = await agent_loop.run(
            query=query_text,
            test_id=test_id,
            query_name=query_name
        )
        
        # Print detailed session information
        print_session_details(session)
        
        # Print test result
        print("\n" + "-" * 80)
        print("TEST RESULT")
        print("-" * 80)
        if session.state.get("original_goal_achieved", False):
            print("[SUCCESS] Goal achieved")
            print(f"Answer: {session.state.get('final_answer', 'N/A')}")
        else:
            print("[PARTIAL/FAILED] Goal not fully achieved")
            print(f"Reason: {session.state.get('reasoning_note', 'N/A')}")
        
        return session
        
    except Exception as e:
        print(f"\n[ERROR] Test {test_id} failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """Run all 10 test cases."""
    print("\n" + "=" * 80)
    print("SESSION 10 DETAILED TEST - 10 CASES")
    print("=" * 80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # Generate test queries
    test_queries = generate_test_queries(10)
    
    # Print query distribution
    print("\n" + "-" * 80)
    print("QUERY DISTRIBUTION")
    print("-" * 80)
    type_counts = {}
    for test_id, query_type, query_text in test_queries:
        type_counts[query_type] = type_counts.get(query_type, 0) + 1
    
    for qtype, count in sorted(type_counts.items()):
        print(f"  {qtype}: {count} queries")
    
    print("\n" + "-" * 80)
    print("TEST EXECUTION")
    print("-" * 80)
    
    # Run tests
    results = []
    for test_id, query_type, query_text in test_queries:
        session = await run_single_test(test_id, query_type, query_text)
        results.append((test_id, query_type, session))
        
        # Small delay between tests
        if test_id < 10:
            print("\n[Waiting 10 seconds before next test...]")
            await asyncio.sleep(10)
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    success_count = 0
    failed_count = 0
    
    for test_id, query_type, session in results:
        if session and session.state.get("original_goal_achieved", False):
            status = "SUCCESS"
            success_count += 1
        else:
            status = "FAILED/PARTIAL"
            failed_count += 1
        
        print(f"Test {test_id} [{query_type}]: {status}")
    
    print("\n" + "-" * 80)
    print(f"Total: {len(results)} tests")
    print(f"Success: {success_count}")
    print(f"Failed/Partial: {failed_count}")
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

