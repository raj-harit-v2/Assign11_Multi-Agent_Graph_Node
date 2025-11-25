# Complete fix for PowerShell profile prompt function
$profilePath = $PROFILE

if (Test-Path $profilePath) {
    # Read all lines
    $lines = Get-Content $profilePath
    
    # Find and remove all prompt function definitions
    $newLines = @()
    $inPromptFunction = $false
    $braceCount = 0
    
    foreach ($line in $lines) {
        if ($line -match '^\s*function\s+prompt\s*\{') {
            $inPromptFunction = $true
            $braceCount = 0
            continue
        }
        
        if ($inPromptFunction) {
            # Count braces
            $braceCount += ($line.ToCharArray() | Where-Object { $_ -eq '{' }).Count
            $braceCount -= ($line.ToCharArray() | Where-Object { $_ -eq '}' }).Count
            
            if ($braceCount -le 0) {
                $inPromptFunction = $false
            }
            continue
        }
        
        # Keep all other lines
        $newLines += $line
    }
    
    # Add new prompt function at the end
    $newLines += ""
    $newLines += "function prompt {"
    $newLines += "    if (`$PWD.Path -like '*Assign11*') {"
    $newLines += "        'C:\Asgn11> '"
    $newLines += "    } else {"
    $newLines += "        'PS ' + `$PWD.Path + '> '"
    $newLines += "    }"
    $newLines += "}"
    
    # Write back to profile
    $newLines | Set-Content -Path $profilePath
    Write-Host "Profile fixed successfully!" -ForegroundColor Green
    Write-Host "Restart PowerShell or run: . `$PROFILE" -ForegroundColor Yellow
} else {
    Write-Host "Profile does not exist. Creating new one..." -ForegroundColor Yellow
    $profileDir = Split-Path $profilePath -Parent
    if (-not (Test-Path $profileDir)) {
        New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
    }
    
    $newContent = @"
function prompt {
    if (`$PWD.Path -like '*Assign11*') {
        'C:\Asgn11> '
    } else {
        'PS ' + `$PWD.Path + '> '
    }
}
"@
    
    Set-Content -Path $profilePath -Value $newContent
    Write-Host "Profile created successfully!" -ForegroundColor Green
}

Write-Host "`nProfile location: $profilePath" -ForegroundColor Cyan

