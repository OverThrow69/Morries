import math

import pygame

from config import (
    BASE_LINE_X,
    BOTTOM_HUD_HEIGHT,
    FIELD_BOTTOM,
    FIELD_HEIGHT,
    FIELD_TOP,
    LANE_COUNT,
    LANE_HEIGHT,
    TOP_HUD_HEIGHT,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from visual_theme import (
    BACKGROUND,
    BUILD_TILES,
    EFFECTS,
    ENEMIES,
    ENEMY_DETAILS,
    HUD,
    LANES,
    UNITS,
)


def lighten(color, amount=28):
    return tuple(min(255, value + amount) for value in color)


def darken(color, amount=28):
    return tuple(max(0, value - amount) for value in color)


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.font_small = pygame.font.SysFont("Segoe UI", HUD["font_small"])
        self.font = pygame.font.SysFont("Segoe UI", HUD["font"])
        self.font_bold = pygame.font.SysFont("Segoe UI", HUD["font_bold"], bold=True)
        self.font_title = pygame.font.SysFont("Segoe UI", HUD["font_title"], bold=True)

    def draw(self, state):
        self.screen.fill(BACKGROUND["screen"])
        self.draw_background(state["time"])
        self.draw_lanes()
        self.draw_build_tiles(state)
        self.draw_base()
        self.draw_units(state["units"])
        self.draw_enemies(state["time"])
        self.draw_top_hud(state)
        self.draw_bottom_hud(state)

    def draw_background(self, tick):
        sky = pygame.Rect(0, TOP_HUD_HEIGHT, WINDOW_WIDTH, FIELD_HEIGHT)
        pygame.draw.rect(self.screen, BACKGROUND["sky"], sky)
        pygame.draw.rect(self.screen, BACKGROUND["sky_light"], (0, TOP_HUD_HEIGHT, WINDOW_WIDTH, 120))
        sun_x = 72
        sun_y = TOP_HUD_HEIGHT + 54
        pygame.draw.circle(self.screen, BACKGROUND["sun"], (sun_x, sun_y), 40)
        pygame.draw.circle(self.screen, BACKGROUND["sun_highlight"], (sun_x - 12, sun_y - 12), 15)
        for index in range(EFFECTS["cloud_count"]):
            offset = (tick * (0.15 + index * 0.04)) % (WINDOW_WIDTH + 180)
            x = int((index * 260 + offset) % (WINDOW_WIDTH + 180)) - 90
            y = TOP_HUD_HEIGHT + 28 + (index % 3) * 20
            self.draw_cloud(x, y, EFFECTS["cloud_base_size"] + index * EFFECTS["cloud_size_step"])

    def draw_cloud(self, x, y, size):
        color = BACKGROUND["cloud"]
        pygame.draw.ellipse(self.screen, color, (x - size, y + 8, size * 2, 28))
        pygame.draw.ellipse(self.screen, color, (x - int(size * 0.65), y - 8, size, 32))
        pygame.draw.ellipse(self.screen, color, (x - 4, y - 12, int(size * 1.25), 34))

    def draw_lanes(self):
        for lane in range(LANE_COUNT):
            top = int(FIELD_TOP + lane * LANE_HEIGHT)
            height = int(math.ceil(LANE_HEIGHT))
            base = LANES["even"] if lane % 2 == 0 else LANES["odd"]
            pygame.draw.rect(self.screen, base, (0, top, WINDOW_WIDTH, height))
            pygame.draw.rect(self.screen, darken(base, LANES["separator_darken"]), (0, top + height - 5, WINDOW_WIDTH, 5))
            for x in range(0, WINDOW_WIDTH, 42):
                grass = LANES["grass_dark"] if (x // 42 + lane) % 2 == 0 else LANES["grass_light"]
                pygame.draw.line(self.screen, grass, (x, top + height - 10), (x + 11, top + height - 25), 2)

    def draw_build_tiles(self, state):
        mouse_pos = state["mouse_pos"]
        selected_tile = state["hover_tile"]
        for tile in state["tiles"]:
            rect = tile["rect"]
            occupied = tile["key"] in state["units"]
            hovered = selected_tile == tile["key"]
            shadow = rect.move(0, EFFECTS["shadow_offset"])
            pygame.draw.ellipse(self.screen, BUILD_TILES["shadow"], shadow)
            if occupied:
                fill = BUILD_TILES["occupied"]
                edge = BUILD_TILES["occupied_edge"]
            else:
                fill = BUILD_TILES["empty"]
                edge = BUILD_TILES["empty_edge"]
            pygame.draw.ellipse(self.screen, fill, rect)
            pygame.draw.ellipse(self.screen, edge, rect, 3)
            inner = rect.inflate(-18, -16)
            pygame.draw.ellipse(self.screen, lighten(fill, BUILD_TILES["inner_lighten"]), inner, 2)
            if hovered or rect.collidepoint(mouse_pos):
                pygame.draw.ellipse(
                    self.screen,
                    BUILD_TILES["hover"],
                    rect.inflate(BUILD_TILES["hover_inflate"], BUILD_TILES["hover_inflate"]),
                    BUILD_TILES["hover_width"],
                )

    def draw_base(self):
        pygame.draw.rect(self.screen, BACKGROUND["base_wall"], (BASE_LINE_X - 8, FIELD_TOP + 18, 16, FIELD_HEIGHT - 36), border_radius=6)
        pygame.draw.line(self.screen, BACKGROUND["base_trim"], (BASE_LINE_X + 14, FIELD_TOP + 24), (BASE_LINE_X + 14, FIELD_BOTTOM - 24), 3)
        house_y = FIELD_TOP + 52
        pygame.draw.rect(self.screen, BACKGROUND["house_wall"], (30, house_y + 36, 74, 76), border_radius=4)
        pygame.draw.polygon(self.screen, BACKGROUND["house_roof"], [(22, house_y + 40), (112, house_y + 40), (67, house_y)])
        pygame.draw.rect(self.screen, BACKGROUND["house_door"], (58, house_y + 78, 20, 34), border_radius=3)

    def draw_units(self, units):
        for unit in units.values():
            unit_type = UNITS[unit["unit_index"]]
            x, y = unit["pos"]
            pygame.draw.ellipse(self.screen, EFFECTS["unit_shadow"], (x - 30, y + 22, 60, 16))
            pygame.draw.circle(self.screen, unit_type["color"], (x, y), 22)
            pygame.draw.circle(self.screen, unit_type["accent"], (x, y), 22, 3)
            pygame.draw.circle(self.screen, EFFECTS["unit_skin"], (x, y - 28), 17)
            pygame.draw.rect(self.screen, darken(unit_type["color"], 10), (x - 17, y - 42, 34, 12), border_radius=5)
            pygame.draw.line(self.screen, unit_type["weapon"], (x + 16, y - 3), (x + 46, y - 12), 6)
            label = self.font_small.render(str(unit["unit_index"] + 1), True, HUD["text"])
            self.screen.blit(label, (x - label.get_width() // 2, y - 8))

    def draw_enemies(self, tick):
        for index, enemy_type in enumerate(ENEMIES):
            lane = index % LANE_COUNT
            x = WINDOW_WIDTH - 130 - index * 88
            y = int(FIELD_TOP + lane * LANE_HEIGHT + LANE_HEIGHT / 2)
            bob = math.sin(tick * 0.06 + index) * 3
            radius = enemy_type["radius"]
            pygame.draw.ellipse(self.screen, ENEMY_DETAILS["shadow"], (x - radius, y + 18, radius * 2, 12))
            pygame.draw.circle(self.screen, enemy_type["color"], (x, int(y + bob)), radius)
            pygame.draw.circle(self.screen, enemy_type["accent"], (x, int(y + bob)), radius, 3)
            if enemy_type["name"] == "Runner":
                pygame.draw.line(self.screen, enemy_type["accent"], (x - 26, y + 2), (x - 44, y + 2), 3)
            elif enemy_type["name"] == "Brute":
                pygame.draw.rect(self.screen, darken(enemy_type["color"], ENEMY_DETAILS["brute_plate_darken"]), (x - 22, y - 4, 44, 28), border_radius=8)
            elif enemy_type["name"] == "Armored":
                pygame.draw.rect(self.screen, ENEMY_DETAILS["armored_plate"], (x - 20, y - 18, 40, 16), border_radius=5)
            elif enemy_type["name"] == "Medic":
                pygame.draw.rect(self.screen, ENEMY_DETAILS["medic_cross"], (x - 4, y - 13, 8, 26))
                pygame.draw.rect(self.screen, ENEMY_DETAILS["medic_cross"], (x - 13, y - 4, 26, 8))
            name = self.font_small.render(enemy_type["name"], True, HUD["text"])
            self.screen.blit(name, (x - name.get_width() // 2, y + 34))

    def draw_top_hud(self, state):
        pygame.draw.rect(self.screen, HUD["panel"], (0, 0, WINDOW_WIDTH, TOP_HUD_HEIGHT))
        title = self.font_title.render("Stormwall", True, HUD["selected"])
        subtitle = self.font_small.render("Pygame visual prototype", True, HUD["text_muted"])
        self.screen.blit(title, (24, 15))
        self.screen.blit(subtitle, (26, 51))
        cards = [
            ("Gold", str(state["gold"]), HUD["gold"]),
            ("Lives", str(state["lives"]), HUD["danger"]),
            ("Wave", str(state["wave"]), HUD["accent"]),
            ("Speed", f"{state['speed']}x", HUD["speed"]),
        ]
        x = 250
        for label, value, color in cards:
            self.draw_stat_card(x, 14, label, value, color)
            x += 122
        selected = UNITS[state["selected_unit"]]["name"]
        text = self.font_bold.render(f"Selected: {selected}", True, HUD["text"])
        hint = self.font_small.render("Press F9 to save visual report for ChatGPT", True, HUD["text_muted"])
        self.screen.blit(text, (WINDOW_WIDTH - 360, 20))
        self.screen.blit(hint, (WINDOW_WIDTH - 380, 50))
        report_message = state.get("last_report_message")
        if report_message:
            saved = self.font_small.render(report_message, True, HUD["gold"])
            self.screen.blit(saved, (WINDOW_WIDTH - 560, 68))

    def draw_stat_card(self, x, y, label, value, color):
        rect = pygame.Rect(x, y, HUD["stat_card_width"], HUD["stat_card_height"])
        pygame.draw.rect(self.screen, HUD["panel_light"], rect, border_radius=10)
        pygame.draw.rect(self.screen, darken(color, 65), rect, 2, border_radius=10)
        self.screen.blit(self.font_small.render(label, True, HUD["text_muted"]), (x + 12, y + 8))
        self.screen.blit(self.font_bold.render(value, True, color), (x + 12, y + 28))

    def draw_bottom_hud(self, state):
        top = WINDOW_HEIGHT - BOTTOM_HUD_HEIGHT
        pygame.draw.rect(self.screen, HUD["panel"], (0, top, WINDOW_WIDTH, BOTTOM_HUD_HEIGHT))
        card_width = HUD["unit_card_width"]
        gap = HUD["unit_card_gap"]
        start_x = HUD["unit_card_start_x"]
        for index, unit in enumerate(UNITS):
            rect = pygame.Rect(start_x + index * (card_width + gap), top + 22, card_width, HUD["unit_card_height"])
            selected = index == state["selected_unit"]
            fill = HUD["panel_selected"] if selected else HUD["panel_idle"]
            border = HUD["selected"] if selected else HUD["border"]
            pygame.draw.rect(self.screen, fill, rect, border_radius=12)
            pygame.draw.rect(self.screen, border, rect, 3 if selected else 2, border_radius=12)
            pygame.draw.circle(self.screen, unit["color"], (rect.x + 38, rect.y + 52), 22)
            pygame.draw.circle(self.screen, unit["accent"], (rect.x + 38, rect.y + 52), 22, 3)
            self.screen.blit(self.font_bold.render(f"{index + 1}. {unit['name']}", True, HUD["text"]), (rect.x + 72, rect.y + 22))
            self.screen.blit(self.font_small.render(unit["short"], True, HUD["text_muted"]), (rect.x + 72, rect.y + 51))
            self.screen.blit(self.font_small.render("Lane-wide prototype", True, HUD["accent"]), (rect.x + 72, rect.y + 75))

    def tile_at(self, tiles, pos):
        for tile in tiles:
            if tile["rect"].collidepoint(pos):
                return tile
        return None
