"""
Script to add duplicate queries to query_text.csv with same query_id.
"""

import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict


def add_duplicate_queries(
    data_dir: str = "data",
    query_ids: List[int] = None,
    duplicate_count: int = 5,
    duplicate_interval: int = 5
):
    """
    Add duplicate queries to query_text.csv.
    
    Args:
        data_dir: Directory containing CSV files
        query_ids: List of query IDs to duplicate (if None, duplicates first 5 queries)
        duplicate_count: Number of duplicates per query
        duplicate_interval: Spacing between duplicates (not used in this simple version)
    """
    data_path = Path(data_dir)
    query_file = data_path / "query_text.csv"
    
    if not query_file.exists():
        print(f"File {query_file} does not exist.")
        return
    
    # Read existing queries
    queries = []
    with open(query_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        queries = list(reader)
    
    if not queries:
        print("No queries found in file.")
        return
    
    # Select queries to duplicate
    if query_ids is None:
        # Duplicate first 5 queries
        query_ids = [int(q.get('Query_Id', 0)) for q in queries[:5] if q.get('Query_Id')]
    
    # Find queries to duplicate
    queries_to_dup = [q for q in queries if int(q.get('Query_Id', 0)) in query_ids]
    
    if not queries_to_dup:
        print("No matching queries found.")
        return
    
    # Add duplicates
    new_rows = []
    for query in queries_to_dup:
        query_id = int(query.get('Query_Id', 0))
        query_name = query.get('Query_Name', '')
        query_text = query.get('Query_Text', '')
        
        for i in range(duplicate_count):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_rows.append({
                'Query_Id': query_id,
                'Query_Name': query_name,
                'Query_Text': query_text,
                'Create_Datetime': now,
                'Update_Datetime': now,
                'Active_Flag': '1'
            })
    
    # Append duplicates to file
    with open(query_file, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['Query_Id', 'Query_Name', 'Query_Text', 'Create_Datetime', 'Update_Datetime', 'Active_Flag']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        for row in new_rows:
            writer.writerow(row)
    
    print(f"Added {len(new_rows)} duplicate entries for {len(queries_to_dup)} queries.")


if __name__ == "__main__":
    add_duplicate_queries()

