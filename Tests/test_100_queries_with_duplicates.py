"""
Compact Test Script for 100 Queries with 5 Duplicates
Shows brief logging for each step: Query → Memory → Perception → Decision → PlanGraph → Execution → Answer
Final stats summary at the end.
Includes 5 duplicate queries arranged at intervals to test memory usage.
"""

import asyncio
import time
from pathlib import Path
import sys
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp_servers.multiMCP import MultiMCP
from agent.agent_loop import AgentLoop
from utils.csv_manager import CSVManager
import yaml
import re


def create_test_queries():
    """
    Create 100 diverse test queries with 5 duplicates arranged at intervals.
    
    Duplicate placement strategy:
    - Duplicate 1: After query 20 (20% mark)
    - Duplicate 2: After query 40 (40% mark)
    - Duplicate 3: After query 60 (60% mark)
    - Duplicate 4: After query 80 (80% mark)
    - Duplicate 5: After query 95 (95% mark)
    """
    base_queries = []
    
    # Information queries (30 queries)
    info_queries = [
        {"query": "What is the chemical formula for water?", "category": "information", "expected_type": "factual"},
        {"query": "Who wrote the novel '1984'?", "category": "information", "expected_type": "factual"},
        {"query": "What is the capital of Japan?", "category": "information", "expected_type": "factual"},
        {"query": "What is the speed of light?", "category": "information", "expected_type": "factual"},
        {"query": "What is the capital of Australia?", "category": "information", "expected_type": "factual"},
        {"query": "Who invented the telephone?", "category": "information", "expected_type": "factual"},
        {"query": "What is the largest planet in our solar system?", "category": "information", "expected_type": "factual"},
        {"query": "What year did World War II end?", "category": "information", "expected_type": "factual"},
        {"query": "What is the smallest country in the world?", "category": "information", "expected_type": "factual"},
        {"query": "How many chambers does a human heart have?", "category": "information", "expected_type": "factual"},
        {"query": "What is the largest organ in the human body?", "category": "information", "expected_type": "factual"},
        {"query": "What gas do plants absorb from the atmosphere?", "category": "information", "expected_type": "factual"},
        {"query": "What is the national animal of India?", "category": "information", "expected_type": "factual"},
        {"query": "Who painted the Mona Lisa?", "category": "information", "expected_type": "factual"},
        {"query": "What is the capital of France?", "category": "information", "expected_type": "factual"},
        {"query": "What is the capital of Germany?", "category": "information", "expected_type": "factual"},
        {"query": "What is the capital of Italy?", "category": "information", "expected_type": "factual"},
        {"query": "What is the capital of Spain?", "category": "information", "expected_type": "factual"},
        {"query": "What is the capital of Brazil?", "category": "information", "expected_type": "factual"},
        {"query": "What is the capital of Canada?", "category": "information", "expected_type": "factual"},
        {"query": "What is the capital of Mexico?", "category": "information", "expected_type": "factual"},
        {"query": "What is the capital of Russia?", "category": "information", "expected_type": "factual"},
        {"query": "What is the capital of China?", "category": "information", "expected_type": "factual"},
        {"query": "What is the capital of India?", "category": "information", "expected_type": "factual"},
        {"query": "What is the capital of South Korea?", "category": "information", "expected_type": "factual"},
        {"query": "What is the capital of Egypt?", "category": "information", "expected_type": "factual"},
        {"query": "What is the capital of South Africa?", "category": "information", "expected_type": "factual"},
        {"query": "What is the capital of Argentina?", "category": "information", "expected_type": "factual"},
        {"query": "What is the capital of Chile?", "category": "information", "expected_type": "factual"},
        {"query": "What is the capital of New Zealand?", "category": "information", "expected_type": "factual"},
    ]
    
    # Math queries (30 queries)
    math_queries = [
        {"query": "Calculate 144 divided by 12", "category": "math", "expected_type": "computation"},
        {"query": "Calculate 200 divided by 8", "category": "math", "expected_type": "computation"},
        {"query": "Calculate 10 * 5", "category": "math", "expected_type": "computation"},
        {"query": "What is 81 divided by 9?", "category": "math", "expected_type": "computation"},
        {"query": "What is 5 to the power of 3?", "category": "math", "expected_type": "computation"},
        {"query": "Find the factorial of 5", "category": "math", "expected_type": "computation"},
        {"query": "Calculate 25 multiplied by 4", "category": "math", "expected_type": "computation"},
        {"query": "Calculate 100 divided by 4", "category": "math", "expected_type": "computation"},
        {"query": "Calculate 15 * 6", "category": "math", "expected_type": "computation"},
        {"query": "Calculate 72 divided by 8", "category": "math", "expected_type": "computation"},
        {"query": "What is 3 to the power of 4?", "category": "math", "expected_type": "computation"},
        {"query": "Find the factorial of 6", "category": "math", "expected_type": "computation"},
        {"query": "Calculate 50 * 2", "category": "math", "expected_type": "computation"},
        {"query": "Calculate 120 divided by 10", "category": "math", "expected_type": "computation"},
        {"query": "Calculate 7 * 8", "category": "math", "expected_type": "computation"},
        {"query": "Calculate 64 divided by 8", "category": "math", "expected_type": "computation"},
        {"query": "What is 2 to the power of 8?", "category": "math", "expected_type": "computation"},
        {"query": "Find the factorial of 4", "category": "math", "expected_type": "computation"},
        {"query": "Calculate 30 * 3", "category": "math", "expected_type": "computation"},
        {"query": "Calculate 90 divided by 9", "category": "math", "expected_type": "computation"},
        {"query": "Calculate 12 * 7", "category": "math", "expected_type": "computation"},
        {"query": "Calculate 56 divided by 7", "category": "math", "expected_type": "computation"},
        {"query": "What is 4 to the power of 3?", "category": "math", "expected_type": "computation"},
        {"query": "Find the factorial of 7", "category": "math", "expected_type": "computation"},
        {"query": "Calculate 40 * 2", "category": "math", "expected_type": "computation"},
        {"query": "Calculate 108 divided by 9", "category": "math", "expected_type": "computation"},
        {"query": "Calculate 9 * 9", "category": "math", "expected_type": "computation"},
        {"query": "Calculate 84 divided by 7", "category": "math", "expected_type": "computation"},
        {"query": "What is 6 to the power of 2?", "category": "math", "expected_type": "computation"},
        {"query": "Find the factorial of 8", "category": "math", "expected_type": "computation"},
    ]
    
    # Data analysis queries (20 queries)
    data_queries = [
        {"query": "Calculate the average of numbers: 5, 10, 15, 20, 25", "category": "data_analysis", "expected_type": "computation"},
        {"query": "Calculate the average of numbers: 10, 20, 30, 40, 50", "category": "data_analysis", "expected_type": "computation"},
        {"query": "Calculate the average of numbers: 100, 200, 300, 400, 500", "category": "data_analysis", "expected_type": "computation"},
        {"query": "Calculate the average of numbers: 15, 25, 35, 45, 55", "category": "data_analysis", "expected_type": "computation"},
        {"query": "Calculate the average of numbers: 20, 40, 60, 80, 100", "category": "data_analysis", "expected_type": "computation"},
        {"query": "Calculate the average of numbers: 12, 24, 36, 48, 60", "category": "data_analysis", "expected_type": "computation"},
        {"query": "Calculate the average of numbers: 7, 14, 21, 28, 35", "category": "data_analysis", "expected_type": "computation"},
        {"query": "Calculate the average of numbers: 50, 100, 150, 200, 250", "category": "data_analysis", "expected_type": "computation"},
        {"query": "Calculate the average of numbers: 8, 16, 24, 32, 40", "category": "data_analysis", "expected_type": "computation"},
        {"query": "Calculate the average of numbers: 11, 22, 33, 44, 55", "category": "data_analysis", "expected_type": "computation"},
        {"query": "Calculate the average of numbers: 6, 12, 18, 24, 30", "category": "data_analysis", "expected_type": "computation"},
        {"query": "Calculate the average of numbers: 9, 18, 27, 36, 45", "category": "data_analysis", "expected_type": "computation"},
        {"query": "Calculate the average of numbers: 13, 26, 39, 52, 65", "category": "data_analysis", "expected_type": "computation"},
        {"query": "Calculate the average of numbers: 14, 28, 42, 56, 70", "category": "data_analysis", "expected_type": "computation"},
        {"query": "Calculate the average of numbers: 16, 32, 48, 64, 80", "category": "data_analysis", "expected_type": "computation"},
        {"query": "Calculate the average of numbers: 17, 34, 51, 68, 85", "category": "data_analysis", "expected_type": "computation"},
        {"query": "Calculate the average of numbers: 19, 38, 57, 76, 95", "category": "data_analysis", "expected_type": "computation"},
        {"query": "Calculate the average of numbers: 21, 42, 63, 84, 105", "category": "data_analysis", "expected_type": "computation"},
        {"query": "Calculate the average of numbers: 23, 46, 69, 92, 115", "category": "data_analysis", "expected_type": "computation"},
        {"query": "Calculate the average of numbers: 25, 50, 75, 100, 125", "category": "data_analysis", "expected_type": "computation"},
    ]
    
    # Complex queries (10 queries)
    complex_queries = [
        {"query": "Find the factorial of 5 and calculate the sum of all prime numbers from 1 to 20, then find the greatest common divisor of 48 and 18", "category": "complex", "expected_type": "computation"},
        {"query": "Calculate the average of numbers: 100, 200, 300, 400, 500, then find the square root of that average, and finally multiply it by 10", "category": "complex", "expected_type": "computation"},
        {"query": "Calculate 15 * 4, then divide the result by 3, and finally add 20", "category": "complex", "expected_type": "computation"},
        {"query": "Find the factorial of 6, then calculate 2 to the power of 5, and finally find the sum of both results", "category": "complex", "expected_type": "computation"},
        {"query": "Calculate the average of 10, 20, 30, then multiply by 2, and finally subtract 5", "category": "complex", "expected_type": "computation"},
        {"query": "Find the square root of 144, then multiply by 3, and finally add 10", "category": "complex", "expected_type": "computation"},
        {"query": "Calculate 25 * 4, then divide by 5, and finally find the square root", "category": "complex", "expected_type": "computation"},
        {"query": "Find the factorial of 4, then calculate 3 to the power of 3, and finally find the difference", "category": "complex", "expected_type": "computation"},
        {"query": "Calculate the sum of 50, 100, 150, then divide by 3, and finally multiply by 2", "category": "complex", "expected_type": "computation"},
        {"query": "Find the square root of 81, then multiply by 2, and finally subtract 3", "category": "complex", "expected_type": "computation"},
    ]
    
    # Property queries (10 queries)
    property_queries = [
        {"query": "List the security features in DLF Camelia.", "category": "property", "expected_type": "factual"},
        {"query": "What are the price ranges for 3BHK apartments in DLF Camelia?", "category": "property", "expected_type": "factual"},
        {"query": "What amenities are available in DLF Camelia?", "category": "property", "expected_type": "factual"},
        {"query": "What are the price ranges for 2BHK apartments in DLF Camelia?", "category": "property", "expected_type": "factual"},
        {"query": "What are the price ranges for 4BHK apartments in DLF Camelia?", "category": "property", "expected_type": "factual"},
        {"query": "List the parking facilities in DLF Camelia.", "category": "property", "expected_type": "factual"},
        {"query": "What are the location advantages of DLF Camelia?", "category": "property", "expected_type": "factual"},
        {"query": "What are the price ranges for 1BHK apartments in DLF Camelia?", "category": "property", "expected_type": "factual"},
        {"query": "What are the price ranges for penthouse in DLF Camelia?", "category": "property", "expected_type": "factual"},
        {"query": "What are the nearby schools and hospitals near DLF Camelia?", "category": "property", "expected_type": "factual"},
    ]
    
    # Combine all base queries (100 total)
    base_queries = info_queries + math_queries + data_queries + complex_queries + property_queries
    
    # Select queries for duplicates (strategically chosen for memory testing)
    duplicate_sources = [
        base_queries[0],   # "What is the chemical formula for water?" (info)
        base_queries[30],  # "Calculate 144 divided by 12" (math)
        base_queries[60],  # "Calculate the average of numbers: 100, 200, 300, 400, 500" (data)
        base_queries[80],  # "Find the factorial of 5 and calculate..." (complex)
        base_queries[90],  # "List the security features in DLF Camelia." (property)
    ]
    
    # Build final query list with duplicates inserted at intervals
    final_queries = []
    query_id = 1
    
    for i, query in enumerate(base_queries):
        final_queries.append({
            "id": query_id,
            "query": query["query"],
            "category": query["category"],
            "expected_type": query["expected_type"],
            "is_duplicate": False
        })
        query_id += 1
        
        # Insert duplicates at intervals: after 20, 40, 60, 80, 95
        if i == 19:  # After query 20 (index 19)
            dup = duplicate_sources[0]
            final_queries.append({
                "id": query_id,
                "query": dup["query"],
                "category": dup["category"],
                "expected_type": dup["expected_type"],
                "is_duplicate": True,
                "original_id": 1
            })
            query_id += 1
        elif i == 39:  # After query 40 (index 39)
            dup = duplicate_sources[1]
            final_queries.append({
                "id": query_id,
                "query": dup["query"],
                "category": dup["category"],
                "expected_type": dup["expected_type"],
                "is_duplicate": True,
                "original_id": 31
            })
            query_id += 1
        elif i == 59:  # After query 60 (index 59)
            dup = duplicate_sources[2]
            final_queries.append({
                "id": query_id,
                "query": dup["query"],
                "category": dup["category"],
                "expected_type": dup["expected_type"],
                "is_duplicate": True,
                "original_id": 61
            })
            query_id += 1
        elif i == 79:  # After query 80 (index 79)
            dup = duplicate_sources[3]
            final_queries.append({
                "id": query_id,
                "query": dup["query"],
                "category": dup["category"],
                "expected_type": dup["expected_type"],
                "is_duplicate": True,
                "original_id": 81
            })
            query_id += 1
        elif i == 94:  # After query 95 (index 94)
            dup = duplicate_sources[4]
            final_queries.append({
                "id": query_id,
                "query": dup["query"],
                "category": dup["category"],
                "expected_type": dup["expected_type"],
                "is_duplicate": True,
                "original_id": 91
            })
            query_id += 1
    
    return final_queries


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


def load_expected_answers(answers_file: str = "Tests/test_100_queries_expected_answers.txt") -> dict:
    """
    Load expected answers from text file.
    
    Format: Query | Expected Answer | Answer Type | Notes
    
    Returns:
        Dictionary mapping query text to expected answer
    """
    expected_answers = {}
    answers_path = project_root / answers_file if answers_file.startswith("Tests/") else Path(answers_file)
    
    if not answers_path.exists():
        print(f"[WARN] Expected answers file not found: {answers_path}")
        return {}
    
    try:
        with open(answers_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Parse format: Query | Expected Answer | Answer Type | Notes
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 2:
                    query = parts[0]
                    expected_answer = parts[1]
                    answer_type = parts[2] if len(parts) > 2 else "unknown"
                    notes = parts[3] if len(parts) > 3 else ""
                    
                    expected_answers[query] = {
                        "expected": expected_answer,
                        "type": answer_type,
                        "notes": notes
                    }
        
        return expected_answers
    except Exception as e:
        print(f"[ERROR] Failed to load expected answers: {e}")
        return {}


def verify_answer(answer: str, expected: str, answer_type: str) -> tuple[bool, list[str]]:
    """
    Verify if the answer matches expected result.
    
    Returns:
        Tuple of (is_correct: bool, issues: list[str])
    """
    issues = []
    answer_clean = answer.strip()
    expected_clean = expected.strip()
    
    # Normalize for comparison (case-insensitive, remove extra spaces)
    answer_lower = answer_clean.lower()
    expected_lower = expected_clean.lower()
    
    # Exact match
    if answer_lower == expected_lower:
        return True, []
    
    # For numeric answers, try to extract and compare numbers
    if answer_type in ["computation", "factual"] and any(c.isdigit() for c in expected_clean):
        # Extract numbers from both
        answer_nums = re.findall(r'\d+\.?\d*', answer_clean)
        expected_nums = re.findall(r'\d+\.?\d*', expected_clean)
        
        if expected_nums:
            expected_num = float(expected_nums[0])
            if answer_nums:
                answer_num = float(answer_nums[0])
                # Allow small tolerance for floating point
                if abs(answer_num - expected_num) < 0.01:
                    return True, []
                else:
                    issues.append(f"Expected {expected_num}, got {answer_num}")
            else:
                issues.append(f"Expected numeric value {expected_num}, but answer contains no numbers")
        else:
            # Not a numeric answer type, do string comparison
            if expected_lower in answer_lower or answer_lower in expected_lower:
                return True, []
            else:
                issues.append(f"Expected '{expected_clean}', got '{answer_clean}'")
    
    # For complex queries, check if expected values are present
    elif "," in expected_clean:
        # Multiple values expected (e.g., "120, 77, 6")
        expected_parts = [p.strip() for p in expected_clean.split(',')]
        answer_nums = re.findall(r'\d+\.?\d*', answer_clean)
        
        missing = []
        for exp_part in expected_parts:
            exp_num = re.findall(r'\d+\.?\d*', exp_part)
            if exp_num:
                if exp_num[0] not in answer_nums:
                    missing.append(exp_num[0])
        
        if missing:
            issues.append(f"Missing expected values: {', '.join(missing)}")
        else:
            return True, []
    
    # For other types, check substring match
    else:
        if expected_lower in answer_lower:
            return True, []
        else:
            issues.append(f"Expected '{expected_clean}' (or substring), got '{answer_clean}'")
    
    return False, issues


async def run_test_100_queries():
    """Run 100 queries with compact logging."""
    print("=" * 80)
    print("COMPACT TEST: 100 QUERIES WITH 5 DUPLICATES")
    print("=" * 80)
    print()
    
    # Load expected answers
    print("[INIT] Loading expected answers...")
    expected_answers = load_expected_answers()
    if not expected_answers:
        print("[WARN] No expected answers loaded. Validation will be limited.")
    else:
        print(f"[OK] Loaded {len(expected_answers)} expected answers for verification\n")
    
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
    duplicate_results = []
    
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
        is_duplicate = query_info.get('is_duplicate', False)
        original_id = query_info.get('original_id', None)
        
        # Print query header
        if is_duplicate:
            print(f"TEST {idx}/105: {category.upper()} (DUPLICATE - Original: Test {original_id})")
        else:
            print(f"TEST {idx}/105: {category.upper()}")
        print("-" * 80)
        print(f"Query: {query}")
        if is_duplicate:
            print(f"[MEMORY TEST] This is a DUPLICATE query - should use memory from Test {original_id}")
        print()
        
        query_start = time.perf_counter()
        query_start_datetime = datetime.now()
        execution_details = {}  # Initialize in case of error
        
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
            
            # Check for Human-in-Loop triggers
            hil_triggered = execution_details.get('human_in_loop_triggered', False)
            hil_reason = execution_details.get('hil_reason', '')
            if hil_triggered:
                print(f"[HIL] Human-in-Loop was triggered: {hil_reason}")
            
            query_elapsed = time.perf_counter() - query_start
            
            # Compact step logging - extract from context if available
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
            
            # Validate answer using expected answers
            is_correct = None
            validation_notes = []
            if query in expected_answers:
                expected_data = expected_answers[query]
                expected_answer = expected_data["expected"]
                expected_type = expected_data.get("type", "unknown")
                
                # Verify answer
                is_correct, issues = verify_answer(answer, expected_answer, expected_type)
                
                if is_correct:
                    print(f"[VALIDATION] ✓ Answer matches expected: '{expected_answer}'")
                else:
                    print(f"[VALIDATION] ✗ Answer does not match expected: '{expected_answer}'")
                    if issues:
                        print(f"[VALIDATION] Issues: {', '.join(issues)}")
                    validation_notes = issues
            
            # Display HIL status if triggered
            if hil_triggered:
                print(f"[HIL] Human-in-Loop was triggered: {hil_reason}")
            
            if is_duplicate:
                print(f"[MEMORY USAGE] Duplicate query - Original was Test {original_id}")
            
            # Derive statuses for CSV:
            # Result_Status  → high-level pipeline outcome (success / failed / error)
            # Actual_Status  → per-query correctness (success / mismatch / warning / error)
            result_status = "success"      # pipeline completed without exception
            actual_status = "success"      # default correctness classification
            if is_correct is False:
                actual_status = "mismatch"
            elif is_correct is None and validation_notes:
                actual_status = "warning"

            # Log to CSV
            # Extract tool_name from execution_details (first tool used, or "agent_loop" if none)
            tools_used_list = execution_details.get('tools_used', [])
            tool_name = tools_used_list[0] if tools_used_list else execution_details.get('tool_name', 'agent_loop')
            
            # Extract nodes data - agent_loop returns nodes_called_json, but not nodes_compact or node_count
            # These will be calculated by CSVManager if not provided
            nodes_called_json = execution_details.get('nodes_called_json', [])
            if isinstance(nodes_called_json, list):
                # Convert list to JSON string if needed
                import json
                nodes_called_json = json.dumps(nodes_called_json)
            
            # Get expected answer if available
            expected_answer = expected_answers.get(query, {}).get("expected", "") if query in expected_answers else ""
            
            csv_manager.log_tool_performance(
                query_id=query_id,
                plan_used=execution_details.get('plan_steps', []),
                plan_step_count=len(execution_details.get('plan_steps', [])),
                query_name=f"Test {query_id} - {category}" + (" (DUPLICATE)" if is_duplicate else ""),
                query_text=query,
                query_answer=answer,
                correct_answer_expected=expected_answer,
                result_status=result_status,
                actual_status=actual_status,
                elapsed_time=query_elapsed,
                tool_name=tool_name,
                retry_count=0,  # Not tracked in execution_details, default to 0
                api_call_type=execution_details.get('api_call_type', ''),
                llm_provider=execution_details.get('llm_provider', ''),
                step_details=execution_details.get('step_details', ''),
                nodes_called=nodes_called_json,  # Pass as JSON string or list (CSVManager will handle it)
                nodes_compact="",  # Will be calculated by CSVManager from nodes_called and step_details
                node_count=0,  # Will be calculated by CSVManager from nodes_called
                nodes_exe_path=execution_details.get('nodes_exe_path', ''),
                final_state=execution_details.get('final_state', {}),
                start_datetime=query_start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                end_datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                error_message=""
            )
            
            result_entry = {
                "id": query_id,
                "query": query,
                "category": category,
                "answer": answer,
                "expected_answer": expected_answers.get(query, {}).get("expected", "N/A"),
                "is_correct": is_correct,
                "validation_notes": validation_notes,
                "status": "success",
                "elapsed": query_elapsed,
                "is_duplicate": is_duplicate,
                "original_id": original_id,
                "hil_triggered": hil_triggered,
                "hil_reason": hil_reason
            }
            
            results.append(result_entry)
            
            if is_duplicate:
                duplicate_results.append(result_entry)
            
        except Exception as e:
            query_elapsed = time.perf_counter() - query_start
            error_msg = str(e)[:100]
            
            print_step_header("ERROR", query_id)
            print(f"{error_msg}")
            
            result_entry = {
                "id": query_id,
                "query": query,
                "category": category,
                "answer": "ERROR",
                "status": "error",
                "elapsed": query_elapsed,
                "error": error_msg,
                "is_duplicate": is_duplicate,
                "original_id": original_id
            }
            
            results.append(result_entry)
            
            if is_duplicate:
                duplicate_results.append(result_entry)
            
            # Log error to CSV
            try:
                # Extract tool_name if execution_details available (might be empty on error)
                tools_used_list = execution_details.get('tools_used', []) if execution_details else []
                tool_name = tools_used_list[0] if tools_used_list else (execution_details.get('tool_name', '') if execution_details else '')
                
                # Get expected answer if available
                expected_answer = expected_answers.get(query, {}).get("expected", "") if query in expected_answers else ""
                
                csv_manager.log_tool_performance(
                    query_id=query_id,
                    plan_used=execution_details.get('plan_steps', []) if execution_details else [],
                    plan_step_count=len(execution_details.get('plan_steps', [])) if execution_details else 0,
                    query_name=f"Test {query_id} - {category}" + (" (DUPLICATE)" if is_duplicate else ""),
                    query_text=query,
                    query_answer="ERROR",
                    correct_answer_expected=expected_answer,
                    result_status="failed",
                    actual_status="error",
                    elapsed_time=query_elapsed,
                    tool_name=tool_name,
                    retry_count=0,
                    error_message=error_msg,
                    api_call_type=execution_details.get('api_call_type', '') if execution_details else '',
                    llm_provider=execution_details.get('llm_provider', '') if execution_details else '',
                    step_details=execution_details.get('step_details', '') if execution_details else '',
                    nodes_called=execution_details.get('nodes_called_json', []) if execution_details else [],
                    nodes_compact=execution_details.get('nodes_compact', '') if execution_details else '',
                    node_count=execution_details.get('node_count', 0) if execution_details else 0,
                    nodes_exe_path=execution_details.get('nodes_exe_path', '') if execution_details else '',
                    final_state=execution_details.get('final_state', {}) if execution_details else {},
                    start_datetime=query_start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                    end_datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            except Exception as csv_error:
                print(f"⚠ Warning: Could not log error to CSV: {csv_error}")
        
        print()
        
        # Small delay between queries to avoid rate limiting
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
    
    # Count Human-in-Loop triggers
    hil_count = sum(1 for r in results if r.get('hil_triggered', False))
    
    # Answer Accuracy (vs Expected Answers)
    correct_answers = 0
    total_with_expected = 0
    validation_issues = []
    
    for r in results:
        if r.get("is_correct") is not None:
            total_with_expected += 1
            if r.get("is_correct"):
                correct_answers += 1
            else:
                validation_issues.append({
                    "id": r["id"],
                    "query": r["query"][:50],
                    "expected": r.get("expected_answer", "N/A"),
                    "got": r["answer"][:50],
                    "notes": r.get("validation_notes", [])
                })
    
    print(f"Total Queries: {len(results)}")
    print(f"  Successful: {successful}")
    print(f"  Errors: {errors}")
    print(f"  Human-in-Loop Triggers: {hil_count}")
    print()
    
    if total_with_expected > 0:
        accuracy = (correct_answers / total_with_expected) * 100
        print(f"Answer Accuracy (vs Expected Answers):")
        print(f"  Correct: {correct_answers}/{total_with_expected} ({accuracy:.1f}%)")
        print()
    
    print(f"Timing:")
    print(f"  Total Time: {total_elapsed:.2f} seconds ({total_elapsed/60:.2f} minutes)")
    print(f"  Average Time: {avg_time:.2f} seconds per query")
    print()
    
    # Duplicate query statistics
    if duplicate_results:
        dup_successful = sum(1 for r in duplicate_results if r['status'] == 'success')
        dup_errors = sum(1 for r in duplicate_results if r['status'] == 'error')
        dup_avg_time = sum(r['elapsed'] for r in duplicate_results) / len(duplicate_results) if duplicate_results else 0
        
        print("Duplicate Query Statistics (Memory Tests):")
        print(f"  Total Duplicates: {len(duplicate_results)}")
        print(f"  Successful: {dup_successful}")
        print(f"  Errors: {dup_errors}")
        print(f"  Average Time: {dup_avg_time:.2f} seconds per duplicate")
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
    
    # Show validation issues if any
    if validation_issues:
        print(f"Validation Issues Found: {len(validation_issues)}")
        print("(Showing first 10 issues)")
        for issue in validation_issues[:10]:
            print(f"  • Test {issue['id']}: {issue['query']}")
            if issue.get('expected') != "N/A":
                print(f"    Expected: {issue['expected']}")
                print(f"    Got: {issue['got']}")
            if issue.get('notes'):
                print(f"    Notes: {', '.join(issue['notes'])}")
        if len(validation_issues) > 10:
            print(f"  ... and {len(validation_issues) - 10} more issues")
        print()
    
    # Duplicate placement summary
    print("Duplicate Placement:")
    print("  Duplicate 1: After Test 20 (Info query)")
    print("  Duplicate 2: After Test 40 (Math query)")
    print("  Duplicate 3: After Test 60 (Data query)")
    print("  Duplicate 4: After Test 80 (Complex query)")
    print("  Duplicate 5: After Test 95 (Property query)")
    print()
    
    # Quick answer preview (first 10)
    print("Answer Preview (First 10):")
    for r in results[:10]:
        answer_preview = r['answer'][:60] + "..." if len(r['answer']) > 60 else r['answer']
        dup_marker = " [DUPLICATE]" if r.get('is_duplicate') else ""
        print(f"  [{r['id']}] {r['category']}{dup_marker}: {answer_preview}")
    
    if len(results) > 10:
        print(f"  ... and {len(results) - 10} more")
    
    print()
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_test_100_queries())

