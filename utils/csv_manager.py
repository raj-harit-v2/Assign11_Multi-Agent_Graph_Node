"""
CSV Manager for Session 10
Handles reading and writing to tool_performance.csv and query_text.csv
"""

import csv
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import json


class CSVManager:
    """Manages CSV file operations for tool performance and query tracking."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.tool_performance_file = self.data_dir / "tool_performance.csv"
        self.query_text_file = self.data_dir / "query_text.csv"
        
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize CSV files with headers if they don't exist."""
        # Initialize tool_performance.csv
        if not self.tool_performance_file.exists():
            headers = [
                "Test_Id", "Query_Id", "Query_Name", "Query_Text", "Query_Answer", "Plan_Used", "Result_Status",
                "Start_Datetime", "End_Datetime", "Elapsed_Time", "Plan_Step_Count",
                "Tool_Name", "Retry_Count", "Error_Message", "Final_State",
                "Api_Call_Type", "Step_Details", "Nodes_Called", "Nodes_Compact", "Node_Count", "Nodes_Exe_Path"
            ]
            self._write_csv_headers(self.tool_performance_file, headers)
        
        # Initialize query_text.csv
        if not self.query_text_file.exists():
            headers = ["Query_Id", "Query_Name", "Query_Text", "Create_Datetime", "Update_Datetime", "Active_Flag"]
            self._write_csv_headers(self.query_text_file, headers)
        else:
            # Migrate existing file if needed
            self._migrate_csv_files()
    
    def _write_csv_headers(self, file_path: Path, headers: List[str]):
        """Write CSV headers to file."""
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
    
    def _migrate_csv_files(self):
        """Migrate existing CSV files to new schema with Query_Name and Bigint Query_Id."""
        # Migrate query_text.csv
        if self.query_text_file.exists():
            try:
                with open(self.query_text_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                
                # Check if migration needed (no Query_Name column)
                if rows and 'Query_Name' not in rows[0]:
                    # Backup old file
                    backup_file = self.query_text_file.with_suffix('.csv.backup')
                    import shutil
                    shutil.copy(self.query_text_file, backup_file)
                    
                    # Write new format
                    with open(self.query_text_file, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(["Query_Id", "Query_Name", "Query_Text", "Create_Datetime", "Update_Datetime", "Active_Flag"])
                        
                        query_id_counter = 1
                        for row in rows:
                            old_query_id = row.get('Query_Id', '')
                            query_text = row.get('Query_Text', '')
                            # Use query_text as Query_Name if it looks like a name, otherwise use default
                            query_name = query_text if len(query_text) < 50 else "Test query for diagnostic"
                            # If Query_Text was actually a name, swap them
                            if query_text == "Test query for diagnostic":
                                query_name = "Test query for diagnostic"
                                query_text = ""  # Will be set when actual query is used
                            
                            writer.writerow([
                                query_id_counter,  # New Bigint ID
                                query_name,
                                query_text,  # Actual query text
                                row.get('Create_Datetime', ''),
                                row.get('Update_Datetime', ''),
                                row.get('Active_Flag', '1')
                            ])
                            query_id_counter += 1
            except Exception as e:
                print(f"Warning: Could not migrate query_text.csv: {e}")
        
        # Migrate tool_performance.csv
        if self.tool_performance_file.exists():
            try:
                with open(self.tool_performance_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                
                # Check if migration needed (no Query_Name column)
                if rows and 'Query_Name' not in rows[0]:
                    # Backup old file
                    backup_file = self.tool_performance_file.with_suffix('.csv.backup')
                    import shutil
                    shutil.copy(self.tool_performance_file, backup_file)
                    
                    # Create mapping from old UUID to new Bigint
                    query_id_map = {}
                    query_id_counter = 1
                    with open(self.query_text_file, 'r', encoding='utf-8') as f:
                        q_reader = csv.DictReader(f)
                        for q_row in q_reader:
                            old_id = q_row.get('Query_Id', '')
                            if old_id and old_id not in query_id_map:
                                query_id_map[old_id] = query_id_counter
                                query_id_counter += 1
                    
                    # Write new format
                    with open(self.tool_performance_file, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            "Test_Id", "Query_Id", "Query_Name", "Query_Text", "Plan_Used", "Result_Status",
                            "Start_Datetime", "End_Datetime", "Elapsed_Time", "Plan_Step_Count",
                            "Tool_Name", "Retry_Count", "Error_Message", "Final_State"
                        ])
                        
                        for row in rows:
                            old_query_id = row.get('Query_Id', '')
                            new_query_id = query_id_map.get(old_query_id, 0)
                            query_text = row.get('Query_Text', '')
                            query_name = "Test query for diagnostic" if query_text == "Test query for diagnostic" else query_text[:50]
                            
                            writer.writerow([
                                row.get('Test_Id', ''),
                                new_query_id,  # New Bigint ID
                                query_name,
                                query_text,  # Actual query text
                                row.get('Plan_Used', ''),
                                row.get('Result_Status', ''),
                                row.get('Start_Datetime', ''),
                                row.get('End_Datetime', ''),
                                row.get('Elapsed_Time', ''),
                                row.get('Plan_Step_Count', ''),
                                row.get('Tool_Name', ''),
                                row.get('Retry_Count', ''),
                                row.get('Error_Message', ''),
                                row.get('Final_State', '')
                            ])
            except Exception as e:
                print(f"Warning: Could not migrate tool_performance.csv: {e}")
    
    def add_query(
        self, 
        query_text: str, 
        query_name: str = "Test query for diagnostic", 
        query_id: Optional[int] = None,
        create_duplicates: bool = False,
        duplicate_count: int = 5,
        duplicate_interval: int = 5
    ) -> int:
        """
        Add a new query to query_text.csv.
        
        Args:
            query_text: The actual query text used
            query_name: The query name/description (default: "Test query for diagnostic")
            query_id: Optional query ID (Bigint). If None, generates sequential ID.
            create_duplicates: If True, create duplicate entries with same query_id
            duplicate_count: Number of duplicates to create
            duplicate_interval: Number of entries between duplicates
        
        Returns:
            int: The query ID (Bigint)
        """
        if query_id is None:
            # Get the next sequential ID
            existing_queries = self.get_all_queries()
            if existing_queries:
                # Find max Query_Id
                max_id = 0
                for q in existing_queries:
                    try:
                        qid = int(q.get('Query_Id', 0))
                        if qid > max_id:
                            max_id = qid
                    except:
                        pass
                query_id = max_id + 1
            else:
                query_id = 1
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Write initial entry
        row = [query_id, query_name, query_text, now, now, "1"]
        
        with open(self.query_text_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)
        
        # Create duplicates if requested
        if create_duplicates:
            import time
            for i in range(duplicate_count):
                # Wait for interval (simulate spacing)
                time.sleep(0.1)  # Small delay for timestamp difference
                dup_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                dup_row = [query_id, query_name, query_text, dup_now, dup_now, "1"]
                
                with open(self.query_text_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(dup_row)
        
        return query_id
    
    def _format_nodes_compact(self, nodes_called: str, step_details: str = "") -> str:
        """
        Format nodes in compact format: A, B, C, CF1, etc.
        
        Args:
            nodes_called: JSON string of node IDs (e.g., ["0", "1", "1F1", "2"])
            step_details: JSON string with variant information
        
        Returns:
            Compact format string (e.g., "0A, 1B, 1F1A, 2A" or simplified "A, B, CF1, A")
        """
        try:
            nodes_list = json.loads(nodes_called) if nodes_called else []
        except:
            nodes_list = []
        
        if not nodes_list:
            return ""
        
        # Parse step_details to get variant information
        variant_map = {}
        node_variants = {}
        if step_details:
            try:
                details = json.loads(step_details)
                # Try to get node_variants mapping first
                node_variants = details.get("node_variants", {})
                # Fallback to variants_tried
                variants_tried = details.get("variants_tried", [])
                # Map node to variant
                for i, variant in enumerate(variants_tried):
                    if i < len(nodes_list):
                        node_id = nodes_list[i]
                        variant_map[node_id] = variant
            except:
                pass
        
        # Format nodes in compact format
        compact_list = []
        for node_id in nodes_list:
            # Check node_variants first
            if node_id in node_variants:
                variant = node_variants[node_id]
                # Extract just the variant letter (e.g., "0A" -> "A", "1F1A" -> "F1A")
                if len(variant) > 1:
                    # Remove numeric prefix, keep variant suffix
                    variant_suffix = variant.lstrip("0123456789")
                    if variant_suffix:
                        compact_list.append(variant_suffix)
                    else:
                        compact_list.append(variant)
                else:
                    compact_list.append(variant)
            elif node_id in variant_map:
                variant = variant_map[node_id]
                # Extract variant suffix
                variant_suffix = variant.lstrip("0123456789")
                if variant_suffix:
                    compact_list.append(variant_suffix)
                else:
                    compact_list.append(variant)
            else:
                # Check if node is a fallback (contains F)
                if "F" in node_id:
                    # Fallback node: extract fallback number (e.g., "1F1" -> "F1")
                    parts = node_id.split("F")
                    if len(parts) > 1:
                        compact_list.append(f"F{parts[1]}")
                    else:
                        compact_list.append(node_id)
                else:
                    # Regular node: default to "A"
                    compact_list.append("A")
        
        return ", ".join(compact_list) if compact_list else ""
    
    def _format_execution_path(self, nodes_called: str) -> str:
        """
        Format execution path as arrow-separated string.
        
        Args:
            nodes_called: JSON string of node IDs (e.g., ["0", "0F1", "0F2", "1", "2", "2F1"])
        
        Returns:
            Execution path string (e.g., "0->0F1->0F2->1->2->2F1")
        """
        try:
            nodes_list = json.loads(nodes_called) if nodes_called else []
        except:
            nodes_list = []
        
        if not nodes_list:
            return ""
        
        return "->".join(nodes_list)
    
    def log_tool_performance(
        self,
        test_id: int,
        query_id: int,
        query_name: str,
        query_text: str,
        query_answer: str,
        plan_used: List[str],
        result_status: str,
        start_datetime: str,
        end_datetime: str,
        elapsed_time: str,
        plan_step_count: int,
        tool_name: str = "",
        retry_count: int = 0,
        error_message: str = "",
        final_state: Dict = None,
            api_call_type: str = "",
            step_details: str = "",
            nodes_called: str = "",
            nodes_exe_path: str = ""
        ):
        """
        Log tool performance to tool_performance.csv.
        
        Args:
            test_id: Test ID number
            query_id: Query ID from query_text.csv (Bigint)
            query_name: Query name/description
            query_text: The actual query text used
            query_answer: The final answer for the query
            plan_used: List of plan steps (will be JSON encoded)
            result_status: "success" or "failure"
            start_datetime: Start timestamp
            end_datetime: End timestamp
            elapsed_time: Elapsed time string
            plan_step_count: Number of steps in plan
            tool_name: Name of tool used
            retry_count: Number of retries
            error_message: Error message if any
            final_state: Final state dictionary (will be JSON encoded)
            api_call_type: Type of API call (e.g., "vector_search", "graph_query", "llm_call", "tool_execution")
            step_details: JSON string of step execution details
            nodes_called: JSON string of node IDs executed in order
            nodes_exe_path: Execution path string (e.g., "0->0F1->0F2->1->2->2F1")
        """
        plan_json = json.dumps(plan_used, ensure_ascii=False)
        final_state_json = json.dumps(final_state or {}, ensure_ascii=False)
        
        # Format nodes in compact format
        nodes_compact = self._format_nodes_compact(nodes_called, step_details)
        
        # Count nodes
        try:
            nodes_list = json.loads(nodes_called) if nodes_called else []
            node_count = len(nodes_list)
        except:
            node_count = 0
        
        # Format execution path (e.g., "0->0F1->0F2->1->2->2F1")
        # Use provided nodes_exe_path or generate from nodes_called
        if nodes_exe_path:
            execution_path = nodes_exe_path
        else:
            execution_path = self._format_execution_path(nodes_called)
        
        row = [
            test_id, query_id, query_name, query_text, query_answer, plan_json, result_status,
            start_datetime, end_datetime, elapsed_time, plan_step_count,
            tool_name, retry_count, error_message, final_state_json,
            api_call_type, step_details, nodes_called, nodes_compact, node_count, execution_path
        ]
        
        with open(self.tool_performance_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)
    
    def get_all_queries(self) -> List[Dict]:
        """Get all queries from query_text.csv."""
        queries = []
        if not self.query_text_file.exists():
            return queries
        
        with open(self.query_text_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                queries.append(row)
        
        return queries
    
    def get_tool_performance(self) -> List[Dict]:
        """Get all tool performance records."""
        records = []
        if not self.tool_performance_file.exists():
            return records
        
        with open(self.tool_performance_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse JSON fields
                try:
                    row['Plan_Used'] = json.loads(row.get('Plan_Used', '[]'))
                except:
                    row['Plan_Used'] = []
                try:
                    row['Final_State'] = json.loads(row.get('Final_State', '{}'))
                except:
                    row['Final_State'] = {}
                records.append(row)
        
        return records

