"""
Migration script to update CSV files to new schema:
- Query_Id: UUID -> Bigint
- Add Query_Name column
- Query_Text: Contains actual query text
"""

import csv
from pathlib import Path
import shutil

def migrate_csv_files():
    """Migrate CSV files to new schema."""
    data_dir = Path("data")
    query_file = data_dir / "query_text.csv"
    perf_file = data_dir / "tool_performance.csv"
    
    # Backup files
    if query_file.exists():
        backup = query_file.with_suffix('.csv.backup')
        if not backup.exists():
            shutil.copy(query_file, backup)
            print(f"Backed up {query_file} to {backup}")
    
    if perf_file.exists():
        backup = perf_file.with_suffix('.csv.backup')
        if not backup.exists():
            shutil.copy(perf_file, backup)
            print(f"Backed up {perf_file} to {backup}")
    
    # Migrate query_text.csv
    if query_file.exists():
        try:
            with open(query_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            if rows and 'Query_Name' not in rows[0]:
                print("Migrating query_text.csv...")
                # Create new file
                new_rows = []
                query_id_counter = 1
                
                for row in rows:
                    old_query_id = row.get('Query_Id', '')
                    old_query_text = row.get('Query_Text', '')
                    
                    # Determine Query_Name and Query_Text
                    if old_query_text == "Test query for diagnostic":
                        query_name = "Test query for diagnostic"
                        query_text = ""  # Will be filled when actual query is used
                    else:
                        # If it's a short text, use as name, otherwise use default
                        query_name = old_query_text if len(old_query_text) < 50 else "Test query for diagnostic"
                        query_text = old_query_text if len(old_query_text) >= 50 else ""
                    
                    new_rows.append({
                        'Query_Id': query_id_counter,
                        'Query_Name': query_name,
                        'Query_Text': query_text,
                        'Create_Datetime': row.get('Create_Datetime', ''),
                        'Update_Datetime': row.get('Update_Datetime', ''),
                        'Active_Flag': row.get('Active_Flag', '1')
                    })
                    query_id_counter += 1
                
                # Write new file
                with open(query_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['Query_Id', 'Query_Name', 'Query_Text', 'Create_Datetime', 'Update_Datetime', 'Active_Flag'])
                    writer.writeheader()
                    writer.writerows(new_rows)
                
                print(f"Migrated {len(new_rows)} rows in query_text.csv")
        except Exception as e:
            print(f"Error migrating query_text.csv: {e}")
    
    # Migrate tool_performance.csv
    if perf_file.exists():
        try:
            with open(perf_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            if rows and 'Query_Name' not in rows[0]:
                print("Migrating tool_performance.csv...")
                
                # Read query_text.csv to map old IDs to new IDs
                id_map = {}
                if query_file.exists():
                    with open(query_file, 'r', encoding='utf-8') as f:
                        q_reader = csv.DictReader(f)
                        for q_row in q_reader:
                            # New format already has Bigint IDs
                            if 'Query_Id' in q_row:
                                try:
                                    new_id = int(q_row['Query_Id'])
                                    # Map by position (assuming order is preserved)
                                    id_map[new_id] = {
                                        'id': new_id,
                                        'name': q_row.get('Query_Name', 'Test query for diagnostic'),
                                        'text': q_row.get('Query_Text', '')
                                    }
                                except:
                                    pass
                
                # Create new rows
                new_rows = []
                for i, row in enumerate(rows):
                    old_query_id = row.get('Query_Id', '')
                    old_query_text = row.get('Query_Text', '')
                    
                    # Get new ID from map (use index if map not available)
                    new_id = i + 1
                    query_name = "Test query for diagnostic"
                    query_text = old_query_text if old_query_text and old_query_text != "Test query for diagnostic" else ""
                    
                    if id_map:
                        mapped = id_map.get(new_id, {})
                        if mapped:
                            query_name = mapped.get('name', query_name)
                            if not query_text:
                                query_text = mapped.get('text', query_text)
                    
                    new_rows.append({
                        'Test_Id': row.get('Test_Id', ''),
                        'Query_Id': new_id,
                        'Query_Name': query_name,
                        'Query_Text': query_text,
                        'Plan_Used': row.get('Plan_Used', ''),
                        'Result_Status': row.get('Result_Status', ''),
                        'Start_Datetime': row.get('Start_Datetime', ''),
                        'End_Datetime': row.get('End_Datetime', ''),
                        'Elapsed_Time': row.get('Elapsed_Time', ''),
                        'Plan_Step_Count': row.get('Plan_Step_Count', ''),
                        'Tool_Name': row.get('Tool_Name', ''),
                        'Retry_Count': row.get('Retry_Count', ''),
                        'Error_Message': row.get('Error_Message', ''),
                        'Final_State': row.get('Final_State', '')
                    })
                
                # Write new file
                with open(perf_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=[
                        'Test_Id', 'Query_Id', 'Query_Name', 'Query_Text', 'Plan_Used', 'Result_Status',
                        'Start_Datetime', 'End_Datetime', 'Elapsed_Time', 'Plan_Step_Count',
                        'Tool_Name', 'Retry_Count', 'Error_Message', 'Final_State'
                    ])
                    writer.writeheader()
                    writer.writerows(new_rows)
                
                print(f"Migrated {len(new_rows)} rows in tool_performance.csv")
        except Exception as e:
            print(f"Error migrating tool_performance.csv: {e}")

if __name__ == "__main__":
    migrate_csv_files()
    print("Migration complete!")

