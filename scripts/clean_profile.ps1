Set-Alias vibe vibe-tools

function prompt {
    $currentPath = (Get-Location).Path
    # Check if we're in Assign11 directory (case-insensitive)
    if ($currentPath -match 'Assign11' -or $currentPath -match 'Assign11_Multi-Agent_Graph_Node') {
        return 'C:\Asgn11> '
    } else {
        return 'PS ' + $currentPath + '> '
    }
}
