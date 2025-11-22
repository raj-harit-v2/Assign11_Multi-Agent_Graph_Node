# VS Code Mermaid Diagram Viewer Setup

## Quick Installation Guide

### Method 1: Install via VS Code UI (Recommended)

1. **Open VS Code Extensions**
   - Press `Ctrl+Shift+X` (Windows/Linux) or `Cmd+Shift+X` (Mac)
   - Or click the Extensions icon in the left sidebar

2. **Search for Mermaid Extension**
   - Type: `Markdown Preview Mermaid Support`
   - Author: **Matt Bierner** (most popular and reliable)

3. **Install**
   - Click the **Install** button
   - Wait for installation to complete

4. **Alternative Extension** (if the above doesn't work)
   - Search: `Mermaid Preview`
   - Author: **vstirbu**
   - This provides a dedicated Mermaid preview pane

### Method 2: Install via Command Line

Open VS Code terminal and run:
```bash
code --install-extension bierner.markdown-mermaid
```

Or for Mermaid Preview:
```bash
code --install-extension vstirbu.vscode-mermaid-preview
```

## How to View Your Architecture Diagrams

### Option 1: Using Markdown Preview (Built-in)

1. **Open any `.md` file** with Mermaid diagrams:
   - `Tests/S10_architecture_flow.md`
   - `Tests/S10_conceptual_architecture.md`
   - `Tests/S10_init_arch01.md`

2. **Open Preview**
   - Press `Ctrl+Shift+V` (Windows/Linux) or `Cmd+Shift+V` (Mac)
   - Or right-click the file → **Open Preview**
   - Or click the preview icon in the top-right corner of the editor

3. **View Diagrams**
   - The Mermaid diagrams will render automatically in the preview
   - Scroll through the document to see all diagrams

### Option 2: Using Mermaid Preview Extension

1. **Open a `.md` file** with Mermaid diagrams

2. **Open Mermaid Preview**
   - Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
   - Type: `Mermaid: Preview`
   - Select: **Mermaid: Preview**

3. **View in Side Panel**
   - The diagram will open in a side panel
   - You can view the diagram while editing the code

### Option 3: Split View (Recommended for Editing)

1. **Open the markdown file** in the editor

2. **Open Preview Side-by-Side**
   - Press `Ctrl+K V` (Windows/Linux) or `Cmd+K V` (Mac)
   - This opens preview in a split view
   - Edit on left, preview on right

## Files with Mermaid Diagrams

Your project has these files with architecture diagrams:

1. **`Tests/S10_architecture_flow.md`**
   - 8 detailed technical diagrams
   - System architecture, execution flows, data flows

2. **`Tests/S10_conceptual_architecture.md`**
   - 9 high-level conceptual diagrams
   - System overview, lifecycle, information flow

3. **`Tests/S10_init_arch01.md`**
   - Initial architecture diagrams
   - Component interactions, flows

## Troubleshooting

### Diagrams Not Rendering?

1. **Check Extension is Installed**
   - Go to Extensions (`Ctrl+Shift+X`)
   - Search for "mermaid"
   - Ensure it's enabled (not disabled)

2. **Reload VS Code**
   - Press `Ctrl+Shift+P` → Type: `Reload Window`
   - Or restart VS Code

3. **Check Mermaid Syntax**
   - Ensure code blocks use ` ```mermaid ` (with "mermaid")
   - Not just ` ``` ` or ` ```markdown `

4. **Try Alternative Extension**
   - If "Markdown Preview Mermaid Support" doesn't work
   - Try "Mermaid Preview" by vstirbu

### Preview Not Updating?

- The preview auto-updates as you edit
- If it doesn't, click the refresh icon in the preview pane
- Or close and reopen the preview

## Keyboard Shortcuts Summary

| Action | Windows/Linux | Mac |
|--------|---------------|-----|
| Open Extensions | `Ctrl+Shift+X` | `Cmd+Shift+X` |
| Open Markdown Preview | `Ctrl+Shift+V` | `Cmd+Shift+V` |
| Preview Side-by-Side | `Ctrl+K V` | `Cmd+K V` |
| Command Palette | `Ctrl+Shift+P` | `Cmd+Shift+P` |

## Recommended Workflow

1. **Install Extension**: `Markdown Preview Mermaid Support` by Matt Bierner
2. **Open**: `Tests/S10_architecture_flow.md`
3. **Press**: `Ctrl+K V` (or `Cmd+K V` on Mac)
4. **Result**: Split view with code on left, rendered diagrams on right
5. **Edit**: Make changes to the markdown, see diagrams update in real-time

## Export Diagrams

If you want to export diagrams as images:

1. **Use Mermaid Live** (online)
   - Copy diagram code to https://mermaid.live/
   - Export as PNG/SVG

2. **Use Mermaid CLI** (command line)
   ```bash
   npm install -g @mermaid-js/mermaid-cli
   mmdc -i diagram.mmd -o diagram.png
   ```

3. **Use VS Code Extension**
   - Some Mermaid extensions have export features
   - Check extension documentation

