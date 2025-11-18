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
                "Test_Id", "Query_Id", "Query_Text", "Plan_Used", "Result_Status",
                "Start_Datetime", "End_Datetime", "Elapsed_Time", "Plan_Step_Count",
                "Tool_Name", "Retry_Count", "Error_Message", "Final_State"
            ]
            self._write_csv_headers(self.tool_performance_file, headers)
        
        # Initialize query_text.csv
        if not self.query_text_file.exists():
            headers = ["Query_Id", "Query_Text", "Create_Datetime", "Update_Datetime", "Active_Flag"]
            self._write_csv_headers(self.query_text_file, headers)
    
    def _write_csv_headers(self, file_path: Path, headers: List[str]):
        """Write CSV headers to file."""
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
    
    def add_query(self, query_text: str, query_id: Optional[str] = None) -> str:
        """
        Add a new query to query_text.csv.
        
        Args:
            query_text: The query text
            query_id: Optional query ID (UUID). If None, generates one.
        
        Returns:
            str: The query ID
        """
        if query_id is None:
            import uuid
            query_id = str(uuid.uuid4())
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        row = [query_id, query_text, now, now, "1"]
        
        with open(self.query_text_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)
        
        return query_id
    
    def log_tool_performance(
        self,
        test_id: int,
        query_id: str,
        query_text: str,
        plan_used: List[str],
        result_status: str,
        start_datetime: str,
        end_datetime: str,
        elapsed_time: str,
        plan_step_count: int,
        tool_name: str = "",
        retry_count: int = 0,
        error_message: str = "",
        final_state: Dict = None
    ):
        """
        Log tool performance to tool_performance.csv.
        
        Args:
            test_id: Test ID number
            query_id: Query ID from query_text.csv
            query_text: The query text
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
        """
        plan_json = json.dumps(plan_used, ensure_ascii=False)
        final_state_json = json.dumps(final_state or {}, ensure_ascii=False)
        
        row = [
            test_id, query_id, query_text, plan_json, result_status,
            start_datetime, end_datetime, elapsed_time, plan_step_count,
            tool_name, retry_count, error_message, final_state_json
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

