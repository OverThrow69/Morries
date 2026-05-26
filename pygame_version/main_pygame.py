import sys

try:
    import pygame
except ImportError:
    print("pygame is not installed. Run: py -m pip install pygame")
    raise SystemExit(1)

from config import (
    AUTO_VISUAL_REPORT_SECONDS,
    COLUMN_COUNT,
    FIELD_TOP,
    FPS,
    LANE_COUNT,
    LANE_HEIGHT,
    TILE_GAP,
    TILE_HEIGHT,
    TILE_START_X,
    TILE_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from reporting import create_visual_report
from renderer import Renderer
from visual_theme import UNITS


def build_tiles():
    tiles = []
    for lane in range(LANE_COUNT):
        y = int(FIELD_TOP + lane * LANE_HEIGHT + LANE_HEIGHT / 2)
        for column in range(COLUMN_COUNT):
            x = TILE_START_X + column * (TILE_WIDTH + TILE_GAP)
            rect = pygame.Rect(0, 0, TILE_WIDTH, TILE_HEIGHT)
            rect.center = (x, y)
            tiles.append({"key": (lane, column), "lane": lane, "column": column, "rect": rect})
    return tiles


def main():
    pygame.init()
    pygame.display.set_caption("Stormwall: Humans vs Zombies - Pygame Prototype")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    renderer = Renderer(screen)
    tiles = build_tiles()
    last_auto_report_ticks = pygame.time.get_ticks()

    state = {
        "gold": 320,
        "lives": 15,
        "wave": 1,
        "speed": 1,
        "selected_unit": 0,
        "tiles": tiles,
        "units": {},
        "mouse_pos": (0, 0),
        "hover_tile": None,
        "time": 0,
    }

    running = True
    while running:
        state["time"] += 1
        state["mouse_pos"] = pygame.mouse.get_pos()
        hover = renderer.tile_at(tiles, state["mouse_pos"])
        state["hover_tile"] = hover["key"] if hover else None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F9:
                    screenshot_path, report_path = create_visual_report(screen, state)
                    state["last_report_message"] = f"Saved {screenshot_path.name} and {report_path.name}"
                elif pygame.K_1 <= event.key <= pygame.K_5:
                    if event.key - pygame.K_1 < len(UNITS):
                        state["selected_unit"] = event.key - pygame.K_1
            elif event.type == pygame.MOUSEBUTTONDOWN:
                tile = renderer.tile_at(tiles, event.pos)
                if not tile:
                    continue
                if event.button == 1 and tile["key"] not in state["units"]:
                    state["units"][tile["key"]] = {
                        "unit_index": state["selected_unit"],
                        "pos": tile["rect"].center,
                    }
                elif event.button == 3 and tile["key"] in state["units"]:
                    del state["units"][tile["key"]]

        renderer.draw(state)
        pygame.display.flip()
        if AUTO_VISUAL_REPORT_SECONDS is not None:
            now_ticks = pygame.time.get_ticks()
            if now_ticks - last_auto_report_ticks >= AUTO_VISUAL_REPORT_SECONDS * 1000:
                screenshot_path, report_path = create_visual_report(screen, state)
                state["last_report_message"] = f"Auto-saved {screenshot_path.name} and {report_path.name}"
                last_auto_report_ticks = now_ticks
        clock.tick(FPS)

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
