# Rewrite PowerShell profile with correct prompt function
$profilePath = [Environment]::GetFolderPath('MyDocuments') + '\WindowsPowerShell\Microsoft.PowerShell_profile.ps1'

if (Test-Path $profilePath) {
    # Read all lines
    $allLines = Get-Content $profilePath
    
    # Build new content, skipping broken prompt functions
    $newContent = @()
    $skipUntilBrace = 0
    $inBrokenFunction = $false
    
    foreach ($line in $allLines) {
        # Detect start of broken prompt function
        if ($line -match '^\s*function\s+prompt') {
            $inBrokenFunction = $true
            $skipUntilBrace = 0
            continue
        }
        
        # If in broken function, count braces to find end
        if ($inBrokenFunction) {
            $openBraces = ($line.ToCharArray() | Where-Object { $_ -eq '{' }).Count
            $closeBraces = ($line.ToCharArray() | Where-Object { $_ -eq '}' }).Count
            $skipUntilBrace += $openBraces - $closeBraces
            
            if ($skipUntilBrace -le 0 -and $line -match '\}') {
                $inBrokenFunction = $false
            }
            continue
        }
        
        # Keep all other lines
        $newContent += $line
    }
    
    # Add correct prompt function at the end
    $newContent += ""
    $newContent += "function prompt {"
    $newContent += "    if (`$PWD.Path -like '*Assign11*') {"
    $newContent += "        'C:\Asgn11> '"
    $newContent += "    } else {"
    $newContent += "        'PS ' + `$PWD.Path + '> '"
    $newContent += "    }"
    $newContent += "}"
    
    # Write back
    $newContent | Set-Content -Path $profilePath
    Write-Host "Profile rewritten successfully!" -ForegroundColor Green
    Write-Host "Please restart PowerShell for changes to take effect." -ForegroundColor Yellow
} else {
    Write-Host "Profile not found. Creating new one..." -ForegroundColor Yellow
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
    Write-Host "Profile created!" -ForegroundColor Green
}

Write-Host "`nProfile: $profilePath" -ForegroundColor Cyan

