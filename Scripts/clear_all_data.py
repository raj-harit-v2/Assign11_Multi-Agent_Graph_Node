"""
Script to clear all logs, session files, memory files, and CSV files.
"""

import os
import shutil
from pathlib import Path


def clear_all_data():
    """Clear all logs, sessions, memory, and CSV files."""
    
    print("=" * 70)
    print("CLEARING ALL DATA FILES")
    print("=" * 70)
    
    # 1. Clear CSV files in data/ directory
    print("\n[1/4] Clearing CSV files...")
    data_dir = Path("data")
    if data_dir.exists():
        csv_files = list(data_dir.glob("*.csv"))
        xlsx_files = list(data_dir.glob("*.xlsx"))
        all_data_files = csv_files + xlsx_files
        
        for file in all_data_files:
            try:
                file.unlink()
                print(f"  [DELETED] {file.name}")
            except Exception as e:
                print(f"  [ERROR] Failed to delete {file.name}: {e}")
        
        print(f"  [OK] Deleted {len(all_data_files)} data files")
    else:
        print("  [SKIP] data/ directory does not exist")
    
    # 2. Clear memory/session_logs directory
    print("\n[2/4] Clearing memory/session_logs...")
    memory_logs_dir = Path("memory/session_logs")
    if memory_logs_dir.exists():
        # Count files before deletion
        json_files = list(memory_logs_dir.rglob("*.json"))
        file_count = len(json_files)
        
        # Delete all JSON files
        for json_file in json_files:
            try:
                json_file.unlink()
            except Exception as e:
                print(f"  [ERROR] Failed to delete {json_file}: {e}")
        
        # Remove empty directories
        for dir_path in sorted(memory_logs_dir.rglob("*"), reverse=True):
            if dir_path.is_dir():
                try:
                    dir_path.rmdir()
                except OSError:
                    pass  # Directory not empty or other error
        
        print(f"  [OK] Deleted {file_count} session log files")
    else:
        print("  [SKIP] memory/session_logs directory does not exist")
    
    # 3. Clear any .log files
    print("\n[3/4] Clearing log files...")
    log_files = list(Path(".").rglob("*.log"))
    for log_file in log_files:
        try:
            log_file.unlink()
            print(f"  [DELETED] {log_file}")
        except Exception as e:
            print(f"  [ERROR] Failed to delete {log_file}: {e}")
    
    if not log_files:
        print("  [OK] No log files found")
    else:
        print(f"  [OK] Deleted {len(log_files)} log files")
    
    # 4. Clear any backup files
    print("\n[4/4] Clearing backup files...")
    backup_files = list(Path(".").rglob("*.backup*"))
    for backup_file in backup_files:
        try:
            backup_file.unlink()
            print(f"  [DELETED] {backup_file}")
        except Exception as e:
            print(f"  [ERROR] Failed to delete {backup_file}: {e}")
    
    if not backup_files:
        print("  [OK] No backup files found")
    else:
        print(f"  [OK] Deleted {len(backup_files)} backup files")
    
    print("\n" + "=" * 70)
    print("CLEANUP COMPLETE")
    print("=" * 70)
    print("\nAll data files have been cleared:")
    print("  - CSV files in data/ directory")
    print("  - Session log files in memory/session_logs/")
    print("  - Log files (*.log)")
    print("  - Backup files (*.backup*)")
    print("\nNote: Directory structure is preserved.")


if __name__ == "__main__":
    clear_all_data()





