"""
Migration script for Session 11 CSV schema updates.
Adds new columns to tool_performance.csv: Api_Call_Type, Step_Details, Nodes_Called, 
Nodes_Compact, Node_Count, Nodes_Exe_Path
"""

import csv
import shutil
from pathlib import Path
from datetime import datetime


def migrate_tool_performance_csv(data_dir: str = "data"):
    """
    Migrate tool_performance.csv to add new columns.
    
    Args:
        data_dir: Directory containing CSV files
    """
    data_path = Path(data_dir)
    tool_perf_file = data_path / "tool_performance.csv"
    
    if not tool_perf_file.exists():
        print(f"File {tool_perf_file} does not exist. Skipping migration.")
        return
    
    # Backup existing file
    backup_file = tool_perf_file.with_suffix('.csv.backup_v2')
    if not backup_file.exists():
        shutil.copy(tool_perf_file, backup_file)
        print(f"Created backup: {backup_file}")
    
    # Read existing data
    rows = []
    headers = []
    
    with open(tool_perf_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        rows = list(reader)
    
    # Check if migration needed
    new_columns = ["Api_Call_Type", "LLM_Provider", "Step_Details", "Nodes_Called", "Nodes_Compact", "Node_Count", "Nodes_Exe_Path"]
    needs_migration = any(col not in headers for col in new_columns)
    
    if not needs_migration:
        print("Migration not needed - columns already exist.")
        return
    
    # Add new columns to headers
    new_headers = list(headers) + new_columns
    
    # Write migrated data
    with open(tool_perf_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=new_headers)
        writer.writeheader()
        
        for row in rows:
            # Add empty values for new columns
            for col in new_columns:
                row[col] = ""
            writer.writerow(row)
    
    print(f"Migration complete. Added columns: {', '.join(new_columns)}")
    print(f"Migrated {len(rows)} rows.")


if __name__ == "__main__":
    migrate_tool_performance_csv()

