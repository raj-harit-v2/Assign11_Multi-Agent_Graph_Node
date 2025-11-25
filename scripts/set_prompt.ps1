# PowerShell script to set custom prompt for Assign11
# Usage: . .\scripts\set_prompt.ps1

function prompt {
    if ($PWD.Path -like "*Assign11*") {
        "C:\Asgn11> "
    } else {
        "PS $($PWD.Path)> "
    }
}

Write-Host "Prompt set to 'C:\Asgn11> ' when in Assign11 directory" -ForegroundColor Green
