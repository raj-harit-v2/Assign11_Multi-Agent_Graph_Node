# PowerShell script to set custom prompt for Assign11
# Usage: . .\scripts\set_prompt.ps1

function prompt {
    "Asgn11> "
}

Write-Host "Prompt set to 'Asgn11> '" -ForegroundColor Green
Write-Host "To make permanent, add this function to your PowerShell profile:" -ForegroundColor Yellow
Write-Host "  notepad `$PROFILE" -ForegroundColor Cyan

