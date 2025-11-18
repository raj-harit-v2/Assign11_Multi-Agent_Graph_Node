"""
Small Diagnostic Test for Session 10 Implementation
Tests core components without requiring full MCP setup.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all core modules can be imported."""
    print("=" * 60)
    print("TEST 1: Module Imports")
    print("=" * 60)
    
    try:
        from core.human_in_loop import ask_user_for_tool_result, ask_user_for_plan
        print("[OK] core.human_in_loop imported successfully")
    except Exception as e:
        print(f"[FAIL] core.human_in_loop import failed: {e}")
        return False
    
    try:
        from core.control_manager import ControlManager
        print("[OK] core.control_manager imported successfully")
    except Exception as e:
        print(f"[FAIL] core.control_manager import failed: {e}")
        return False
    
    try:
        from utils.csv_manager import CSVManager
        print("[OK] utils.csv_manager imported successfully")
    except Exception as e:
        print(f"[FAIL] utils.csv_manager import failed: {e}")
        return False
    
    try:
        from utils.time_utils import get_current_datetime, calculate_elapsed_time
        print("[OK] utils.time_utils imported successfully")
    except Exception as e:
        print(f"[FAIL] utils.time_utils import failed: {e}")
        return False
    
    try:
        from utils.statistics_generator import StatisticsGenerator
        print("[OK] utils.statistics_generator imported successfully")
    except Exception as e:
        print(f"[FAIL] utils.statistics_generator import failed: {e}")
        return False
    
    try:
        from simulator.sleep_manager import sleep_after_test, sleep_after_batch
        print("[OK] simulator.sleep_manager imported successfully")
    except Exception as e:
        print(f"[FAIL] simulator.sleep_manager import failed: {e}")
        return False
    
    return True


def test_control_manager():
    """Test ControlManager functionality."""
    print("\n" + "=" * 60)
    print("TEST 2: Control Manager")
    print("=" * 60)
    
    try:
        from core.control_manager import ControlManager
        
        cm = ControlManager()
        print(f"[OK] ControlManager instantiated")
        print(f"  - MAX_STEPS: {cm.get_max_steps()}")
        print(f"  - MAX_RETRIES: {cm.get_max_retries()}")
        
        # Test step limit check
        is_limit, msg = cm.check_step_limit(2)
        print(f"  - Step limit check (step 2): {is_limit} - {msg}")
        
        is_limit, msg = cm.check_step_limit(3)
        print(f"  - Step limit check (step 3): {is_limit} - {msg}")
        
        # Test retry limit check
        is_limit, msg = cm.check_retry_limit(2)
        print(f"  - Retry limit check (retry 2): {is_limit} - {msg}")
        
        is_limit, msg = cm.check_retry_limit(3)
        print(f"  - Retry limit check (retry 3): {is_limit} - {msg}")
        
        return True
    except Exception as e:
        print(f"[FAIL] ControlManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_csv_manager():
    """Test CSVManager functionality."""
    print("\n" + "=" * 60)
    print("TEST 3: CSV Manager")
    print("=" * 60)
    
    try:
        from utils.csv_manager import CSVManager
        
        csv_mgr = CSVManager()
        print("[OK] CSVManager instantiated")
        
        # Test adding a query
        query_id = csv_mgr.add_query("Test query for diagnostic")
        print(f"[OK] Query added with ID: {query_id[:8]}...")
        
        # Test logging performance
        csv_mgr.log_tool_performance(
            test_id=1,
            query_id=query_id,
            query_text="Test query for diagnostic",
            plan_used=["Step 1", "Step 2"],
            result_status="success",
            start_datetime="2025-01-01 10:00:00",
            end_datetime="2025-01-01 10:00:05",
            elapsed_time="5.000",
            plan_step_count=2,
            tool_name="test_tool",
            retry_count=0,
            error_message="",
            final_state={"goal_achieved": True}
        )
        print("[OK] Performance logged to CSV")
        
        # Test reading queries
        queries = csv_mgr.get_all_queries()
        print(f"[OK] Retrieved {len(queries)} queries from CSV")
        
        # Test reading performance
        perf = csv_mgr.get_tool_performance()
        print(f"[OK] Retrieved {len(perf)} performance records from CSV")
        
        return True
    except Exception as e:
        print(f"[FAIL] CSVManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_time_utils():
    """Test time utilities."""
    print("\n" + "=" * 60)
    print("TEST 4: Time Utilities")
    print("=" * 60)
    
    try:
        from utils.time_utils import get_current_datetime, calculate_elapsed_time
        import time
        
        dt = get_current_datetime()
        print(f"[OK] Current datetime: {dt}")
        
        start = time.perf_counter()
        time.sleep(0.1)
        end = time.perf_counter()
        elapsed = calculate_elapsed_time(start, end)
        print(f"[OK] Elapsed time calculated: {elapsed} seconds")
        
        return True
    except Exception as e:
        print(f"[FAIL] Time utils test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_statistics_generator():
    """Test statistics generator."""
    print("\n" + "=" * 60)
    print("TEST 5: Statistics Generator")
    print("=" * 60)
    
    try:
        from utils.statistics_generator import StatisticsGenerator
        
        gen = StatisticsGenerator()
        print("[OK] StatisticsGenerator instantiated")
        
        stats = gen.generate_statistics()
        print(f"[OK] Statistics generated")
        print(f"  - Total tests: {stats.get('total_tests', 0)}")
        print(f"  - Successes: {stats.get('successes', 0)}")
        print(f"  - Failures: {stats.get('failures', 0)}")
        
        return True
    except Exception as e:
        print(f"[FAIL] StatisticsGenerator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_human_in_loop():
    """Test human-in-loop functions exist."""
    print("\n" + "=" * 60)
    print("TEST 6: Human-in-Loop")
    print("=" * 60)
    
    try:
        from core.human_in_loop import ask_user_for_tool_result, ask_user_for_plan
        
        print("[OK] Human-in-loop functions imported")
        print("  - ask_user_for_tool_result: Available")
        print("  - ask_user_for_plan: Available")
        
        # Test that functions are callable (but don't actually call them in diagnostic)
        assert callable(ask_user_for_tool_result)
        assert callable(ask_user_for_plan)
        print("[OK] Functions are callable")
        
        return True
    except Exception as e:
        print(f"[FAIL] Human-in-loop test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_file_structure():
    """Test that required files and directories exist."""
    print("\n" + "=" * 60)
    print("TEST 7: File Structure")
    print("=" * 60)
    
    required_files = [
        "core/human_in_loop.py",
        "core/control_manager.py",
        "utils/csv_manager.py",
        "utils/time_utils.py",
        "utils/statistics_generator.py",
        "simulator/run_simulator.py",
        "simulator/sleep_manager.py",
        "Tests/sample_queries.txt",
        "Tests/S10_arch.md",
        "Tests/S10_init_arch01.md",
        "README.md"
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"[OK] {file_path}")
        else:
            print(f"[FAIL] {file_path} - MISSING")
            all_exist = False
    
    # Check data directory
    data_dir = project_root / "data"
    if data_dir.exists():
        print(f"[OK] data/ directory exists")
    else:
        print(f"[FAIL] data/ directory - MISSING")
        all_exist = False
    
    return all_exist


def main():
    """Run all diagnostic tests."""
    print("\n" + "=" * 60)
    print("SESSION 10 DIAGNOSTIC TEST")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Control Manager", test_control_manager()))
    results.append(("CSV Manager", test_csv_manager()))
    results.append(("Time Utils", test_time_utils()))
    results.append(("Statistics Generator", test_statistics_generator()))
    results.append(("Human-in-Loop", test_human_in_loop()))
    results.append(("File Structure", test_file_structure()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All diagnostic tests passed!")
        return 0
    else:
        print(f"\n[FAILURE] {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

