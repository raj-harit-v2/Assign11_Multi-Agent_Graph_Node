# PowerShell Script to Move Assign10_Multi-Agent Branch to Raj_Projects_25 Repository
# Run this script in PowerShell

Write-Host "Moving Assign10_Multi-Agent branch to Raj_Projects_25 repository..." -ForegroundColor Cyan

# Navigate to repository
cd C:\A1_School_ai_25\001_My_proj_AI\Assign10_Multi-Agent

# Check current remote
Write-Host "`nCurrent remote configuration:" -ForegroundColor Yellow
git remote -v

# Prompt for GitHub username
$username = Read-Host "`nEnter your GitHub username"

# Remove existing remote if it exists
Write-Host "`nRemoving existing remote (if any)..." -ForegroundColor Yellow
git remote remove origin 2>$null

# Add Raj_Projects_25 as remote
Write-Host "Adding Raj_Projects_25 as remote..." -ForegroundColor Yellow
git remote add origin "https://github.com/$username/Raj_Projects_25.git"

# Verify remote
Write-Host "`nNew remote configuration:" -ForegroundColor Green
git remote -v

# Fetch from remote
Write-Host "`nFetching from remote..." -ForegroundColor Yellow
git fetch origin

# Check current branch
Write-Host "`nCurrent branch:" -ForegroundColor Yellow
git branch

# Push branch to Raj_Projects_25
Write-Host "`nPushing Assign10_Multi-Agent branch to Raj_Projects_25..." -ForegroundColor Yellow
git push -u origin Assign10_Multi-Agent

Write-Host "`n✅ Done! Branch has been pushed to Raj_Projects_25 repository." -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Refresh GitHub Desktop (File → Refresh)" -ForegroundColor White
Write-Host "2. Check branch dropdown - should show Assign10_Multi-Agent with remote tracking" -ForegroundColor White
Write-Host "3. Visit: https://github.com/$username/Raj_Projects_25/branches" -ForegroundColor White

