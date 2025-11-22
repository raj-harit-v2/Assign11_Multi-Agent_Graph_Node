# Mermaid Extension Setup for VS Code/Cursor

## Quick Setup Guide

### Recommended Extension: Markdown Preview Mermaid Support

**Extension ID**: `bierner.markdown-mermaid`

**Installation**:
1. Press `Ctrl+Shift+X` (Windows/Linux) or `Cmd+Shift+X` (Mac)
2. Search: `Markdown Preview Mermaid Support`
3. Author: **Matt Bierner**
4. Click **Install**

**Usage**:
1. Open any `.md` file with Mermaid diagrams
2. Press `Ctrl+Shift+V` (or `Cmd+Shift+V` on Mac) to open preview
3. Diagrams render automatically in the preview pane

**For Split View**:
- Press `Ctrl+K V` (or `Cmd+K V` on Mac)
- Edit on left, rendered diagrams on right

---

## Alternative Extension: Mermaid Preview

**Extension ID**: `vstirbu.vscode-mermaid-preview`

**Installation**:
1. Press `Ctrl+Shift+X`
2. Search: `Mermaid Preview`
3. Author: **vstirbu**
4. Click **Install**

**Usage**:
1. Open `.md` file with Mermaid diagrams
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
3. Type: `Mermaid: Preview`
4. Select the command
5. View in side panel

---

## Viewing Raw Text Files

For files like `S10_vs_S09_comparison_raw.txt`:

### Option 1: Convert to Markdown
- Copy the Mermaid code from `.txt` file
- Paste into a `.md` file with markdown code blocks:
  ` ```mermaid ` ... ` ``` `
- Use Markdown Preview to view

### Option 2: Use Mermaid Live Editor
- Copy diagram code from `.txt` file
- Go to https://mermaid.live/
- Paste code
- View and edit

### Option 3: Install Mermaid Editor Extension
- Search: `Mermaid Editor`
- Some extensions support viewing `.txt` files directly

---

## Files Ready for Viewing

These files contain Mermaid diagrams in markdown format:
- ✅ `Tests/S10_complete_architecture.md` - Complete architecture diagrams
- ✅ `Tests/S10_vs_S09_comparison_viewable.md` - S9 vs S10 comparison (NEW)
- ✅ `Tests/S10_architecture_flow.md` - Detailed flow diagrams
- ✅ `Tests/S10_conceptual_architecture.md` - Conceptual diagrams
- ✅ `Tests/S10_init_arch01.md` - Initial architecture diagrams

These files contain raw Mermaid code (for Mermaid Live):
- 📄 `Tests/S10_vs_S09_comparison_raw.txt` - Raw comparison diagrams
- 📄 `Tests/S10_mermaid_raw.txt` - Raw architecture diagrams

---

## Troubleshooting

### Diagrams Not Rendering?

1. **Check Extension is Installed**
   - Go to Extensions (`Ctrl+Shift+X`)
   - Search for "mermaid"
   - Ensure it's enabled

2. **Reload VS Code**
   - Press `Ctrl+Shift+P` → Type: `Reload Window`
   - Or restart VS Code

3. **Check File Format**
   - Ensure file is `.md` (markdown)
   - Ensure code blocks use ` ```mermaid ` (not just ` ``` `)

4. **Try Alternative Extension**
   - If one doesn't work, try the other

---

## Keyboard Shortcuts

| Action | Windows/Linux | Mac |
|--------|---------------|-----|
| Open Extensions | `Ctrl+Shift+X` | `Cmd+Shift+X` |
| Open Markdown Preview | `Ctrl+Shift+V` | `Cmd+Shift+V` |
| Preview Side-by-Side | `Ctrl+K V` | `Cmd+K V` |
| Command Palette | `Ctrl+Shift+P` | `Cmd+Shift+P` |

---

## Recommended Workflow

1. **Install**: `Markdown Preview Mermaid Support` by Matt Bierner
2. **Open**: `Tests/S10_vs_S09_comparison_viewable.md`
3. **Press**: `Ctrl+K V` (or `Cmd+K V` on Mac)
4. **Result**: Split view with code on left, rendered diagrams on right
5. **Edit**: Make changes to markdown, see diagrams update in real-time

