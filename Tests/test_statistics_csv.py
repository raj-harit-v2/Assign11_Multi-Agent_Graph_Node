"""Quick test to verify statistics CSV generation"""
import csv
from pathlib import Path

# Check if CSV exists
csv_path = Path("data/query_statistics.csv")
if csv_path.exists():
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        print(f"[OK] CSV file exists: {csv_path}")
        print(f"[OK] Total unique queries in CSV: {len(rows)}")
        
        # Check if Query_Id column exists
        if rows:
            first_row = rows[0]
            has_query_id = 'Query_Id' in first_row
            print(f"[OK] Query_Id column present: {has_query_id}")
            if has_query_id:
                query_ids = [r.get('Query_Id', '') for r in rows if r.get('Query_Id', '')]
                print(f"[OK] Query_Ids found: {len(query_ids)} (sample: {query_ids[:5]})")
        
        print(f"\nFirst 3 rows:")
        for i, row in enumerate(rows[:3]):
            print(f"\nRow {i+1}:")
            for k, v in row.items():
                display_v = v[:50] + "..." if len(str(v)) > 50 else str(v)
                print(f"  {k}: {display_v}")
else:
    print(f"[ERROR] CSV file not found: {csv_path}")

# Check tool_performance.csv
tool_csv = Path("data/tool_performance.csv")
if tool_csv.exists():
    with open(tool_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        print(f"\n[OK] tool_performance.csv exists")
        print(f"[OK] Total records: {len(rows)}")
        unique_queries = set(r.get('Query_Text', '').strip() for r in rows if r.get('Query_Text', '').strip())
        print(f"[OK] Unique query texts: {len(unique_queries)}")
else:
    print(f"\n[ERROR] tool_performance.csv not found")

