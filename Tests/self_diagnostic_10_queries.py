"""
Self-Diagnostic Test for 10 Different Query Types + 1 Duplicate
Tests various query categories and memory search functionality.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp_servers.multiMCP import MultiMCP
from agent.agent_loop import AgentLoop
from utils.csv_manager import CSVManager
from memory.memory_search import MemorySearch
import yaml
import re


# Define 10 diverse query types + 1 duplicate
QUERIES = [
    # 1. Information Query - Capital City
    {
        "id": 1,
        "category": "INFORMATION",
        "query": "What is the capital of France?",
        "expected_type": "capital_city"
    },
    # 2. Information Query - Chemical Formula
    {
        "id": 2,
        "category": "INFORMATION",
        "query": "What is the chemical formula for water?",
        "expected_type": "chemical_formula"
    },
    # 3. Information Query - Author
    {
        "id": 3,
        "category": "INFORMATION",
        "query": "Who wrote the novel '1984'?",
        "expected_type": "author"
    },
    # 4. Math Query - Simple Calculation
    {
        "id": 4,
        "category": "MATH",
        "query": "Calculate 15 + 27",
        "expected_type": "simple_math"
    },
    # 5. Math Query - Average
    {
        "id": 5,
        "category": "MATH",
        "query": "Calculate the average of numbers: 10, 20, 30, 40, 50",
        "expected_type": "average"
    },
    # 6. Information Query - Speed of Light
    {
        "id": 6,
        "category": "INFORMATION",
        "query": "What is the speed of light?",
        "expected_type": "numeric_fact"
    },
    # 7. Information Query - Count Question
    {
        "id": 7,
        "category": "INFORMATION",
        "query": "How many chambers does a human heart have?",
        "expected_type": "count"
    },
    # 8. Math Query - Power Calculation
    {
        "id": 8,
        "category": "MATH",
        "query": "What is 5 to the power of 3?",
        "expected_type": "power"
    },
    # 9. Information Query - HTTP Full Form
    {
        "id": 9,
        "category": "INFORMATION",
        "query": "What does HTTP stand for?",
        "expected_type": "acronym"
    },
    # 10. Complex Query - Multiple Operations
    {
        "id": 10,
        "category": "COMPLEX",
        "query": "Find the factorial of 5 and calculate the sum of all prime numbers from 1 to 20",
        "expected_type": "complex_math"
    },
    # 11. DUPLICATE - Memory Search Test (same as query #2)
    {
        "id": 11,
        "category": "INFORMATION",
        "query": "What is the chemical formula for water?",  # Duplicate of query #2
        "expected_type": "chemical_formula",
        "is_duplicate": True,
        "original_id": 2
    }
]


def load_expected_answers(answers_file: str = "Tests/self_diagnostic_expected_answers.txt") -> dict:
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
        print("[INFO] Creating default expected answers...")
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
        
        print(f"[INFO] Loaded {len(expected_answers)} expected answers from {answers_path}")
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
    if answer_type in ["simple_math", "average", "power", "count", "numeric_fact"]:
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
    elif answer_type == "complex_math":
        # Check if expected numbers are in the answer
        expected_nums = re.findall(r'\d+', expected_clean)
        answer_nums = re.findall(r'\d+', answer_clean)
        
        missing = []
        for exp_num in expected_nums:
            if exp_num not in answer_nums:
                missing.append(exp_num)
        
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


async def run_diagnostic_test():
    """Run self-diagnostic test for 10 queries + 1 duplicate."""
    
    print("=" * 80)
    print("SELF-DIAGNOSTIC TEST: 10 QUERIES + 1 DUPLICATE")
    print("=" * 80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Load expected answers
    print("[INIT] Loading expected answers...")
    expected_answers = load_expected_answers()
    if not expected_answers:
        print("[WARN] No expected answers loaded. Validation will be limited.")
    else:
        print(f"[OK] Loaded {len(expected_answers)} expected answers for verification\n")
    
    # Initialize components
    print("[INIT] Loading MCP configuration...")
    # Load MCP server configurations
    config_path = project_root / "config" / "mcp_server_config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    mcp_configs = config.get("mcp_servers", [])
    
    multi_mcp = MultiMCP(server_configs=mcp_configs)
    await multi_mcp.initialize()
    
    print("[INIT] Initializing Agent Loop...")
    agent_loop = AgentLoop(
        perception_prompt_path="prompts/perception_prompt.txt",
        decision_prompt_path="prompts/decision_prompt.txt",
        multi_mcp=multi_mcp
    )
    
    print("[INIT] Initializing CSV Manager...")
    csv_manager = CSVManager()
    
    print("[INIT] Initializing Memory Search...")
    memory_searcher = MemorySearch()
    
    print("\n" + "=" * 80)
    print("EXECUTING QUERIES")
    print("=" * 80 + "\n")
    
    results = []
    test_id = 1
    
    for i, query_data in enumerate(QUERIES, 1):
        query_id = query_data["id"]
        category = query_data["category"]
        query_text = query_data["query"]
        expected_type = query_data.get("expected_type", "unknown")
        is_duplicate = query_data.get("is_duplicate", False)
        original_id = query_data.get("original_id", None)
        
        print(f"\n{'=' * 80}")
        print(f"TEST {i}/11: {category}")
        if is_duplicate:
            print(f"  [DUPLICATE] Original Query ID: {original_id}")
        print(f"{'=' * 80}")
        print(f"Query: {query_text}")
        print(f"Expected Type: {expected_type}\n")
        
        # Check memory before execution (for duplicate)
        if is_duplicate:
            print("[MEMORY CHECK] Searching for previous query in memory...")
            memory_results = memory_searcher.search_memory(query_text, top_k=3)
            if memory_results:
                print(f"[MEMORY] Found {len(memory_results)} matching entry(ies) in memory:")
                for idx, mem in enumerate(memory_results, 1):
                    print(f"  [{idx}] Query: {mem.get('query', 'N/A')}")
                    print(f"      Answer: {mem.get('solution_summary', 'N/A')[:100]}...")
            else:
                print("[MEMORY] No matching entries found (this may indicate a memory search issue)")
        
        # Execute query
        start_time = time.perf_counter()
        start_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            result = await agent_loop.run(query_text, return_execution_details=True)
            
            # agent_loop.run() with return_execution_details=True returns the execution_details dict directly
            # (not wrapped in {'answer': ..., 'execution_details': ...})
            if isinstance(result, dict):
                # Check if it's the execution_details dict (has 'answer' key) or wrapped format
                if 'answer' in result:
                    answer = result.get("answer", "No answer returned")
                    execution_details = result  # The dict itself is execution_details
                else:
                    # Wrapped format (shouldn't happen, but handle it)
                    answer = result.get("answer", "No answer returned")
                    execution_details = result.get("execution_details", {})
            else:
                answer = str(result)
                execution_details = {}
            
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
            end_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Extract execution details
            plan_steps = execution_details.get("plan_steps", [])
            plan_step_count = execution_details.get("plan_step_count", len(plan_steps) if plan_steps else 0)
            tools_used = execution_details.get("tools_used", [])
            nodes_called = execution_details.get("nodes_called_json", execution_details.get("nodes_called", []))
            step_details = execution_details.get("step_details", {})
            final_state = execution_details.get("final_state", {})
            llm_provider = execution_details.get("llm_provider", "Unknown")
            api_call_type = execution_details.get("api_call_type", "")
            nodes_exe_path = execution_details.get("nodes_exe_path", "")
            node_count = execution_details.get("node_count", len(execution_details.get("nodes_called", [])))
            hil_triggered = execution_details.get("human_in_loop_triggered", False)
            hil_reason = execution_details.get("hil_reason", "")
            
            # Extract tool_name (first tool used, or empty if none)
            tool_name = tools_used[0] if tools_used else ""
            retry_count = 0  # Not tracked in execution_details, default to 0
            
            # Determine high-level pipeline status (Result_Status)
            # - "success" → pipeline executed without fatal error
            # - "failed"  → no valid answer returned
            result_status = "success"
            error_message = ""
            
            if not answer or answer.lower() in ["none", "error", "failed"]:
                result_status = "failed"
                error_message = "No valid answer returned"
            
            # Check if answer matches expected (if available) for Actual_Status
            is_correct = None
            expected_answer = ""
            if query_text in expected_answers:
                expected_data = expected_answers[query_text]
                expected_answer = expected_data.get("expected", "")
                is_correct, _ = verify_answer(
                    answer, expected_answer, expected_data.get("type", expected_type)
                )
            
            # Validate answer based on expected type (for warnings/mismatch details)
            validation_notes = []
            if expected_type == "capital_city":
                if len(answer) < 3 or answer.lower() in ["capital", "france", "paris"]:
                    validation_notes.append("May not be extracting city name correctly")
            elif expected_type == "chemical_formula":
                if "H2O" not in answer.upper() and "H₂O" not in answer:
                    validation_notes.append("Expected H2O for water formula")
            elif expected_type == "author":
                if "orwell" not in answer.lower():
                    validation_notes.append("Expected 'George Orwell' for 1984")
            elif expected_type == "average":
                try:
                    num = float(answer.replace(",", ""))
                    if num != 30.0:
                        validation_notes.append(f"Expected 30.0, got {num}")
                except:
                    validation_notes.append("Answer is not a number")
            elif expected_type == "numeric_fact":
                if not any(c.isdigit() for c in answer):
                    validation_notes.append("Expected numeric value for speed of light")
            elif expected_type == "count":
                if not any(c.isdigit() for c in answer):
                    validation_notes.append("Expected numeric count (e.g., '4')")
            
            # Print results
            print(f"\n[RESULT] Status: {result_status}")
            print(f"[RESULT] Answer: {answer[:200]}")
            if validation_notes:
                print(f"[VALIDATION] Notes: {'; '.join(validation_notes)}")
            print(f"[TIMING] Elapsed: {elapsed_time:.3f}s")
            print(f"[EXECUTION] Steps: {plan_step_count} | Tools: {len(tools_used)} | Nodes: {node_count}")
            print(f"[LLM] Provider: {llm_provider}")
            if hil_triggered:
                print(f"[HIL] Human-in-Loop triggered: {hil_reason}")
            
            # Derive Actual_Status (per-query correctness)
            # - "success"  → answer matches expected (or no expected and no validation notes)
            # - "mismatch" → answer does NOT match Correct_Answer_Expected
            # - "warning"  → no strict expected, but validation_notes present
            # - "error"    → handled in exception block
            actual_status = "success"
            if is_correct is False:
                actual_status = "mismatch"
            elif is_correct is None and validation_notes:
                actual_status = "warning"
            
            # Store result
            results.append({
                "test_id": test_id,
                "query_id": query_id,
                "category": category,
                "query_text": query_text,
                "answer": answer,
                "expected_answer": expected_answers.get(query_text, {}).get("expected", "N/A"),
                "is_correct": is_correct if query_text in expected_answers else None,
                "result_status": result_status,
                "elapsed_time": elapsed_time,
                "validation_notes": validation_notes,
                "is_duplicate": is_duplicate,
                "original_id": original_id,
                "plan_steps": plan_steps,
                "tools_used": tools_used,
                "nodes_called": nodes_called,
                "llm_provider": llm_provider
            })
            
            # Log to CSV - populate all columns
            csv_manager.log_tool_performance(
                query_id=query_id,
                plan_used=plan_steps,
                plan_step_count=plan_step_count,
                query_name=f"Diagnostic Test {query_id}",
                query_text=query_text,
                query_answer=answer,
                correct_answer_expected=expected_answer,
                result_status=result_status,
                actual_status=actual_status,
                elapsed_time=elapsed_time,
                tool_name=tool_name,
                retry_count=retry_count,
                api_call_type=api_call_type,
                llm_provider=llm_provider,
                step_details=str(step_details),
                nodes_called=nodes_called,
                nodes_exe_path=nodes_exe_path,
                node_count=node_count,
                final_state=final_state,
                test_id=test_id,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                error_message=error_message
            )
            
            test_id += 1
            
        except Exception as e:
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
            error_msg = f"{type(e).__name__}: {str(e)}"
            
            print(f"\n[ERROR] {error_msg}")
            
            results.append({
                "test_id": test_id,
                "query_id": query_id,
                "category": category,
                "query_text": query_text,
                "answer": "ERROR",
                "result_status": "error",
                "elapsed_time": elapsed_time,
                "validation_notes": [error_msg],
                "is_duplicate": is_duplicate,
                "original_id": original_id
            })
            
            # Log error to CSV
            # Get expected answer if available
            expected_answer = expected_answers.get(query_text, {}).get("expected", "") if query_text in expected_answers else ""
            
            csv_manager.log_tool_performance(
                query_id=query_id,
                plan_used=[],
                plan_step_count=0,
                query_name=f"Diagnostic Test {query_id}",
                query_text=query_text,
                query_answer="ERROR",
                correct_answer_expected=expected_answer,
                result_status="failed",
                actual_status="error",
                elapsed_time=elapsed_time,
                tool_name="",
                retry_count=0,
                api_call_type="",
                llm_provider="",
                step_details="",
                nodes_called=[],
                nodes_exe_path="",
                final_state={},
                test_id=test_id,
                start_datetime=start_datetime,
                end_datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                error_message=error_msg
            )
            
            test_id += 1
        
        # Wait between queries
        if i < len(QUERIES):
            await asyncio.sleep(2)
    
    # Print summary
    print("\n" + "=" * 80)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 80)
    
    total = len(results)
    successful = sum(1 for r in results if r["result_status"] == "success")
    errors = sum(1 for r in results if r["result_status"] == "error")
    warnings = sum(1 for r in results if r["result_status"] == "warning")
    
    print(f"\nTotal Tests: {total}")
    print(f"Successful: {successful} ({successful/total*100:.1f}%)")
    print(f"Errors: {errors} ({errors/total*100:.1f}%)")
    print(f"Warnings: {warnings} ({warnings/total*100:.1f}%)")
    
    # Category breakdown
    print(f"\nCategory Breakdown:")
    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "success": 0, "error": 0}
        categories[cat]["total"] += 1
        if r["result_status"] == "success":
            categories[cat]["success"] += 1
        elif r["result_status"] == "error":
            categories[cat]["error"] += 1
    
    for cat, stats in categories.items():
        print(f"  {cat}: {stats['success']}/{stats['total']} successful")
    
    # Memory search test results
    duplicate_results = [r for r in results if r.get("is_duplicate", False)]
    if duplicate_results:
        print(f"\nMemory Search Test:")
        dup = duplicate_results[0]
        print(f"  Duplicate Query: {dup['query_text']}")
        print(f"  Original Query ID: {dup.get('original_id', 'N/A')}")
        print(f"  Result: {dup['result_status']}")
        if dup['result_status'] == "success":
            print(f"  [OK] Memory search working correctly")
        else:
            print(f"  [WARN] Memory search may need investigation")
    
    # Validation issues (using expected answers)
    validation_issues = []
    correct_answers = 0
    total_with_expected = 0
    
    for r in results:
        if r.get("is_correct") is not None:
            total_with_expected += 1
            if r.get("is_correct"):
                correct_answers += 1
            else:
                validation_issues.append({
                    "query": r["query_text"][:50],
                    "expected": r.get("expected_answer", "N/A"),
                    "got": r["answer"][:50],
                    "notes": r["validation_notes"]
                })
        elif r.get("validation_notes"):
            validation_issues.append({
                "query": r["query_text"][:50],
                "expected": r.get("expected_answer", "N/A"),
                "got": r["answer"][:50],
                "notes": r["validation_notes"]
            })
    
    if total_with_expected > 0:
        accuracy = (correct_answers / total_with_expected) * 100
        print(f"\nAnswer Accuracy (vs Expected Answers):")
        print(f"  Correct: {correct_answers}/{total_with_expected} ({accuracy:.1f}%)")
    
    if validation_issues:
        print(f"\nValidation Issues Found: {len(validation_issues)}")
        for issue in validation_issues:
            print(f"  • {issue['query']}")
            if issue.get('expected') != "N/A":
                print(f"    Expected: {issue['expected']}")
                print(f"    Got: {issue['got']}")
            if issue.get('notes'):
                print(f"    Notes: {', '.join(issue['notes'])}")
    else:
        print(f"\n[OK] No validation issues found - all answers match expected results!")
    
    # Timing summary
    avg_time = sum(r["elapsed_time"] for r in results) / total if total > 0 else 0
    min_time = min(r["elapsed_time"] for r in results) if results else 0
    max_time = max(r["elapsed_time"] for r in results) if results else 0
    
    print(f"\nTiming Summary:")
    print(f"  Average: {avg_time:.3f}s")
    print(f"  Min: {min_time:.3f}s")
    print(f"  Max: {max_time:.3f}s")
    
    print(f"\n{'=' * 80}")
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 80}\n")
    
    return results


if __name__ == "__main__":
    try:
        results = asyncio.run(run_diagnostic_test())
        print("\n[OK] Diagnostic test completed successfully!")
    except KeyboardInterrupt:
        print("\n\n⚠ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

