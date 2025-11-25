# Create a clean PowerShell profile with correct prompt
$profilePath = "$env:USERPROFILE\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"

# Backup existing profile if it exists
if (Test-Path $profilePath) {
    $backupPath = "$profilePath.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item $profilePath $backupPath
    Write-Host "Backed up existing profile to: $backupPath" -ForegroundColor Yellow
}

# Create clean profile content
# First, try to preserve existing content (except broken prompt functions)
$cleanContent = @()
if (Test-Path $profilePath) {
    $lines = Get-Content $profilePath -ErrorAction SilentlyContinue
    $skipFunction = $false
    $braceLevel = 0
    
    foreach ($line in $lines) {
        if ($line -match '^\s*function\s+prompt') {
            $skipFunction = $true
            $braceLevel = 0
            continue
        }
        
        if ($skipFunction) {
            $openCount = ($line -split '\{').Count - 1
            $closeCount = ($line -split '\}').Count - 1
            $braceLevel += $openCount - $closeCount
            
            if ($braceLevel -le 0 -and $line -match '\}') {
                $skipFunction = $false
            }
            continue
        }
        
        # Skip duplicate else blocks
        if ($line -match '^\s*\}\s+else\s+\{' -and $cleanContent[-1] -match 'else') {
            continue
        }
        
        $cleanContent += $line
    }
} else {
    # New profile - add Set-Alias if it was there before
    $cleanContent += "Set-Alias vibe vibe-tools"
}

# Add correct prompt function
$cleanContent += ""
$cleanContent += "function prompt {"
$cleanContent += "    if (`$PWD.Path -like '*Assign11*') {"
$cleanContent += "        'C:\Asgn11> '"
$cleanContent += "    } else {"
$cleanContent += "        'PS ' + `$PWD.Path + '> '"
$cleanContent += "    }"
$cleanContent += "}"

# Ensure profile directory exists
$profileDir = Split-Path $profilePath -Parent
if (-not (Test-Path $profileDir)) {
    New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
}

# Write clean profile
$cleanContent | Set-Content -Path $profilePath -Encoding UTF8

Write-Host "`nClean profile created successfully!" -ForegroundColor Green
Write-Host "Profile location: $profilePath" -ForegroundColor Cyan
Write-Host "`nPlease close and reopen PowerShell for the prompt to take effect." -ForegroundColor Yellow
Write-Host "Or run: . `$PROFILE" -ForegroundColor Yellow

