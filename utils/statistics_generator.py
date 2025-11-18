"""
Statistics Generator for Session 10
Generates statistics from tool_performance.csv
"""

from utils.csv_manager import CSVManager
from pathlib import Path
from collections import defaultdict
from typing import Dict, List


class StatisticsGenerator:
    """Generates statistics from tool performance data."""
    
    def __init__(self):
        self.csv_manager = CSVManager()
    
    def generate_statistics(self) -> Dict:
        """
        Generate comprehensive statistics from tool_performance.csv.
        
        Returns:
            dict: Statistics dictionary
        """
        records = self.csv_manager.get_tool_performance()
        
        if not records:
            return {"error": "No performance records found"}
        
        stats = {
            "total_tests": len(records),
            "successes": 0,
            "failures": 0,
            "by_tool": defaultdict(lambda: {"attempts": 0, "successes": 0, "failures": 0, "total_time": 0.0}),
            "avg_time_per_test": 0.0,
            "most_used_tool": "",
            "worst_tool": "",
            "failure_reasons": defaultdict(int)
        }
        
        total_time = 0.0
        
        for record in records:
            # Count successes/failures
            if record.get("Result_Status", "").lower() == "success":
                stats["successes"] += 1
            else:
                stats["failures"] += 1
                error_msg = record.get("Error_Message", "Unknown error")
                if error_msg:
                    stats["failure_reasons"][error_msg[:100]] += 1
            
            # Tool statistics
            tool_name = record.get("Tool_Name", "unknown")
            if tool_name:
                stats["by_tool"][tool_name]["attempts"] += 1
                if record.get("Result_Status", "").lower() == "success":
                    stats["by_tool"][tool_name]["successes"] += 1
                else:
                    stats["by_tool"][tool_name]["failures"] += 1
                
                # Calculate time
                try:
                    elapsed = float(record.get("Elapsed_Time", "0"))
                    stats["by_tool"][tool_name]["total_time"] += elapsed
                    total_time += elapsed
                except:
                    pass
        
        # Calculate averages
        if stats["total_tests"] > 0:
            stats["avg_time_per_test"] = total_time / stats["total_tests"]
        
        # Find most used tool
        if stats["by_tool"]:
            most_used = max(stats["by_tool"].items(), key=lambda x: x[1]["attempts"])
            stats["most_used_tool"] = most_used[0]
        
        # Find worst tool (highest failure rate)
        if stats["by_tool"]:
            worst_tool = None
            worst_rate = 0.0
            for tool, data in stats["by_tool"].items():
                if data["attempts"] > 0:
                    failure_rate = data["failures"] / data["attempts"]
                    if failure_rate > worst_rate:
                        worst_rate = failure_rate
                        worst_tool = tool
            stats["worst_tool"] = worst_tool or "N/A"
        
        # Convert defaultdict to dict for JSON serialization
        stats["by_tool"] = dict(stats["by_tool"])
        stats["failure_reasons"] = dict(stats["failure_reasons"])
        
        return stats
    
    def format_statistics(self, stats: Dict) -> str:
        """
        Format statistics as markdown string.
        
        Args:
            stats: Statistics dictionary
        
        Returns:
            str: Formatted markdown string
        """
        if "error" in stats:
            return f"# Statistics\n\n{stats['error']}\n"
        
        md = "# Tool Performance Statistics\n\n"
        md += f"## Overview\n\n"
        md += f"- **Total Tests**: {stats['total_tests']}\n"
        md += f"- **Successes**: {stats['successes']}\n"
        md += f"- **Failures**: {stats['failures']}\n"
        md += f"- **Success Rate**: {(stats['successes']/stats['total_tests']*100):.2f}%\n"
        md += f"- **Average Time per Test**: {stats['avg_time_per_test']:.3f} seconds\n\n"
        
        md += f"## Tool Performance\n\n"
        md += f"| Tool Name | Attempts | Successes | Failures | Success Rate | Avg Time |\n"
        md += f"|-----------|----------|-----------|----------|--------------|----------|\n"
        
        for tool, data in stats["by_tool"].items():
            attempts = data["attempts"]
            successes = data["successes"]
            failures = data["failures"]
            success_rate = (successes / attempts * 100) if attempts > 0 else 0
            avg_time = (data["total_time"] / attempts) if attempts > 0 else 0
            
            md += f"| {tool} | {attempts} | {successes} | {failures} | {success_rate:.2f}% | {avg_time:.3f}s |\n"
        
        md += f"\n## Summary\n\n"
        md += f"- **Most Used Tool**: {stats['most_used_tool']}\n"
        md += f"- **Worst Tool (by failure rate)**: {stats['worst_tool']}\n"
        
        if stats["failure_reasons"]:
            md += f"\n## Common Failure Reasons\n\n"
            for reason, count in sorted(stats["failure_reasons"].items(), key=lambda x: x[1], reverse=True)[:10]:
                md += f"- {reason}: {count} occurrences\n"
        
        return md
    
    def save_statistics(self, output_path: str = "Tests/Result_Stats.md"):
        """
        Generate and save statistics to file.
        
        Args:
            output_path: Path to output markdown file
        """
        stats = self.generate_statistics()
        formatted = self.format_statistics(stats)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted)
        
        print(f"Statistics saved to: {output_path}")
        return formatted


if __name__ == "__main__":
    generator = StatisticsGenerator()
    formatted_stats = generator.save_statistics()
    print("\n" + formatted_stats)

