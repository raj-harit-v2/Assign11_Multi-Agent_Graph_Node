"""
Statistics Generator for Session 10
Generates statistics from tool_performance.csv
Creates CSV statistics file and graphical plots
"""

from utils.csv_manager import CSVManager
from pathlib import Path
from collections import defaultdict
from typing import Dict, List
import csv
import json
from datetime import datetime

# Try to import plotting libraries (optional)
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("[WARNING] matplotlib not installed. Plots will be skipped. Install with: pip install matplotlib")


class StatisticsGenerator:
    """Generates statistics from tool performance data."""
    
    def __init__(self):
        self.csv_manager = CSVManager()
    
    def generate_statistics(self) -> Dict:
        """
        Generate comprehensive statistics from tool_performance.csv.
        Includes statistics by tool and by unique query_text.
        
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
            "by_query_text": defaultdict(lambda: {
                "attempts": 0, 
                "successes": 0, 
                "failures": 0, 
                "total_time": 0.0,
                "min_time": float('inf'),
                "max_time": 0.0,
                "query_name": "",
                "query_id": None
            }),
            "avg_time_per_test": 0.0,
            "total_time_all_queries": 0.0,
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
            
            # Get elapsed time
            try:
                elapsed = float(record.get("Elapsed_Time", "0"))
                total_time += elapsed
            except:
                elapsed = 0.0
            
            # Tool statistics
            tool_name = record.get("Tool_Name", "unknown")
            if tool_name:
                stats["by_tool"][tool_name]["attempts"] += 1
                if record.get("Result_Status", "").lower() == "success":
                    stats["by_tool"][tool_name]["successes"] += 1
                else:
                    stats["by_tool"][tool_name]["failures"] += 1
                stats["by_tool"][tool_name]["total_time"] += elapsed
            
            # Query text statistics (per unique query_text)
            query_text = record.get("Query_Text", "").strip()
            query_name = record.get("Query_Name", "").strip()
            query_id = record.get("Query_Id", "")
            if query_text:
                stats["by_query_text"][query_text]["attempts"] += 1
                if record.get("Result_Status", "").lower() == "success":
                    stats["by_query_text"][query_text]["successes"] += 1
                else:
                    stats["by_query_text"][query_text]["failures"] += 1
                stats["by_query_text"][query_text]["total_time"] += elapsed
                if elapsed < stats["by_query_text"][query_text]["min_time"]:
                    stats["by_query_text"][query_text]["min_time"] = elapsed
                if elapsed > stats["by_query_text"][query_text]["max_time"]:
                    stats["by_query_text"][query_text]["max_time"] = elapsed
                if query_name and not stats["by_query_text"][query_text]["query_name"]:
                    stats["by_query_text"][query_text]["query_name"] = query_name
                # Store Query_Id (use first encountered or most common)
                if query_id:
                    try:
                        query_id_int = int(query_id)
                        # If no Query_Id stored yet, or if this is the first record, store it
                        if stats["by_query_text"][query_text]["query_id"] is None:
                            stats["by_query_text"][query_text]["query_id"] = query_id_int
                    except (ValueError, TypeError):
                        pass
        
        # Calculate averages
        if stats["total_tests"] > 0:
            stats["avg_time_per_test"] = total_time / stats["total_tests"]
        stats["total_time_all_queries"] = total_time
        
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
        stats["by_query_text"] = dict(stats["by_query_text"])
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
        
        md += f"\n## Query Text Statistics\n\n"
        md += f"| Query_Id | Query Text (truncated) | Query Name | Attempts | Successes | Failures | Success Rate | Total Time | Avg Time |\n"
        md += f"|----------|------------------------|------------|----------|-----------|----------|--------------|------------|----------|\n"
        
        # Show top 20 queries by attempts
        sorted_queries = sorted(stats["by_query_text"].items(), key=lambda x: x[1]["attempts"], reverse=True)[:20]
        for query_text, data in sorted_queries:
            attempts = data["attempts"]
            successes = data["successes"]
            failures = data["failures"]
            success_rate = (successes / attempts * 100) if attempts > 0 else 0
            total_time = data["total_time"]
            avg_time = (total_time / attempts) if attempts > 0 else 0
            query_id = data["query_id"] if data["query_id"] is not None else "N/A"
            
            display_text = query_text[:40] + "..." if len(query_text) > 40 else query_text
            query_name = data["query_name"][:30] if data["query_name"] else ""
            
            md += f"| {query_id} | {display_text} | {query_name} | {attempts} | {successes} | {failures} | {success_rate:.2f}% | {total_time:.3f}s | {avg_time:.3f}s |\n"
        
        md += f"\n## Summary\n\n"
        md += f"- **Total Time (All Queries)**: {stats.get('total_time_all_queries', 0):.3f} seconds\n"
        md += f"- **Most Used Tool**: {stats['most_used_tool']}\n"
        md += f"- **Worst Tool (by failure rate)**: {stats['worst_tool']}\n"
        md += f"- **Unique Query Texts**: {len(stats.get('by_query_text', {}))}\n"
        
        if stats["failure_reasons"]:
            md += f"\n## Common Failure Reasons\n\n"
            for reason, count in sorted(stats["failure_reasons"].items(), key=lambda x: x[1], reverse=True)[:10]:
                md += f"- {reason}: {count} occurrences\n"
        
        return md
    
    def save_statistics_csv(self, output_path: str = "data/query_statistics.csv"):
        """
        Save statistics per unique query_text to CSV file.
        
        Args:
            output_path: Path to output CSV file
        
        Returns:
            str: Path to saved CSV file
        """
        stats = self.generate_statistics()
        
        if "error" in stats:
            print(f"Error: {stats['error']}")
            return None
        
        output_file = Path(output_path)
        output_file.parent.mkdir(exist_ok=True)
        
        # Write CSV with statistics per unique query_text
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Headers
            writer.writerow([
                "Query_Id", "Query_Text", "Query_Name", "Total_Attempts", "Successes", "Failures", 
                "Success_Rate_Percent", "Total_Time_Seconds", "Avg_Time_Seconds", 
                "Min_Time_Seconds", "Max_Time_Seconds"
            ])
            
            # Write data for each unique query_text
            for query_text, data in stats["by_query_text"].items():
                attempts = data["attempts"]
                successes = data["successes"]
                failures = data["failures"]
                success_rate = (successes / attempts * 100) if attempts > 0 else 0.0
                total_time = data["total_time"]
                avg_time = (total_time / attempts) if attempts > 0 else 0.0
                min_time = data["min_time"] if data["min_time"] != float('inf') else 0.0
                max_time = data["max_time"]
                query_id = data["query_id"] if data["query_id"] is not None else ""
                
                writer.writerow([
                    query_id,  # Query_Id first for easy reference
                    query_text[:200],  # Truncate long queries
                    data["query_name"][:100] if data["query_name"] else "",
                    attempts,
                    successes,
                    failures,
                    f"{success_rate:.2f}",
                    f"{total_time:.3f}",
                    f"{avg_time:.3f}",
                    f"{min_time:.3f}",
                    f"{max_time:.3f}"
                ])
        
        print(f"Query statistics CSV saved to: {output_path}")
        return str(output_file)
    
    def create_plots(self, stats: Dict, output_dir: str = "data/plots"):
        """
        Create graphical plots for statistics.
        
        Args:
            stats: Statistics dictionary
            output_dir: Directory to save plot images
        """
        if not HAS_MATPLOTLIB:
            print("[SKIP] matplotlib not available - skipping plots")
            return
        
        if "error" in stats:
            return
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)
        
        # Plot 1: Success/Failure Rate by Query Text
        if stats["by_query_text"]:
            query_texts = []
            success_rates = []
            failure_rates = []
            
            for query_text, data in list(stats["by_query_text"].items())[:20]:  # Limit to 20 for readability
                attempts = data["attempts"]
                if attempts > 0:
                    query_texts.append(query_text[:30] + "..." if len(query_text) > 30 else query_text)
                    success_rates.append((data["successes"] / attempts) * 100)
                    failure_rates.append((data["failures"] / attempts) * 100)
            
            if query_texts:
                plt.figure(figsize=(14, 8))
                x = range(len(query_texts))
                width = 0.35
                plt.bar([i - width/2 for i in x], success_rates, width, label='Success Rate %', color='green', alpha=0.7)
                plt.bar([i + width/2 for i in x], failure_rates, width, label='Failure Rate %', color='red', alpha=0.7)
                plt.xlabel('Query Text (truncated)')
                plt.ylabel('Rate (%)')
                plt.title('Success/Failure Rate by Unique Query Text')
                plt.xticks(x, query_texts, rotation=45, ha='right')
                plt.legend()
                plt.tight_layout()
                plt.savefig(output_path / "query_success_failure_rate.png", dpi=150, bbox_inches='tight')
                plt.close()
                print(f"Plot saved: {output_path / 'query_success_failure_rate.png'}")
        
        # Plot 2: Execution Time by Query Text
        if stats["by_query_text"]:
            query_texts = []
            avg_times = []
            total_times = []
            
            for query_text, data in list(stats["by_query_text"].items())[:20]:  # Limit to 20
                attempts = data["attempts"]
                if attempts > 0:
                    query_texts.append(query_text[:30] + "..." if len(query_text) > 30 else query_text)
                    avg_times.append(data["total_time"] / attempts)
                    total_times.append(data["total_time"])
            
            if query_texts:
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
                
                # Average time per query
                ax1.bar(range(len(query_texts)), avg_times, color='blue', alpha=0.7)
                ax1.set_xlabel('Query Text (truncated)')
                ax1.set_ylabel('Average Time (seconds)')
                ax1.set_title('Average Execution Time per Query Text')
                ax1.set_xticks(range(len(query_texts)))
                ax1.set_xticklabels(query_texts, rotation=45, ha='right')
                
                # Total time per query
                ax2.bar(range(len(query_texts)), total_times, color='orange', alpha=0.7)
                ax2.set_xlabel('Query Text (truncated)')
                ax2.set_ylabel('Total Time (seconds)')
                ax2.set_title('Total Execution Time per Query Text')
                ax2.set_xticks(range(len(query_texts)))
                ax2.set_xticklabels(query_texts, rotation=45, ha='right')
                
                plt.tight_layout()
                plt.savefig(output_path / "query_execution_time.png", dpi=150, bbox_inches='tight')
                plt.close()
                print(f"Plot saved: {output_path / 'query_execution_time.png'}")
        
        # Plot 3: Overall Success/Failure Distribution
        plt.figure(figsize=(8, 6))
        labels = ['Successes', 'Failures']
        sizes = [stats["successes"], stats["failures"]]
        colors = ['green', 'red']
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.title(f'Overall Success/Failure Distribution\n(Total: {stats["total_tests"]} tests)')
        plt.axis('equal')
        plt.savefig(output_path / "overall_success_failure.png", dpi=150, bbox_inches='tight')
        plt.close()
        print(f"Plot saved: {output_path / 'overall_success_failure.png'}")
    
    def save_statistics(self, output_path: str = "Tests/Result_Stats.md", create_csv: bool = True, create_plots: bool = True):
        """
        Generate and save statistics to file.
        
        Args:
            output_path: Path to output markdown file
            create_csv: Whether to create CSV statistics file
            create_plots: Whether to create graphical plots
        """
        stats = self.generate_statistics()
        formatted = self.format_statistics(stats)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted)
        
        print(f"Statistics saved to: {output_path}")
        
        # Create CSV file with query statistics
        if create_csv:
            csv_path = self.save_statistics_csv()
            if csv_path:
                formatted += f"\n\n## Query Statistics CSV\n\n"
                formatted += f"Detailed statistics per unique query_text saved to: `{csv_path}`\n"
        
        # Create plots
        if create_plots:
            self.create_plots(stats)
            formatted += f"\n\n## Graphical Plots\n\n"
            formatted += f"Plots saved to: `data/plots/`\n"
            formatted += f"- `query_success_failure_rate.png`: Success/Failure rates by query\n"
            formatted += f"- `query_execution_time.png`: Execution time analysis by query\n"
            formatted += f"- `overall_success_failure.png`: Overall distribution pie chart\n"
        
        # Update markdown file with plot references
        if create_plots and HAS_MATPLOTLIB:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(formatted)
        
        return formatted


if __name__ == "__main__":
    generator = StatisticsGenerator()
    formatted_stats = generator.save_statistics()
    print("\n" + formatted_stats)

