# Fix PowerShell profile prompt function
$profilePath = $PROFILE

if (Test-Path $profilePath) {
    $content = Get-Content $profilePath -Raw
    
    # Remove old prompt function definitions
    $content = $content -replace '(?s)function prompt.*?\{.*?\}', ''
    
    # Add new prompt function at the end
    $newPromptFunction = @"

function prompt {
    if (`$PWD.Path -like "*Assign11*") {
        "C:\Asgn11> "
    } else {
        "PS `$(`$PWD.Path)> "
    }
}
"@
    
    # Remove any trailing whitespace and add new function
    $content = $content.TrimEnd() + "`n`n" + $newPromptFunction
    
    Set-Content -Path $profilePath -Value $content -NoNewline
    Write-Host "Profile fixed! Restart PowerShell or run: . `$PROFILE" -ForegroundColor Green
} else {
    Write-Host "Profile does not exist. Run set_prompt_permanent.ps1 first." -ForegroundColor Yellow
}

