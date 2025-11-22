"""
Detailed Test for Session 10 - 100 Test Cases
Shows detailed agent execution like agent/test.py
Uses 5 different query types in random order.
"""

import sys
import random
import asyncio
import json
import time
import signal
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
        "Calculate 15 + 27",
        "What is 3 * 7?",
        "Calculate 50 - 23",
        "Find the square root of 25",
        "What is 8 * 9?",
        "Calculate 144 / 12",
        "What is 5 to the power of 3?",
        "Calculate 20 * 4",
        "Find the square root of 36",
        "What is 100 - 37?",
        "Calculate 6 * 8",
        "What is 81 divided by 9?",
        "Calculate 12 + 15",
        "Find the square root of 49",
        "What is 7 * 6?",
        "Calculate 200 / 10"
    ],
    "property": [
        "Find number of BHK variants available in DLF Camelia from local sources.",
        "What are the price ranges for 3BHK apartments in DLF Camelia?",
        "List all available property types in DLF Camelia project.",
        "Find amenities available in DLF Camelia residential complex.",
        "What is the total number of units in DLF Camelia?",
        "Find the location details of DLF Camelia project.",
        "What are the payment plans available for DLF Camelia?",
        "List the floor plans for 2BHK units in DLF Camelia.",
        "Find the possession date for DLF Camelia project.",
        "What are the nearby schools near DLF Camelia?",
        "Find the parking facilities in DLF Camelia.",
        "What is the RERA registration number for DLF Camelia?",
        "List the clubhouse facilities in DLF Camelia.",
        "Find the connectivity options near DLF Camelia.",
        "What are the maintenance charges for DLF Camelia?",
        "Find the builder information for DLF Camelia project.",
        "What are the specifications for 3BHK units in DLF Camelia?",
        "List the security features in DLF Camelia.",
        "Find the total project area of DLF Camelia.",
        "What are the nearby hospitals near DLF Camelia?"
    ],
    "information": [
        "What is the capital of France?",
        "Who wrote the novel '1984'?",
        "What is the chemical formula for water?",
        "When was the first computer invented?",
        "What is the largest planet in our solar system?",
        "Who painted the Mona Lisa?",
        "What is the speed of light?",
        "When did World War II end?",
        "What is the smallest planet in our solar system?",
        "Who discovered penicillin?",
        "What is the capital of Japan?",
        "Who wrote 'Romeo and Juliet'?",
        "What is the chemical symbol for gold?",
        "When was the internet invented?",
        "What is the tallest mountain in the world?",
        "Who invented the telephone?",
        "What is the capital of Australia?",
        "Who wrote 'The Great Gatsby'?",
        "What is the chemical formula for carbon dioxide?",
        "When was the first moon landing?"
    ],
    "data_analysis": [
        "Calculate the average of numbers: 10, 20, 30, 40, 50",
        "Find the sum of all even numbers from 1 to 100",
        "What is the factorial of 5?",
        "Calculate the percentage: 25 out of 80",
        "Find the greatest common divisor of 48 and 18",
        "Calculate the average of numbers: 5, 10, 15, 20, 25",
        "Find the sum of all odd numbers from 1 to 50",
        "What is the factorial of 6?",
        "Calculate the percentage: 30 out of 100",
        "Find the least common multiple of 12 and 18",
        "Calculate the average of numbers: 100, 200, 300, 400, 500",
        "Find the sum of all numbers from 1 to 100",
        "What is the factorial of 7?",
        "Calculate the percentage: 45 out of 90",
        "Find the greatest common divisor of 60 and 24",
        "Calculate the average of numbers: 1, 2, 3, 4, 5",
        "Find the sum of all prime numbers from 1 to 20",
        "What is the factorial of 4?",
        "Calculate the percentage: 15 out of 60",
        "Find the least common multiple of 8 and 12"
    ],
    "computation": [
        "What is 3 to the power of 4?",
        "Calculate 144 divided by 12",
        "What is 7 times 8?",
        "Calculate 1000 minus 234",
        "What is the square of 9?",
        "What is 2 to the power of 8?",
        "Calculate 256 divided by 16",
        "What is 9 times 7?",
        "Calculate 500 minus 123",
        "What is the square of 12?",
        "What is 4 to the power of 3?",
        "Calculate 200 divided by 8",
        "What is 6 times 9?",
        "Calculate 1000 minus 567",
        "What is the square of 15?",
        "What is 5 to the power of 2?",
        "Calculate 180 divided by 9",
        "What is 8 times 7?",
        "Calculate 300 minus 89",
        "What is the square of 11?"
    ]
}

def generate_test_queries(num_tests: int = 100) -> list:
    """
    Generate test queries using 5 different types in random order.
    
    Args:
        num_tests: Number of test cases to generate (default: 100)
    
    Returns:
        list: List of tuples (test_id, query_type, query_text)
    """
    all_queries = []
    for query_type, queries in QUERY_TYPES.items():
        for query in queries:
            all_queries.append((query_type, query))
    
    # Randomize order
    random.shuffle(all_queries)
    
    # Take first 100 (or repeat if needed)
    test_queries = []
    for i in range(num_tests):
        query_type, query = all_queries[i % len(all_queries)]
        test_queries.append((i + 1, query_type, query))
    
    return test_queries


def print_test_header(test_id: int, query_type: str, query_text: str, total_tests: int = 100):
    """Print detailed test header."""
    print("\n" + "=" * 80)
    print(f"TEST {test_id}/{total_tests} - [{query_type.upper()}]")
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


async def run_single_test(test_id: int, query_type: str, query_text: str, total_tests: int = 100, csv_manager=None):
    """
    Run a single test case with detailed output and immediate CSV logging.
    
    Args:
        test_id: Test ID number
        query_type: Type of query (mathematical, property, etc.)
        query_text: The query text
        total_tests: Total number of tests (for display)
        csv_manager: CSVManager instance for logging (optional, will create if None)
    
    Returns:
        tuple: (session, logged_to_csv) - session object and whether it was logged
    """
    print_test_header(test_id, query_type, query_text, total_tests)
    
    session = None
    query_id = None
    start_datetime = None
    test_start_time = None
    logged_to_csv = False
    
    try:
        import yaml
        from mcp_servers.multiMCP import MultiMCP
        from agent.agent_loop2 import AgentLoop
        from utils.csv_manager import CSVManager
        from utils.time_utils import get_current_datetime, calculate_elapsed_time
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # Initialize CSV manager if not provided
        if csv_manager is None:
            csv_manager = CSVManager()
        
        # Record start time
        start_datetime = get_current_datetime()
        test_start_time = time.perf_counter()
        
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
        
        # Get query_id from session (it was set during agent_loop.run)
        # We need to get it from the CSV manager or session
        # The agent_loop.run already logs to CSV, but we'll also log here for safety
        # Actually, let's check if it was already logged by checking the CSV
        # For now, we'll log it again here to ensure it's captured
        
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
        
            # Log to CSV immediately after test completes
            # CRITICAL: Ensure ALL 100 tests are logged to CSV
            # agent_loop2.py logs when test_id is not None, but we need backup logging
        try:
            # Check if this test was already logged by agent_loop.run() to avoid duplicates
            existing_records = csv_manager.get_tool_performance()
            already_logged = False
            
            # Check for duplicate: same Test_Id and Query_Text
            for record in existing_records:
                try:
                    record_test_id = int(record.get('Test_Id', 0))
                    record_query_text = record.get('Query_Text', '').strip()
                    # Match on Test_Id and Query_Text to identify duplicates
                    if record_test_id == test_id and record_query_text == query_text.strip():
                        already_logged = True
                        print(f"\n[CSV] Test {test_id} already logged by agent_loop (verified in CSV)")
                        logged_to_csv = True  # Mark as logged even though we didn't log it
                        break
                except Exception as check_error:
                    # If error checking, continue to next record
                    continue
            
            # Always log if not already logged - this ensures all 100 tests are captured
            # This is critical: if agent_loop didn't log (due to error), we must log here
            if not already_logged:
                print(f"\n[CSV] Test {test_id} NOT found in CSV - logging now (agent_loop may not have logged it)")
                end_datetime = get_current_datetime()
                # Use test_start_time (from time.perf_counter()) for elapsed calculation
                test_end_time = time.perf_counter()
                elapsed_time = calculate_elapsed_time(test_start_time, test_end_time)
                
                # Get plan used
                plan_used = []
                if session.plan_versions:
                    plan_used = session.plan_versions[-1].get("plan_text", [])
                
                # Get result status (same logic as agent_loop2.py)
                original_goal_achieved = session.state.get("original_goal_achieved", False)
                final_answer_check = session.state.get("final_answer") or session.state.get("solution_summary") or ""
                
                # If final answer indicates we're concluding due to failure, mark as failure
                is_conclusion_due_to_failure = (
                    "conclude with current results" in final_answer_check.lower() or
                    ("conclude" in final_answer_check.lower() and "current results" in final_answer_check.lower())
                )
                
                # Result is success only if goal was achieved AND we're not concluding due to failure
                if original_goal_achieved and not is_conclusion_due_to_failure:
                    result_status = "success"
                else:
                    result_status = "failure"
                
                # Get query answer
                query_answer = session.state.get("final_answer") or session.state.get("solution_summary") or ""
                
                # Get tool name and retry count from steps
                tool_name = ""
                retry_count = 0
                if session.plan_versions:
                    for step in session.plan_versions[-1].get("steps", []):
                        if step.code:
                            tool_name = step.code.tool_name
                        if hasattr(step, 'execution_result') and step.execution_result:
                            exec_result = step.execution_result
                            if isinstance(exec_result, dict):
                                retry_count = max(retry_count, exec_result.get("retry_count", 0))
                
                # Get error message
                error_message = session.state.get("reasoning_note", "") if result_status == "failure" else ""
                
                # Get query_id - we need to find it from query_text.csv or generate it
                # Check if query already exists
                all_queries = csv_manager.get_all_queries()
                query_id = None
                for q in all_queries:
                    if q.get('Query_Text', '').strip() == query_text.strip() and q.get('Query_Name', '') == query_name:
                        try:
                            query_id = int(q.get('Query_Id', 0))
                            break
                        except:
                            pass
                
                # If not found, add it
                if query_id is None:
                    query_id = csv_manager.add_query(query_text=query_text, query_name=query_name)
                
                # Log to CSV (backup logging in case agent_loop didn't log it)
                csv_manager.log_tool_performance(
                    test_id=test_id,
                    query_id=query_id,
                    query_name=query_name,
                    query_text=query_text,
                    query_answer=query_answer,
                    plan_used=plan_used,
                    result_status=result_status,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    elapsed_time=elapsed_time,
                    plan_step_count=len(plan_used),
                    tool_name=tool_name,
                    retry_count=retry_count,
                    error_message=error_message,
                    final_state=session.state
                )
                
                logged_to_csv = True
                print(f"\n[CSV LOGGED] Test {test_id} logged to tool_performance.csv")
            else:
                # Already logged by agent_loop, but verify it's in CSV
                logged_to_csv = True  # Mark as logged since agent_loop logged it
                print(f"\n[CSV] Test {test_id} already logged by agent_loop - verified in CSV")
            
        except Exception as csv_error:
            print(f"\n[WARNING] Failed to log Test {test_id} to CSV: {csv_error}")
            import traceback
            traceback.print_exc()
            # Try to log anyway as a last resort
            try:
                end_datetime = get_current_datetime()
                test_end_time = time.perf_counter() if test_start_time else None
                elapsed_time = calculate_elapsed_time(test_start_time, test_end_time) if test_start_time and test_end_time else "0.000"
                
                # Get minimal data for error log
                query_id = csv_manager.add_query(query_text=query_text, query_name=query_name) if session else 0
                csv_manager.log_tool_performance(
                    test_id=test_id,
                    query_id=query_id,
                    query_name=query_name,
                    query_text=query_text,
                    query_answer="Error during test execution",
                    plan_used=[],
                    result_status="failure",
                    start_datetime=start_datetime or get_current_datetime(),
                    end_datetime=end_datetime,
                    elapsed_time=elapsed_time,
                    plan_step_count=0,
                    tool_name="",
                    retry_count=0,
                    error_message=f"CSV logging error: {csv_error}",
                    final_state={"error": str(csv_error)}
                )
                logged_to_csv = True
                print(f"\n[CSV LOGGED] Test {test_id} error case logged to tool_performance.csv")
            except:
                print(f"\n[CRITICAL] Could not log Test {test_id} even with error handler")
        
        return session, logged_to_csv
        
    except Exception as e:
        print(f"\n[ERROR] Test {test_id} failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Try to log the failure to CSV even if test crashed
        try:
            if csv_manager is None:
                from utils.csv_manager import CSVManager
                csv_manager = CSVManager()
            
            end_datetime = get_current_datetime() if start_datetime else get_current_datetime()
            # Use time.perf_counter() for elapsed time calculation, not datetime strings
            # If test_start_time is not available, use 0.000
            if test_start_time is not None:
                test_end_time = time.perf_counter()
                elapsed_time = calculate_elapsed_time(test_start_time, test_end_time)
            else:
                elapsed_time = "0.000"
            
            query_name = f"Test {test_id} - {query_type}"
            
            # Get or create query_id
            all_queries = csv_manager.get_all_queries()
            query_id = None
            for q in all_queries:
                if q.get('Query_Text', '').strip() == query_text.strip():
                    try:
                        query_id = int(q.get('Query_Id', 0))
                        break
                    except:
                        pass
            
            if query_id is None:
                query_id = csv_manager.add_query(query_text=query_text, query_name=query_name)
            
            csv_manager.log_tool_performance(
                test_id=test_id,
                query_id=query_id,
                query_name=query_name,
                query_text=query_text,
                query_answer="",
                plan_used=[],
                result_status="error",
                start_datetime=start_datetime or end_datetime,
                end_datetime=end_datetime,
                elapsed_time=elapsed_time,
                plan_step_count=0,
                tool_name="",
                retry_count=0,
                error_message=str(e),
                final_state={"error": str(e), "traceback": traceback.format_exc()}
            )
            logged_to_csv = True
            print(f"\n[CSV LOGGED] Test {test_id} failure logged to tool_performance.csv")
        except Exception as csv_error2:
            print(f"\n[CRITICAL] Failed to log error to CSV: {csv_error2}")
        
        return None, logged_to_csv


# Global flag for graceful shutdown
interrupted = False

def signal_handler(signum, frame):
    """Handle interruption signals (Ctrl+C)."""
    global interrupted
    interrupted = True
    print("\n\n[INTERRUPTED] Received interrupt signal. Finishing current test and saving progress...")
    print("[NOTE] All completed tests have been logged to CSV.")

async def main():
    """Run all 100 test cases with immediate CSV logging and interruption handling."""
    global interrupted
    
    # Set up signal handlers for graceful shutdown (Windows compatible)
    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    except AttributeError:
        # Windows doesn't support SIGTERM
        try:
            signal.signal(signal.SIGINT, signal_handler)
        except:
            pass
    
    print("\n" + "=" * 80)
    print("SESSION 10 DETAILED TEST - 100 CASES")
    print("=" * 80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n[IMPORTANT] Each test is logged to CSV immediately upon completion.")
    print("[IMPORTANT] If interrupted, all completed tests will be preserved in tool_performance.csv")
    print("=" * 80)
    
    # Initialize CSV manager once for all tests
    from utils.csv_manager import CSVManager
    csv_manager = CSVManager()
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # Generate test queries
    test_queries = generate_test_queries(100)
    
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
    print("Note: This will run 100 tests with 10-second delays between tests.")
    print("Total estimated time: ~16-17 minutes (plus execution time)")
    print("Press Ctrl+C to interrupt gracefully (completed tests will be saved)")
    print("-" * 80)
    
    # Run tests
    results = []
    start_time = datetime.now()
    logged_count = 0
    
    try:
        for idx, (test_id, query_type, query_text) in enumerate(test_queries, 1):
            # Check for interruption
            if interrupted:
                print("\n[INTERRUPTED] Stopping test execution after current test completes...")
                break
            
            session, logged = await run_single_test(
                test_id, query_type, query_text, 
                total_tests=100, 
                csv_manager=csv_manager
            )
            results.append((test_id, query_type, session, logged))
            
            if logged:
                logged_count += 1
            
            # Progress update every 10 tests
            if test_id % 10 == 0:
                elapsed = (datetime.now() - start_time).total_seconds()
                avg_time = elapsed / test_id
                remaining = (100 - test_id) * avg_time
                print("\n" + "=" * 80)
                print(f"PROGRESS: {test_id}/100 tests completed")
                print(f"Logged to CSV: {logged_count}/{test_id}")
                print(f"Elapsed: {elapsed/60:.1f} minutes")
                print(f"Estimated remaining: {remaining/60:.1f} minutes")
                print("=" * 80)
            
            # Check for interruption before sleep
            if interrupted:
                break
            
            # Sleep between tests (10 seconds normal, longer for batches)
            if test_id < 100:
                if test_id % 10 == 0:
                    # Longer sleep after every 10 tests
                    print("\n[Waiting 15 seconds before next batch...]")
                    # Check for interruption during sleep
                    for _ in range(15):
                        if interrupted:
                            break
                        await asyncio.sleep(1)
                else:
                    print("\n[Waiting 4 seconds before next test...]")
                    # Check for interruption during sleep
                    for _ in range(4):
                        if interrupted:
                            break
                        await asyncio.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Keyboard interrupt received. Saving progress...")
        interrupted = True
    
    # Final summary
    print("\n" + "=" * 80)
    if interrupted:
        print("TEST EXECUTION INTERRUPTED")
        print("=" * 80)
        print(f"Tests completed before interruption: {len(results)}/100")
        print(f"Tests logged to CSV: {logged_count}")
    else:
        print("TEST EXECUTION COMPLETED")
        print("=" * 80)
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    success_count = 0
    failed_count = 0
    error_count = 0
    type_success = {}
    type_failed = {}
    type_error = {}
    
    for result in results:
        if len(result) == 4:
            test_id, query_type, session, logged = result
        else:
            # Backward compatibility
            test_id, query_type, session = result[:3]
            logged = True
        
        if session is None:
            status = "ERROR"
            error_count += 1
            type_error[query_type] = type_error.get(query_type, 0) + 1
        elif session.state.get("original_goal_achieved", False):
            status = "SUCCESS"
            success_count += 1
            type_success[query_type] = type_success.get(query_type, 0) + 1
        else:
            status = "FAILED/PARTIAL"
            failed_count += 1
            type_failed[query_type] = type_failed.get(query_type, 0) + 1
        
        # Print only every 10th test in summary to keep it manageable
        if test_id % 10 == 0 or test_id <= 10:
            logged_status = "[LOGGED]" if logged else "[NOT LOGGED]"
            print(f"Test {test_id} [{query_type}]: {status} {logged_status}")
    
    print("\n" + "-" * 80)
    print("OVERALL STATISTICS")
    print("-" * 80)
    print(f"Total Tests Run: {len(results)}")
    print(f"Logged to CSV: {logged_count}")
    print(f"Success: {success_count} ({success_count*100/len(results):.1f}%)" if results else "Success: 0")
    print(f"Failed/Partial: {failed_count} ({failed_count*100/len(results):.1f}%)" if results else "Failed/Partial: 0")
    print(f"Errors: {error_count} ({error_count*100/len(results):.1f}%)" if results else "Errors: 0")
    
    print("\n" + "-" * 80)
    print("SUCCESS BY QUERY TYPE")
    print("-" * 80)
    all_types = set(type_success.keys() | type_failed.keys() | type_error.keys())
    for qtype in sorted(all_types):
        success = type_success.get(qtype, 0)
        failed = type_failed.get(qtype, 0)
        error = type_error.get(qtype, 0)
        total = success + failed + error
        if total > 0:
            print(f"  {qtype}: {success} success, {failed} failed, {error} errors ({success*100/total:.1f}% success)")
    
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()
    print("\n" + "-" * 80)
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Duration: {total_time/60:.1f} minutes")
    print("\n[CSV FILES]")
    print(f"  - tool_performance.csv: Contains {logged_count} logged test results")
    print(f"  - query_text.csv: Contains all query definitions")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

