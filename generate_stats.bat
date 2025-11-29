@echo off
REM Quick script to generate statistics from tool_performance.csv
echo Generating statistics from tool_performance.csv...
python utils/generate_result_stats.py
if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] Statistics generated: data\Result_Stats.md
    echo.
    echo Open data\Result_Stats.md to view the results.
) else (
    echo.
    echo [ERROR] Failed to generate statistics
    pause
)

