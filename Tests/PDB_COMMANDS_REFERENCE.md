# PDB Commands Reference

## Basic Navigation Commands

| Command | Description |
|---------|-------------|
| `n` (next) | Execute next line (doesn't enter functions) |
| `s` (step) | Step into function calls |
| `c` (continue) | Continue execution until next breakpoint |
| `q` (quit) | Quit debugger and exit program |
| `u` (up) | Move up one level in stack |
| `d` (down) | Move down one level in stack |
| `w` (where) | Show current stack trace |

## Inspection Commands

| Command | Description |
|---------|-------------|
| `p <expression>` | Print value of expression |
| `pp <expression>` | Pretty print value |
| `l` (list) | Show current code context |
| `ll` (longlist) | Show full source code |
| `a` (args) | Show function arguments |
| `h` (help) | Show help for commands |

## Breakpoint Commands

| Command | Description |
|---------|-------------|
| `b` (break) | Set breakpoint |
| `b <line>` | Set breakpoint at line number |
| `b <file>:<line>` | Set breakpoint in file at line |
| `cl` (clear) | Clear breakpoint |
| `cl <num>` | Clear breakpoint number |
| `tbreak` | Temporary breakpoint (auto-clears) |

## Variable Commands

| Command | Description |
|---------|-------------|
| `p <var>` | Print variable value |
| `pp <var>` | Pretty print variable |
| `whatis <var>` | Show type of variable |
| `!<statement>` | Execute Python statement |

## Common Usage Patterns

### Quick Inspection
```
n, n, p session.state          # Step 2 lines, print state
p session.to_json()            # Print full JSON
pp session.state               # Pretty print state
```

### Step Through Code
```
n                              # Next line
s                              # Step into function
c                              # Continue to next breakpoint
```

### Inspect Variables
```
p session                      # Print session object
p session.state                # Print session state
pp session.to_json()           # Pretty print JSON
a                              # Show function arguments
```

### Set Breakpoints
```
b 150                          # Break at line 150
b agent/test.py:150            # Break in specific file
tbreak 150                     # Temporary breakpoint
```

### Navigation
```
w                              # Show stack trace
u                              # Move up stack
d                              # Move down stack
l                              # Show code context
```

## Quick Reference Card

```
Navigation:  n (next), s (step), c (continue), q (quit)
Inspection:  p (print), pp (pretty print), l (list), a (args)
Breakpoints: b (break), cl (clear), tbreak (temporary)
Stack:       w (where), u (up), d (down)
Help:        h (help), h <command> (help for command)
```

## Example Session

```
(Pdb) n, n, p session.state
> agent/test.py(150)
-> pdb.set_trace()
(Pdb) n
> agent/test.py(152)
-> print("\n" + "=" * 80)
(Pdb) n
> agent/test.py(153)
-> print("FINAL SESSION JSON OUTPUT")
(Pdb) p session.state
{'original_goal_achieved': False, 'final_answer': '...', ...}
(Pdb) c
```

## Tips

- Type commands on one line: `n, n, p var` executes 3 commands
- Use `!` prefix to execute Python code: `!import json; print(json.dumps(session.state))`
- Use `h` for help on any command: `h p` shows help for print command
- Use `ll` to see full source code context

