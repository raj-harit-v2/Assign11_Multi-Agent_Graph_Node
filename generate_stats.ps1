# Quick PowerShell script to generate statistics from tool_performance.csv
Write-Host "`n=== Generating Statistics ===" -ForegroundColor Green
Write-Host "Reading from: data/tool_performance.csv" -ForegroundColor Cyan
Write-Host "Output: data/Result_Stats.md" -ForegroundColor Cyan
Write-Host ""

python utils/generate_result_stats.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[SUCCESS] Statistics generated: data\Result_Stats.md" -ForegroundColor Green
    Write-Host "`nTo view the results, open: data\Result_Stats.md" -ForegroundColor Yellow
} else {
    Write-Host "`n[ERROR] Failed to generate statistics" -ForegroundColor Red
}

