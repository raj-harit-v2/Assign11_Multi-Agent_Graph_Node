# PowerShell Extension Terminal Fix

## Issue
VS Code/Cursor shows error: "The PowerShell Extension Terminal has stopped, would you like to restart it?"

## Solutions

### Option 1: Restart via IDE Notification
- Click "Yes" or "Restart" in the notification popup
- The PowerShell extension terminal will restart automatically

### Option 2: Manual Restart via Command Palette
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type: `PowerShell: Restart Extension`
3. Select the command and press Enter

### Option 3: Reload Window
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type: `Developer: Reload Window`
3. Select and press Enter

### Option 4: Restart Terminal Manually
1. Close the current terminal tab
2. Open a new terminal: `Ctrl+`` (backtick) or `Terminal > New Terminal`
3. Select PowerShell as the terminal type

## Verify PowerShell is Working

Run this command to verify:
```powershell
Write-Host "PowerShell is working!" -ForegroundColor Green
$PSVersionTable.PSVersion
```

## Check Profile

Your PowerShell profile should be at:
```
C:\Users\rajuh\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1
```

To verify it loads correctly:
```powershell
. $PROFILE
prompt
```

## Common Causes

1. **Profile Syntax Error**: If your profile has syntax errors, the extension may fail to start
   - Check: `powershell -NoProfile -File $PROFILE`
   - Fix any errors in the profile file

2. **Extension Update**: PowerShell extension may need an update
   - Check: Extensions panel > PowerShell > Update

3. **PowerShell Path Issues**: Extension can't find PowerShell
   - Check: Settings > PowerShell > PowerShell Path
   - Should be: `C:\Program Files\PowerShell\7\pwsh.exe` or similar

## Prevention

- Keep your PowerShell profile syntax error-free
- Regularly update the PowerShell extension
- Use `-NoProfile` flag when testing scripts to avoid profile issues

