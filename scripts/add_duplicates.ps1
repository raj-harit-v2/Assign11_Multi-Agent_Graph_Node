# PowerShell script to add duplicate queries to query_text.csv
# Usage: .\scripts\add_duplicates.ps1

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
$pythonScript = Join-Path $projectRoot "utils\add_duplicate_queries.py"

Write-Host "Adding duplicate queries to query_text.csv..."
Write-Host "Running: python $pythonScript"

python $pythonScript

if ($LASTEXITCODE -eq 0) {
    Write-Host "Duplicate queries added successfully!" -ForegroundColor Green
} else {
    Write-Host "Error adding duplicate queries." -ForegroundColor Red
    exit $LASTEXITCODE
}

