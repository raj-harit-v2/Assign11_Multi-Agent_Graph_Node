# PowerShell script to permanently set custom prompt for Assign11
# Run this once to add the prompt function to your PowerShell profile

$profileContent = @"
function prompt {
    if (`$PWD.Path -like "*Assign11*") {
        "C:\Asgn11> "
    } else {
        "PS `$(`$PWD.Path)> "
    }
}
"@

# Check if profile exists
if (Test-Path $PROFILE) {
    $existingContent = Get-Content $PROFILE -Raw
    if ($existingContent -notlike "*Asgn11*") {
        Add-Content -Path $PROFILE -Value "`n$profileContent"
        Write-Host "Prompt function added to PowerShell profile." -ForegroundColor Green
        Write-Host "Restart PowerShell or run: . `$PROFILE" -ForegroundColor Yellow
    } else {
        # Update existing function
        $updatedContent = $existingContent -replace '(?s)function prompt.*?\{.*?\}', $profileContent
        if ($updatedContent -ne $existingContent) {
            Set-Content -Path $PROFILE -Value $updatedContent
            Write-Host "Prompt function updated in PowerShell profile." -ForegroundColor Green
            Write-Host "Restart PowerShell or run: . `$PROFILE" -ForegroundColor Yellow
        } else {
            Write-Host "Prompt function already correct in profile." -ForegroundColor Yellow
        }
    }
} else {
    # Create profile directory if it doesn't exist
    $profileDir = Split-Path $PROFILE -Parent
    if (-not (Test-Path $profileDir)) {
        New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
    }
    Set-Content -Path $PROFILE -Value $profileContent
    Write-Host "PowerShell profile created with Asgn11 prompt." -ForegroundColor Green
    Write-Host "Restart PowerShell or run: . `$PROFILE" -ForegroundColor Yellow
}

Write-Host "`nProfile location: $PROFILE" -ForegroundColor Cyan
