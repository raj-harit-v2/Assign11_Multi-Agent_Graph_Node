"""
Generate Result Statistics from tool_performance.csv
Creates a markdown report similar to Result_Stats.md format
"""

import csv
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple
from datetime import datetime


def parse_elapsed_time(time_str: str) -> float:
    """Parse elapsed time from string to float."""
    try:
        return float(time_str) if time_str else 0.0
    except (ValueError, TypeError):
        return 0.0


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to max_length with ellipsis."""
    if not text:
        return ""
    text = str(text).strip()
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def generate_statistics(csv_path: Path = None, output_path: Path = None, generate_csv: bool = True) -> str:
    """
    Generate statistics from tool_performance.csv and save to markdown file.
    Optionally generate CSV statistics file.
    
    Args:
        csv_path: Path to tool_performance.csv (default: data/tool_performance.csv)
        output_path: Path to output markdown file (default: data/Result_Stats.md)
        generate_csv: Whether to also generate CSV statistics file (default: True)
    
    Returns:
        str: Path to generated statistics file
    """
    if csv_path is None:
        csv_path = Path("data/tool_performance.csv")
    if output_path is None:
        output_path = Path("data/Result_Stats.md")
    
    if not csv_path.exists():
        print(f"[ERROR] CSV file not found: {csv_path}")
        return None
    
    # Read CSV data
    records = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        records = list(reader)
    
    if not records:
        print(f"[ERROR] No records found in {csv_path}")
        return None
    
    print(f"[OK] Loaded {len(records)} records from {csv_path}")
    
    # Initialize statistics
    total_tests = len(records)
    successes = 0
    failures = 0
    total_time = 0.0
    
    # Tool statistics
    tool_stats = defaultdict(lambda: {
        "attempts": 0,
        "successes": 0,
        "failures": 0,
        "total_time": 0.0
    })
    
    # Query statistics (by Query_Id)
    query_stats = defaultdict(lambda: {
        "attempts": 0,
        "successes": 0,
        "failures": 0,
        "total_time": 0.0,
        "query_text": "",
        "query_name": "",
        "query_id": None
    })
    
    # Failure reasons
    failure_reasons = defaultdict(int)
    
    # Process records
    for record in records:
        result_status = record.get('Result_Status', '').lower()
        elapsed_time = parse_elapsed_time(record.get('Elapsed_Time', '0'))
        tool_name = record.get('Tool_Name', 'unknown')
        query_id = record.get('Query_Id', '')
        query_text = record.get('Query_Text', '')
        query_name = record.get('Query_Name', '')
        error_message = record.get('Error_Message', '')
        
        # Count successes/failures
        if result_status == 'success':
            successes += 1
        else:
            failures += 1
            if error_message:
                # Extract failure reason (first 100 chars)
                reason = error_message[:100].strip()
                if reason:
                    failure_reasons[reason] += 1
        
        total_time += elapsed_time
        
        # Tool statistics
        tool_stats[tool_name]["attempts"] += 1
        tool_stats[tool_name]["total_time"] += elapsed_time
        if result_status == 'success':
            tool_stats[tool_name]["successes"] += 1
        else:
            tool_stats[tool_name]["failures"] += 1
        
        # Query statistics
        if query_id:
            query_key = str(query_id)
            query_stats[query_key]["attempts"] += 1
            query_stats[query_key]["total_time"] += elapsed_time
            query_stats[query_key]["query_id"] = query_id
            if not query_stats[query_key]["query_text"]:
                query_stats[query_key]["query_text"] = query_text
            if not query_stats[query_key]["query_name"]:
                query_stats[query_key]["query_name"] = query_name
            if result_status == 'success':
                query_stats[query_key]["successes"] += 1
            else:
                query_stats[query_key]["failures"] += 1
    
    # Calculate averages
    avg_time_per_test = total_time / total_tests if total_tests > 0 else 0.0
    success_rate = (successes / total_tests * 100) if total_tests > 0 else 0.0
    
    # Find most used tool
    most_used_tool = ""
    max_attempts = 0
    for tool, stats in tool_stats.items():
        if stats["attempts"] > max_attempts:
            max_attempts = stats["attempts"]
            most_used_tool = tool
    
    # Find worst tool (by failure rate)
    worst_tool = "N/A"
    worst_failure_rate = 0.0
    for tool, stats in tool_stats.items():
        if stats["attempts"] > 0:
            failure_rate = (stats["failures"] / stats["attempts"] * 100)
            if failure_rate > worst_failure_rate and stats["attempts"] >= 3:  # At least 3 attempts
                worst_failure_rate = failure_rate
                worst_tool = tool
    
    # Generate markdown report
    md_content = []
    md_content.append("# Tool Performance Statistics\n")
    md_content.append("## Overview\n")
    md_content.append(f"- **Total Tests**: {total_tests}")
    md_content.append(f"- **Successes**: {successes}")
    md_content.append(f"- **Failures**: {failures}")
    md_content.append(f"- **Success Rate**: {success_rate:.2f}%")
    md_content.append(f"- **Average Time per Test**: {avg_time_per_test:.3f} seconds\n")
    
    # Tool Performance Table
    md_content.append("## Tool Performance\n")
    md_content.append("| Tool Name | Attempts | Successes | Failures | Success Rate | Avg Time |")
    md_content.append("|-----------|----------|-----------|----------|--------------|----------|")
    
    # Sort tools by attempts (descending)
    sorted_tools = sorted(tool_stats.items(), key=lambda x: x[1]["attempts"], reverse=True)
    for tool_name, stats in sorted_tools:
        attempts = stats["attempts"]
        tool_successes = stats["successes"]
        tool_failures = stats["failures"]
        tool_success_rate = (tool_successes / attempts * 100) if attempts > 0 else 0.0
        avg_time = (stats["total_time"] / attempts) if attempts > 0 else 0.0
        md_content.append(
            f"| {tool_name} | {attempts} | {tool_successes} | {tool_failures} | "
            f"{tool_success_rate:.2f}% | {avg_time:.3f}s |"
        )
    
    # Query Text Statistics
    md_content.append("\n## Query Text Statistics\n")
    md_content.append(
        "| Query_Id | Query Text (truncated) | Query Name | Attempts | Successes | "
        "Failures | Success Rate | Total Time | Avg Time |"
    )
    md_content.append(
        "|----------|------------------------|------------|----------|-----------|"
        "----------|--------------|------------|----------|"
    )
    
    # Sort queries by Query_Id (numeric)
    sorted_queries = sorted(
        query_stats.items(),
        key=lambda x: int(x[1]["query_id"]) if x[1]["query_id"] and str(x[1]["query_id"]).isdigit() else 999999
    )
    
    for query_key, stats in sorted_queries:
        query_id = stats["query_id"] or query_key
        attempts = stats["attempts"]
        query_successes = stats["successes"]
        query_failures = stats["failures"]
        query_success_rate = (query_successes / attempts * 100) if attempts > 0 else 0.0
        total_time = stats["total_time"]
        avg_time = (total_time / attempts) if attempts > 0 else 0.0
        query_text = truncate_text(stats["query_text"], 50)
        query_name = stats["query_name"] or ""
        
        md_content.append(
            f"| {query_id} | {query_text} | {query_name} | {attempts} | "
            f"{query_successes} | {query_failures} | {query_success_rate:.2f}% | "
            f"{total_time:.3f}s | {avg_time:.3f}s |"
        )
    
    # Summary
    md_content.append("\n## Summary\n")
    md_content.append(f"- **Total Time (All Queries)**: {total_time:.3f} seconds")
    md_content.append(f"- **Most Used Tool**: {most_used_tool}")
    md_content.append(f"- **Worst Tool (by failure rate)**: {worst_tool}")
    md_content.append(f"- **Unique Query Texts**: {len(query_stats)}\n")
    
    # Common Failure Reasons
    if failure_reasons:
        md_content.append("## Common Failure Reasons\n")
        # Sort by frequency (descending)
        sorted_failures = sorted(failure_reasons.items(), key=lambda x: x[1], reverse=True)
        for reason, count in sorted_failures:
            md_content.append(f"- {reason}: {count} occurrences")
    
    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_content))
    
    print(f"[OK] Statistics generated: {output_path}")
    print(f"[OK] Total tests: {total_tests}, Successes: {successes}, Failures: {failures}")
    print(f"[OK] Success rate: {success_rate:.2f}%")
    print(f"[OK] Average time: {avg_time_per_test:.3f} seconds")
    
    # Generate CSV statistics if requested
    if generate_csv:
        csv_output_path = output_path.parent / "query_statistics.csv"
        generate_csv_statistics(records, query_stats, csv_output_path)
    
    return str(output_path)


def generate_csv_statistics(records: List[Dict], query_stats: Dict, csv_path: Path):
    """
    Generate CSV statistics file from query statistics.
    
    Args:
        records: List of all records from tool_performance.csv
        query_stats: Dictionary of query statistics
        csv_path: Path to output CSV file
    """
    import csv
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Headers
        writer.writerow([
            "Query_Id", "Query_Text", "Query_Name", "Total_Attempts", "Successes", "Failures",
            "Success_Rate_Percent", "Total_Time_Seconds", "Avg_Time_Seconds"
        ])
        
        # Sort queries by Query_Id
        sorted_queries = sorted(
            query_stats.items(),
            key=lambda x: int(x[1]["query_id"]) if x[1]["query_id"] and str(x[1]["query_id"]).isdigit() else 999999
        )
        
        for query_key, stats in sorted_queries:
            query_id = stats["query_id"] or query_key
            attempts = stats["attempts"]
            query_successes = stats["successes"]
            query_failures = stats["failures"]
            query_success_rate = (query_successes / attempts * 100) if attempts > 0 else 0.0
            total_time = stats["total_time"]
            avg_time = (total_time / attempts) if attempts > 0 else 0.0
            query_text = stats["query_text"][:200] if stats["query_text"] else ""  # Truncate long queries
            query_name = stats["query_name"][:100] if stats["query_name"] else ""
            
            writer.writerow([
                query_id,
                query_text,
                query_name,
                attempts,
                query_successes,
                query_failures,
                f"{query_success_rate:.2f}",
                f"{total_time:.3f}",
                f"{avg_time:.3f}"
            ])
    
    print(f"[OK] CSV statistics generated: {csv_path}")


if __name__ == "__main__":
    # Generate statistics
    output_file = generate_statistics()
    if output_file:
        print(f"\n[SUCCESS] Statistics report saved to: {output_file}")
    else:
        print("\n[ERROR] Failed to generate statistics")

