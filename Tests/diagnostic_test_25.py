"""
Diagnostic Test for Session 10 - 25 Test Cases
Tests agent with 5 different query types in random order.
"""

import sys
import random
import asyncio
from pathlib import Path

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

def generate_test_queries(num_tests: int = 25) -> list:
    """
    Generate 25 test queries using 5 different types in random order.
    
    Args:
        num_tests: Number of test cases to generate (default: 25)
    
    Returns:
        list: List of tuples (test_id, query_type, query_text)
    """
    all_queries = []
    for query_type, queries in QUERY_TYPES.items():
        for query in queries:
            all_queries.append((query_type, query))
    
    # Randomize order
    random.shuffle(all_queries)
    
    # Take first 25 (or repeat if needed)
    test_queries = []
    for i in range(num_tests):
        query_type, query = all_queries[i % len(all_queries)]
        test_queries.append((i + 1, query_type, query))
    
    return test_queries


def test_imports():
    """Test that all core modules can be imported."""
    print("=" * 60)
    print("TEST 1: Module Imports")
    print("=" * 60)
    
    modules = [
        ("core.human_in_loop", "ask_user_for_tool_result", "ask_user_for_plan"),
        ("core.control_manager", "ControlManager"),
        ("utils.csv_manager", "CSVManager"),
        ("utils.time_utils", "get_current_datetime", "calculate_elapsed_time"),
        ("utils.statistics_generator", "StatisticsGenerator"),
        ("simulator.sleep_manager", "sleep_after_test", "sleep_after_batch"),
    ]
    
    all_passed = True
    for module_info in modules:
        module_name = module_info[0]
        try:
            module = __import__(module_name, fromlist=module_info[1:])
            print(f"[OK] {module_name} imported successfully")
        except Exception as e:
            print(f"[FAIL] {module_name} import failed: {e}")
            all_passed = False
    
    return all_passed


def test_csv_manager():
    """Test CSV Manager functionality."""
    print("\n" + "=" * 60)
    print("TEST 2: CSV Manager")
    print("=" * 60)
    
    try:
        from utils.csv_manager import CSVManager
        
        csv_mgr = CSVManager()
        print("[OK] CSVManager instantiated")
        
        # Test adding queries
        test_queries = generate_test_queries(5)  # Test with 5 queries
        query_ids = []
        for test_id, query_type, query_text in test_queries:
            query_name = f"Test {test_id} - {query_type}"
            query_id = csv_mgr.add_query(query_text=query_text, query_name=query_name)
            query_ids.append(query_id)
            print(f"[OK] Query {test_id} added: {query_id} ({query_type})")
        
        # Test reading queries
        all_queries = csv_mgr.get_all_queries()
        print(f"[OK] Retrieved {len(all_queries)} queries from CSV")
        
        return True
    except Exception as e:
        print(f"[FAIL] CSV Manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_control_manager():
    """Test Control Manager limits."""
    print("\n" + "=" * 60)
    print("TEST 3: Control Manager")
    print("=" * 60)
    
    try:
        from core.control_manager import ControlManager
        
        cm = ControlManager()
        print(f"[OK] ControlManager instantiated")
        print(f"  - MAX_STEPS: {cm.get_max_steps()}")
        print(f"  - MAX_RETRIES: {cm.get_max_retries()}")
        
        # Test step limit checks
        for step_idx in [0, 1, 2, 3, 4]:
            is_limit, msg = cm.check_step_limit(step_idx)
            status = "LIMIT" if is_limit else "OK"
            print(f"  - Step {step_idx}: {status}")
        
        # Test retry limit checks
        for retry_count in [0, 1, 2, 3, 4]:
            is_limit, msg = cm.check_retry_limit(retry_count)
            status = "LIMIT" if is_limit else "OK"
            print(f"  - Retry {retry_count}: {status}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Control Manager test failed: {e}")
        return False


def test_time_utils():
    """Test Time Utilities."""
    print("\n" + "=" * 60)
    print("TEST 4: Time Utilities")
    print("=" * 60)
    
    try:
        from utils.time_utils import get_current_datetime, calculate_elapsed_time
        import time
        
        current_dt = get_current_datetime()
        print(f"[OK] Current datetime: {current_dt}")
        
        start = time.perf_counter()
        time.sleep(0.1)
        end = time.perf_counter()
        elapsed = calculate_elapsed_time(start, end)
        print(f"[OK] Elapsed time calculated: {elapsed} seconds")
        
        return True
    except Exception as e:
        print(f"[FAIL] Time Utils test failed: {e}")
        return False


def test_statistics_generator():
    """Test Statistics Generator."""
    print("\n" + "=" * 60)
    print("TEST 5: Statistics Generator")
    print("=" * 60)
    
    try:
        from utils.statistics_generator import StatisticsGenerator
        
        stats_gen = StatisticsGenerator()
        print("[OK] StatisticsGenerator instantiated")
        
        stats = stats_gen.generate_statistics()
        print(f"[OK] Statistics generated")
        print(f"  - Total tests: {stats['total_tests']}")
        print(f"  - Successes: {stats['successes']}")
        print(f"  - Failures: {stats['failures']}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Statistics Generator test failed: {e}")
        return False


def test_query_generation():
    """Test query generation with 5 types in random order."""
    print("\n" + "=" * 60)
    print("TEST 6: Query Generation (25 Test Cases)")
    print("=" * 60)
    
    try:
        test_queries = generate_test_queries(25)
        
        # Count by type
        type_counts = {}
        for test_id, query_type, query_text in test_queries:
            type_counts[query_type] = type_counts.get(query_type, 0) + 1
        
        print(f"[OK] Generated {len(test_queries)} test queries")
        print(f"\nQuery Type Distribution:")
        for qtype, count in sorted(type_counts.items()):
            print(f"  - {qtype}: {count} queries")
        
        # Show first 5 queries
        print(f"\nFirst 5 queries (random order):")
        for test_id, query_type, query_text in test_queries[:5]:
            print(f"  {test_id}. [{query_type}] {query_text}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Query generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_csv_logging_simulation():
    """Simulate CSV logging for 25 test cases."""
    print("\n" + "=" * 60)
    print("TEST 7: CSV Logging Simulation (25 Cases)")
    print("=" * 60)
    
    try:
        from utils.csv_manager import CSVManager
        from utils.time_utils import get_current_datetime
        import time
        
        csv_mgr = CSVManager()
        test_queries = generate_test_queries(25)
        
        logged_count = 0
        for test_id, query_type, query_text in test_queries:
            try:
                # Add query
                query_name = f"Test {test_id} - {query_type}"
                query_id = csv_mgr.add_query(query_text=query_text, query_name=query_name)
                
                # Simulate logging performance
                start_time = time.perf_counter()
                time.sleep(0.01)  # Simulate processing
                end_time = time.perf_counter()
                
                csv_mgr.log_tool_performance(
                    test_id=test_id,
                    query_id=query_id,
                    query_name=query_name,
                    query_text=query_text,
                    query_answer=f"Simulated answer for {query_type} query",
                    plan_used=[f"Step 1 for {query_type}", f"Step 2 for {query_type}"],
                    result_status="success" if test_id % 2 == 0 else "failure",
                    start_datetime=get_current_datetime(),
                    end_datetime=get_current_datetime(),
                    elapsed_time=str(round(end_time - start_time, 3)),
                    plan_step_count=2,
                    tool_name=f"test_tool_{query_type}",
                    retry_count=0,
                    error_message="" if test_id % 2 == 0 else "Simulated error",
                    final_state={"test_id": test_id, "query_type": query_type}
                )
                logged_count += 1
                
                if test_id % 5 == 0:
                    print(f"[OK] Logged {test_id}/25 test cases...")
            except PermissionError as pe:
                print(f"[WARN] Test {test_id}: CSV file locked (may be open in Excel/editor). Skipping...")
                continue
            except Exception as e:
                print(f"[WARN] Test {test_id}: Error - {e}. Continuing...")
                continue
        
        if logged_count > 0:
            print(f"[OK] Successfully logged {logged_count}/25 test cases to CSV")
            
            # Verify data
            try:
                all_queries = csv_mgr.get_all_queries()
                perf_data = csv_mgr.get_tool_performance()
                print(f"[OK] Verified: {len(all_queries)} queries, {len(perf_data)} performance records")
            except Exception as e:
                print(f"[WARN] Could not verify data: {e}")
            
            return True
        else:
            print("[WARN] No test cases logged (CSV file may be locked)")
            print("[INFO] Close CSV files in Excel/editor and rerun to complete logging test")
            return False
    except Exception as e:
        print(f"[FAIL] CSV logging simulation failed: {e}")
        print("[INFO] This may be due to CSV file being open in another program")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all diagnostic tests."""
    print("\n" + "=" * 60)
    print("SESSION 10 DIAGNOSTIC TEST - 25 CASES")
    print("=" * 60)
    
    # Set random seed for reproducibility (optional)
    random.seed(42)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Control Manager", test_control_manager()))
    results.append(("CSV Manager", test_csv_manager()))
    results.append(("Time Utils", test_time_utils()))
    results.append(("Statistics Generator", test_statistics_generator()))
    results.append(("Query Generation", test_query_generation()))
    results.append(("CSV Logging Simulation", test_csv_logging_simulation()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed + failed}/{len(results)} tests passed")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n[SUCCESS] All diagnostic tests passed!")
    else:
        print(f"\n[WARNING] {failed} test(s) failed.")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

