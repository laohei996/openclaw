---
name: screen-control
description: Windows screen control with hybrid approach - OCR text recognition, image template matching, and coordinate clicking. Use for automating desktop/game interactions, clicking UI elements, dragging objects, and controlling applications that require precise mouse/keyboard input. Supports resolution adaptation and intelligent target detection.
---

# Screen Control

A hybrid Windows screen automation skill that combines OCR text recognition, image template matching, and coordinate-based clicking for reliable desktop control.

## Quick Start

The main script `scripts/screen_controller.py` provides a CLI interface for all operations.

**Basic usage:**

```bash
python scripts/screen_controller.py <action> --target <target> [options]
```

### Common Actions

**Click by text (OCR):**

```bash
python scripts/screen_controller.py click --target "确定"
python scripts/screen_controller.py click --target "Start Game"
```

**Click by image template:**

```bash
python scripts/screen_controller.py click --target "button.png"
```

**Click by coordinates:**

```bash
# Absolute coordinates (scaled from 1920x1080)
python scripts/screen_controller.py click --target "960,540"

# Relative coordinates (0-1 range, screen center)
python scripts/screen_controller.py click --target "0.5,0.5"
```

**Drag operation:**

```bash
python scripts/screen_controller.py drag --start "文件" --end "回收站"
python scripts/screen_controller.py drag --start "100,100" --end "500,500"
```

**Screenshot:**

```bash
python scripts/screen_controller.py screenshot --output "screen.png"
python scripts/screen_controller.py screenshot --region "0,0,800,600" --output "region.png"
```

## Resolution Adaptation

The skill automatically handles different screen resolutions:

- **Relative coordinates (0-1)**: Always scaled to current resolution
  - `0.5,0.5` = screen center
  - `0,0` = top-left corner
  - `1,1` = bottom-right corner

- **Absolute coordinates**: Auto-scaled from reference resolution (default 1920x1080)
  - On 2560x1440 screen, `960,540` becomes `1280,720`

Use relative coordinates for best cross-resolution compatibility.

## Hybrid Detection Strategy

The script automatically chooses the best detection method:

1. **Auto mode** (default): Analyzes target type
   - File path with image extension → image matching
   - Numeric with comma → coordinate
   - Otherwise → OCR text search

2. **Manual override**: Use `--method` flag
   - `--method text`: Force OCR
   - `--method image`: Force template matching
   - `--method coord`: Force coordinate

## Installation

First install Python dependencies:

```bash
pip install -r scripts/requirements.txt
```

**For OCR support**, install Tesseract-OCR:

- See `references/tesseract-setup.md` for detailed instructions
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install Chinese language pack (`chi_sim`) for Chinese text recognition

## Advanced Options

**Double-click:**

```bash
python scripts/screen_controller.py click --target "folder" --clicks 2
```

**Right-click:**

```bash
python scripts/screen_controller.py click --target "file" --button right
```

**Search within region:**

```bash
# Only search in top-left 800x600 area
python scripts/screen_controller.py click --target "button" --region "0,0,800,600"
```

**Adjust image matching confidence:**

```bash
python scripts/screen_controller.py click --target "icon.png" --confidence 0.9
```

**Debug mode:**

```bash
python scripts/screen_controller.py click --target "button" --debug
```

## Output Format

All commands output JSON:

```json
{"status": "success", "action": "click", "target": "button"}
{"status": "failed", "action": "click", "target": "button"}
```

Exit code: 0 for success, 1 for failure.

## Examples

See `references/examples.md` for comprehensive usage examples including:

- Game automation scenarios
- Office automation workflows
- Multi-step interactions
- Error handling patterns

## Tips

1. **Safety**: Move mouse to top-left corner to abort (pyautogui.FAILSAFE)
2. **Template images**: Should match actual UI size (take screenshots as templates)
3. **OCR accuracy**: Works best with clear, high-contrast text
4. **Region limiting**: Speeds up search and reduces false positives
5. **Prefer relative coordinates**: More portable across different resolutions

## Integration with OpenClaw

When calling from OpenClaw, use `exec` tool:

```python
# Click by text
exec('python C:\\Users\\admin\\openclaw\\skills\\screen-control\\scripts\\screen_controller.py click --target "确定"')

# Drag with coordinates
exec('python C:\\Users\\admin\\openclaw\\skills\\screen-control\\scripts\\screen_controller.py drag --start "0.2,0.3" --end "0.8,0.7"')

# Take screenshot
exec('python C:\\Users\\admin\\openclaw\\skills\\screen-control\\scripts\\screen_controller.py screenshot --output "C:\\temp\\screen.png"')
```

Parse JSON output to check success status.

## Best Practices for AI Agents

**Auto-cleanup temporary screenshots:**

- Always delete screenshots after reading/using them
- Use temporary paths like `C:\Users\admin\Desktop\temp_*.png`
- Clean up immediately after `read` tool completes

**Example workflow:**

```python
# 1. Take screenshot
exec('python ... screenshot --output C:\\Users\\admin\\Desktop\\temp_screen.png')

# 2. Read and analyze
read('C:\\Users\\admin\\Desktop\\temp_screen.png')

# 3. Clean up immediately (Windows - use Remove-Item for reliability)
exec('powershell -Command "Remove-Item -Path C:\\Users\\admin\\Desktop\\temp_screen.png -Force"')
```

**Alternative cleanup methods:**

```bash
# PowerShell (recommended for Windows)
powershell -Command "Remove-Item -Path 'C:\path\to\file.png' -Force"

# CMD
cmd /c del /f /q "C:\path\to\file.png"

# Direct del (less reliable in PowerShell context)
del C:\path\to\file.png
```

**Naming convention for temp files:**

- Use descriptive prefixes: `temp_`, `screenshot_`, `analysis_`
- Include timestamp or context: `temp_game_menu.png`
- Always track what needs cleanup
