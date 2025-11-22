"""Test Query_Id in statistics generator"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.statistics_generator import StatisticsGenerator

print("Testing Query_Id extraction...")
gen = StatisticsGenerator()
stats = gen.generate_statistics()

if "error" in stats:
    print(f"Error: {stats['error']}")
else:
    print(f"Total unique queries: {len(stats['by_query_text'])}")
    
    # Check first 5 queries for Query_Id
    sample = list(stats['by_query_text'].items())[:5]
    print("\nSample queries with Query_Id:")
    for query_text, data in sample:
        query_id = data.get("query_id", "N/A")
        query_name = data.get("query_name", "")
        attempts = data.get("attempts", 0)
        print(f"  Query_Id: {query_id} | Query: {query_text[:50]}... | Name: {query_name} | Attempts: {attempts}")
    
    # Check if all have Query_Id
    queries_with_id = sum(1 for d in stats['by_query_text'].values() if d.get("query_id") is not None)
    print(f"\nQueries with Query_Id: {queries_with_id} / {len(stats['by_query_text'])}")

