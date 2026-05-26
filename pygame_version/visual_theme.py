# BACKGROUND
BACKGROUND = {
    "screen": (12, 18, 32),
    "sky": (97, 178, 223),
    "sky_light": (181, 226, 246),
    "sun": (253, 224, 71),
    "sun_highlight": (254, 249, 195),
    "cloud": (248, 250, 252),
    "base_wall": (245, 245, 220),
    "base_trim": (202, 138, 4),
    "house_wall": (254, 249, 195),
    "house_roof": (220, 38, 38),
    "house_door": (146, 64, 14),
}

# LANES
LANES = {
    "even": (74, 157, 58),
    "odd": (65, 145, 51),
    "grass_dark": (50, 122, 38),
    "grass_light": (88, 178, 65),
    "separator_darken": 24,
}

# BUILD_TILES
BUILD_TILES = {
    "empty": (74, 173, 74),
    "empty_edge": (28, 126, 58),
    "occupied": (115, 79, 47),
    "occupied_edge": (74, 48, 28),
    "shadow": (32, 88, 42),
    "inner_lighten": 22,
    "hover": (251, 146, 60),
    "hover_width": 3,
    "hover_inflate": 8,
}

# HUD
HUD = {
    "panel": (18, 26, 43),
    "panel_light": (29, 41, 64),
    "panel_selected": (22, 32, 52),
    "panel_idle": (15, 23, 39),
    "border": (45, 61, 88),
    "text": (241, 245, 249),
    "text_muted": (148, 163, 184),
    "gold": (250, 204, 21),
    "danger": (248, 113, 113),
    "accent": (56, 189, 248),
    "selected": (251, 146, 60),
    "speed": (94, 234, 212),
    "stat_card_width": 104,
    "stat_card_height": 58,
    "unit_card_width": 220,
    "unit_card_height": 104,
    "unit_card_gap": 22,
    "unit_card_start_x": 28,
    "font_small": 15,
    "font": 18,
    "font_bold": 20,
    "font_title": 30,
}

# UNITS
UNITS = [
    {
        "name": "Soldier",
        "color": (59, 130, 246),
        "accent": (219, 234, 254),
        "short": "Burst fire",
        "weapon": (226, 232, 240),
    },
    {
        "name": "Hunter",
        "color": (34, 197, 94),
        "accent": (220, 252, 231),
        "short": "Slow shots",
        "weapon": (187, 247, 208),
    },
    {
        "name": "Sniper",
        "color": (168, 85, 247),
        "accent": (243, 232, 255),
        "short": "Piercing",
        "weapon": (226, 232, 240),
    },
    {
        "name": "Flamethrower",
        "color": (249, 115, 22),
        "accent": (255, 237, 213),
        "short": "Area burn",
        "weapon": (253, 186, 116),
    },
    {
        "name": "Engineer",
        "color": (234, 179, 8),
        "accent": (254, 249, 195),
        "short": "Repairs",
        "weapon": (94, 234, 212),
    },
]

# ENEMIES
ENEMIES = [
    {"name": "Walker", "color": (132, 204, 22), "accent": (217, 249, 157), "radius": 19},
    {"name": "Runner", "color": (34, 197, 94), "accent": (187, 247, 208), "radius": 15},
    {"name": "Brute", "color": (77, 124, 15), "accent": (236, 252, 203), "radius": 25},
    {"name": "Armored", "color": (71, 85, 105), "accent": (226, 232, 240), "radius": 22},
    {"name": "Medic", "color": (20, 184, 166), "accent": (204, 251, 241), "radius": 18},
]

ENEMY_DETAILS = {
    "shadow": (35, 94, 47),
    "brute_plate_darken": 25,
    "armored_plate": (148, 163, 184),
    "medic_cross": (240, 253, 250),
}

# PROJECTILES
PROJECTILES = {
    "soldier": (219, 234, 254),
    "hunter": (103, 232, 249),
    "sniper": (233, 213, 255),
    "flamethrower": (251, 146, 60),
    "engineer": (94, 234, 212),
    "trail": (248, 250, 252),
}

# EFFECTS
EFFECTS = {
    "unit_shadow": (30, 70, 36),
    "unit_skin": (253, 230, 138),
    "glow_alpha": 120,
    "shadow_offset": 7,
    "cloud_count": 5,
    "cloud_base_size": 34,
    "cloud_size_step": 5,
}

# UPGRADE_LEVELS
UPGRADE_LEVELS = {
    1: {"outline_width": 2, "weapon_width": 6, "glow_radius": 0, "badge_count": 1},
    2: {"outline_width": 3, "weapon_width": 7, "glow_radius": 6, "badge_count": 2},
    3: {"outline_width": 4, "weapon_width": 8, "glow_radius": 10, "badge_count": 3},
}
