# Stormwall Pygame Prototype

This folder contains a separate Pygame visual prototype for **Stormwall: Humans vs Zombies**.

It does not replace the current Tkinter game in `main.py`.

## Install Pygame

If Pygame is not installed, run:

```text
py -m pip install pygame
```

## Run

```text
py pygame_version/main_pygame.py
```

## Visual Reports For ChatGPT

While the Pygame prototype is running, press `F9` to save a visual report.

Reports are saved in:

```text
pygame_version/reports/
```

Each report creates two matching files:

```text
screenshot_YYYY-MM-DD_HHMM.png
report_YYYY-MM-DD_HHMM.md
```

Send both the screenshot PNG and the markdown report to ChatGPT when asking for visual feedback.

Automatic reports are disabled by default. To enable them for local testing, set this in `pygame_version/config.py`:

```text
AUTO_VISUAL_REPORT_SECONDS = 30
```

## Phase 1 Scope

- Opens a Pygame window.
- Draws a modern placeholder battlefield.
- Shows 5 lanes and 7 build columns.
- Shows clear build tiles.
- Shows a cleaner HUD for gold, lives, wave, speed, and selected unit.
- Shows placeholder unit cards for Soldier, Hunter, Sniper, Flamethrower, and Engineer.
- Shows placeholder enemy shapes for Walker, Runner, Brute, Armored, and Medic.
- Supports number keys `1` to `5` to change selected unit.
- Supports left click to place a placeholder unit on an empty build tile.
- Supports right click to remove a placed unit.
- Supports `F9` to save a screenshot and visual report.
- Supports Escape and window close to quit.

## Not Included Yet

- Real combat.
- Waves.
- Gold costs.
- Enemy movement.
- Projectiles.
- Sounds.
- Shared gameplay state with the Tkinter version.
- External image assets.
