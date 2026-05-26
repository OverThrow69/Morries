from datetime import datetime
from pathlib import Path

import pygame

from config import FPS, WINDOW_HEIGHT, WINDOW_WIDTH
from visual_theme import ENEMIES, UNITS


REPORTS_DIR = Path(__file__).resolve().parent / "reports"
VISUAL_THEME_NAME = "Default Pygame Prototype Theme"


def create_visual_report(screen, state):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    stamp = now.strftime("%Y-%m-%d_%H%M")
    screenshot_path = REPORTS_DIR / f"screenshot_{stamp}.png"
    report_path = REPORTS_DIR / f"report_{stamp}.md"

    pygame.image.save(screen, str(screenshot_path))
    report_path.write_text(build_report_text(now, state, screenshot_path), encoding="utf-8")
    return screenshot_path, report_path


def build_report_text(created_at, state, screenshot_path):
    selected_unit = UNITS[state["selected_unit"]]["name"]
    placed_units_count = len(state.get("units", {}))
    enemies = state.get("enemies", [])
    projectiles = state.get("projectiles", [])
    enemy_count = len(enemies) if enemies else len(ENEMIES)

    lines = [
        "# Stormwall Pygame Visual Report",
        "",
        f"Created: {created_at.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Screenshot: `{screenshot_path.name}`",
        "",
        "## Runtime",
        "",
        f"- Screen size: {WINDOW_WIDTH} x {WINDOW_HEIGHT}",
        f"- Target FPS: {FPS}",
        f"- Visual theme: {VISUAL_THEME_NAME}",
        "",
        "## Current State",
        "",
        f"- Gold: {state.get('gold', 'unknown')}",
        f"- Lives: {state.get('lives', 'unknown')}",
        f"- Wave: {state.get('wave', 'unknown')}",
        f"- Speed: {state.get('speed', 'unknown')}x",
        f"- Selected unit: {selected_unit}",
        f"- Placed units count: {placed_units_count}",
        f"- Enemy count: {enemy_count}",
        f"- Projectile count: {len(projectiles)}",
        "",
        "## Unit Types Visible",
        "",
    ]
    lines.extend(f"- {unit['name']}" for unit in UNITS)
    lines.extend([
        "",
        "## Enemy Types Visible",
        "",
    ])
    lines.extend(f"- {enemy['name']}" for enemy in ENEMIES)
    lines.extend([
        "",
        "## Controls",
        "",
        "- Number keys 1-5 select a unit.",
        "- Left click places a placeholder unit on an empty build tile.",
        "- Right click removes a placed unit.",
        "- F9 saves this visual report and screenshot for ChatGPT.",
        "- Escape or the window close button quits.",
        "",
        "## Known Prototype Limitations",
        "",
        "- This Pygame version is a visual prototype shell.",
        "- It does not replace the Tkinter game yet.",
        "- No real waves or combat are implemented yet.",
        "- Enemies are static placeholders.",
        "- Projectiles are not implemented yet.",
        "- Gold costs are displayed as HUD state only; spending is not implemented yet.",
        "- Units and enemies use placeholder shapes instead of sprite assets.",
    ])
    return "\n".join(lines) + "\n"
