---
name: cities-skylines
description: Cities Skylines gameplay assistant with vision-guided automation, city planning strategies, and learning system. Use when playing Cities Skylines (城市天际线) to help with building placement, road layout, zoning decisions, budget management, traffic optimization, and game automation. Includes template matching for UI elements, OCR for reading stats, and iterative strategy improvement based on gameplay outcomes.
---

# Cities Skylines Assistant

AI-powered gameplay assistant that learns and improves city-building strategies through vision-based automation and outcome analysis.

## Overview

This skill helps you play Cities Skylines more effectively by:

1. **Vision-based automation** - Using screen-control to interact with the game
2. **Strategic guidance** - Providing city planning advice based on best practices
3. **Iterative learning** - Analyzing outcomes and improving strategies over time
4. **Template library** - Pre-captured UI elements for reliable automation

## Quick Start

### Enhanced Scripts (2026-02-07)

**新增强控制器** - 支持操作序列、智能验证：

- `game_controller.py` - 增强版控制器（序列操作、自动重试、验证机制）
- `state_detector.py` - 游戏状态检测（OCR 读取金钱/人口/日期）

**测试基础功能**:

```bash
# 测试初始化
python scripts/game_controller.py test

# 截图
python scripts/game_controller.py screenshot --output test.png

# 点击测试（需要游戏运行）
python scripts/game_controller.py click --target "0.5,0.5"
```

### First Time Setup

1. **Capture UI templates** - Take screenshots of key UI elements:

   ```bash
   python scripts/capture_templates.py
   ```

   This will guide you through capturing buttons, icons, and UI elements.

2. **Configure game settings** - Tell the assistant about your game:

   ```bash
   python scripts/configure.py
   ```

   Specify resolution, language, DLC installed, etc.

3. **Start playing** - The assistant will observe and help!

### Basic Commands

**Get advice for current situation:**

```
"帮我看看这个路口应该怎么规划"
"Current traffic flow is 65%, what should I improve?"
```

**Automate repetitive tasks:**

```
"帮我铺一条主干道从这里到这里"
"自动规划住宅区"
```

**Analyze city stats:**

```
"帮我看看预算情况"
"分析一下交通拥堵的原因"
```

## Core Features

### 1. Vision-Based Game Interaction

Uses `screen-control` skill to:

- Detect UI elements (buttons, icons, menus)
- Read stats and numbers (OCR)
- Execute game actions (click, drag, build)

**Example workflow:**

```python
# Find and click the "Roads" menu
screen_control.click("roads_icon.png")

# Select highway tool
screen_control.click("highway_tool.png")

# Draw road from point A to B
screen_control.drag("0.3,0.4", "0.7,0.6")
```

### 2. City Planning Strategies

See `references/strategies.md` for detailed guides:

- **Early game** - Efficient starting layouts
- **Road hierarchy** - Arterial, collector, local road patterns
- **Zoning principles** - Mixed-use vs. separated zones
- **Public transport** - Bus, metro, train networks
- **Traffic management** - Intersection design, flow optimization
- **Budget planning** - Revenue vs. expenses balance

### 3. Iterative Learning System

The assistant improves over time by:

1. **Recording actions** - Logs what was built and why
2. **Measuring outcomes** - Tracks city stats (traffic, happiness, budget)
3. **Analyzing results** - Identifies what worked and what didn't
4. **Updating strategies** - Adjusts recommendations based on data

**Learning data stored in:**

- `templates/game_state/` - Screenshots of successful city layouts
- `references/learned_patterns.md` - Documented successful strategies
- `references/mistakes.md` - Common pitfalls to avoid

### 4. Template Library

Pre-captured UI elements for reliable automation:

```
templates/
├── ui_elements/
│   ├── roads_icon.png
│   ├── zones_icon.png
│   ├── services_icon.png
│   └── ...
├── building_icons/
│   ├── residential_low.png
│   ├── commercial.png
│   └── ...
└── game_state/
    ├── successful_layout_01.png
    └── ...
```

**Capture new templates:**

```bash
python scripts/capture_templates.py --category ui_elements --name "new_button"
```

## Automation Capabilities

### Road Building

**Straight roads:**

```python
build_road(start=(0.3, 0.4), end=(0.7, 0.4), road_type="highway")
```

**Grid layout:**

```python
create_grid(
    origin=(0.3, 0.3),
    size=(10, 10),
    spacing=8,
    road_type="two_lane"
)
```

**Curved roads (manual guidance):**
The assistant will guide you through waypoints.

### Zoning

**Zone a rectangular area:**

```python
zone_area(
    corner1=(0.3, 0.3),
    corner2=(0.5, 0.5),
    zone_type="residential_low"
)
```

**Smart zoning (follows roads):**

```python
zone_along_road(
    road_start=(0.3, 0.4),
    road_end=(0.7, 0.4),
    zone_type="commercial",
    density="high"
)
```

### Service Placement

**Find optimal location for service:**

```python
suggest_service_location(
    service="fire_station",
    coverage_needed=[(0.3, 0.3), (0.5, 0.5)]
)
```

**Auto-place service:**

```python
place_service(
    service="elementary_school",
    location="auto"  # or specific coordinates
)
```

## Strategy References

### Road Hierarchy Best Practices

See `references/road_hierarchy.md` for:

- Arterial roads (highways, 6-lane roads)
- Collector roads (4-lane, 2-lane with median)
- Local roads (2-lane residential streets)
- Intersection design patterns

### Zoning Principles

See `references/zoning.md` for:

- Residential density progression
- Commercial strip vs. commercial center
- Industrial placement and logistics
- Mixed-use development patterns

### Traffic Optimization

See `references/traffic.md` for:

- Lane mathematics (capacity calculations)
- Public transport integration
- Traffic flow analysis
- Common bottleneck solutions

### Budget Management

See `references/budget.md` for:

- Income sources and optimization
- Essential vs. optional services
- Loan management
- Tax rate optimization

## Learning from Gameplay

### Recording Sessions

Start a learning session:

```bash
python scripts/start_session.py --goal "Build efficient highway interchange"
```

This will:

1. Take baseline screenshots
2. Record all actions you take (manual or automated)
3. Monitor city stats every 5 minutes
4. Save final state and analysis

### Reviewing Outcomes

After a session:

```bash
python scripts/analyze_session.py --session last
```

This generates:

- Success metrics (traffic improvement, budget impact, etc.)
- Visual comparison (before/after screenshots)
- Strategy recommendations
- Updated knowledge base

### Strategy Evolution

The assistant maintains:

- **Working strategies** - Proven patterns that succeeded
- **Experimental** - New ideas being tested
- **Deprecated** - Approaches that didn't work

Access via: `references/strategy_library.md`

## Configuration

Edit `config.json` to customize:

```json
{
  "game": {
    "resolution": "3840x2160",
    "language": "chinese",
    "dlc": ["after_dark", "snowfall", "natural_disasters"]
  },
  "automation": {
    "speed": "normal",
    "confidence_threshold": 0.85,
    "pause_between_actions": 0.5
  },
  "learning": {
    "record_screenshots": true,
    "track_stats": true,
    "auto_analyze": true
  }
}
```

## Safety & Controls

**Pause automation:**

- Move mouse to top-left corner (pyautogui failsafe)
- Press `Ctrl+C` in terminal
- Say "停下" or "stop"

**Manual override:**

- The assistant will pause and ask before major actions
- You can take over at any time
- All actions are logged and can be undone

**Game state protection:**

- Automatic quicksaves before risky actions
- Non-destructive by default (asks before demolition)
- Budget checks before expensive builds

## Troubleshooting

**UI elements not detected:**

1. Check resolution matches config
2. Re-capture templates at current resolution
3. Adjust confidence threshold in config
4. Try OCR-based detection instead

**Actions executing incorrectly:**

1. Verify game is in focus
2. Check for UI overlays blocking clicks
3. Slow down automation speed
4. Use debug mode: `--debug`

**OCR reading wrong stats:**

1. Ensure clear view of stats panel
2. Check language setting matches game
3. Try different OCR parameters
4. Use template matching for icons instead

## Advanced Usage

### Custom Strategies

Create your own strategy file in `references/custom/`:

```markdown
# My Highway Interchange Pattern

## Context

Use when connecting two highways at different elevations.

## Steps

1. Build elevated highway at +12m
2. Create ramp entry at 45° angle
3. Add merge lane (200m length)
   ...

## Expected Outcome

- Traffic flow: >80%
- No backups at peak hours
```

The assistant will learn to recognize when to suggest this pattern.

### Scripted Builds

Create multi-step build sequences:

```python
# scripts/custom_builds/grid_neighborhood.py
def build_grid_neighborhood(origin, size):
    # 1. Build perimeter road
    build_rectangle_road(origin, size, "four_lane")

    # 2. Create internal grid
    create_grid(origin, size, spacing=8, road_type="two_lane")

    # 3. Zone residential
    zone_interior(origin, size, "residential_low")

    # 4. Place services
    place_service("elementary_school", auto_locate(origin, size))
    place_service("clinic", auto_locate(origin, size))

    return build_summary()
```

### Integration with Other Skills

**Combine with browser for wiki lookup:**

```python
# Look up optimal service coverage
browser.open("https://skylines.paradoxwikis.com/Services")
info = browser.extract("coverage radius")
```

**Use canvas for city visualization:**

```python
# Display city stats overlay
canvas.present("city_stats_dashboard.html")
```

## Examples

See `references/examples.md` for:

- Starting city walkthrough
- Highway interchange tutorial
- Metro network design
- Industrial zone optimization
- Tourism district setup

## Roadmap

Future improvements:

- [ ] Mod compatibility (Traffic Manager, etc.)
- [ ] Multi-city comparison and learning
- [ ] Procedural city generation
- [ ] Real-time traffic prediction
- [ ] Budget optimization AI
- [ ] Asset workshop integration

## Contributing Your Knowledge

Share successful strategies:

```bash
python scripts/contribute.py --strategy "My traffic solution" --description "..."
```

Your patterns will be added to the community knowledge base.

---

**Note:** This skill is in active development. It learns from your gameplay, so the more you use it, the better it becomes at helping you build amazing cities! 🏙️
