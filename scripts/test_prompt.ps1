# Test script to verify prompt works correctly
Write-Host "Testing PowerShell prompt function..." -ForegroundColor Cyan

# Load profile
. $PROFILE

# Test in Assign11 directory
Write-Host "`n1. Testing in Assign11 directory:" -ForegroundColor Yellow
Push-Location "C:\A1_School_ai_25\001_My_proj_AI\Assign11_Multi-Agent_Graph_Node"
$prompt1 = prompt
Write-Host "   Prompt result: '$prompt1'" -ForegroundColor $(if ($prompt1 -eq 'C:\Asgn11> ') { 'Green' } else { 'Red' })
Write-Host "   Expected: 'C:\Asgn11> '" -ForegroundColor Gray

# Test in different directory
Write-Host "`n2. Testing in different directory:" -ForegroundColor Yellow
Push-Location "C:\"
$prompt2 = prompt
Write-Host "   Prompt result: '$prompt2'" -ForegroundColor $(if ($prompt2 -like 'PS C:\*') { 'Green' } else { 'Red' })
Write-Host "   Expected: 'PS C:\> '" -ForegroundColor Gray

# Return to Assign11
Pop-Location
Pop-Location

Write-Host "`nPrompt test complete!" -ForegroundColor Cyan

