import math
import os
import random
import struct
import tkinter as tk
import wave
import winsound


TOP_BAR_HEIGHT = 88
BOTTOM_BAR_HEIGHT = 180
LANE_COUNT = 5
COLUMN_COUNT = 7
MAX_WAVES = 12
FRAMES_PER_SECOND = 60
WAVE_DELAY_SECONDS = 5
SOUND_DIR = os.path.join(os.path.dirname(__file__), "sounds")

UNIT_TYPES = [
    {
        "name": "Soldier",
        "cost": 45,
        "base_damage": 10,
        "base_range": 180,
        "base_fire_rate": 20,
        "projectile_speed": 15,
        "max_hp": 90,
        "color": "#3b82f6",
        "accent": "#dbeafe",
        "upgrade_cost": 22,
        "projectile_color": "#dbeafe",
        "short": "Balanced",
    },
    {
        "name": "Hunter",
        "cost": 58,
        "base_damage": 18,
        "base_range": 230,
        "base_fire_rate": 34,
        "projectile_speed": 17,
        "max_hp": 75,
        "color": "#22c55e",
        "accent": "#dcfce7",
        "upgrade_cost": 28,
        "projectile_color": "#bbf7d0",
        "short": "Fast shots",
    },
    {
        "name": "Sniper",
        "cost": 72,
        "base_damage": 30,
        "base_range": 340,
        "base_fire_rate": 54,
        "projectile_speed": 20,
        "max_hp": 68,
        "color": "#a855f7",
        "accent": "#f3e8ff",
        "upgrade_cost": 36,
        "projectile_color": "#e9d5ff",
        "short": "Long range",
    },
    {
        "name": "Flamethrower",
        "cost": 68,
        "base_damage": 8,
        "base_range": 130,
        "base_fire_rate": 8,
        "projectile_speed": 11,
        "max_hp": 110,
        "color": "#f97316",
        "accent": "#ffedd5",
        "upgrade_cost": 32,
        "projectile_color": "#fdba74",
        "short": "Close burst",
    },
    {
        "name": "Engineer",
        "cost": 82,
        "base_damage": 20,
        "base_range": 200,
        "base_fire_rate": 26,
        "projectile_speed": 14,
        "max_hp": 120,
        "color": "#eab308",
        "accent": "#fef9c3",
        "upgrade_cost": 40,
        "projectile_color": "#fde68a",
        "short": "Heavy armor",
    },
]

ENEMY_TYPES = [
    {
        "name": "Walker",
        "kind": "Zombie",
        "color": "#84cc16",
        "accent": "#d9f99d",
        "base_hp": 56,
        "speed": 1.1,
        "damage": 10,
        "attack_rate": 40,
        "reward": 14,
        "radius": 20,
        "shape": "walker",
    },
    {
        "name": "Runner",
        "kind": "Zombie",
        "color": "#22c55e",
        "accent": "#bbf7d0",
        "base_hp": 42,
        "speed": 1.85,
        "damage": 7,
        "attack_rate": 28,
        "reward": 12,
        "radius": 16,
        "shape": "runner",
    },
    {
        "name": "Brute",
        "kind": "Brute",
        "color": "#4d7c0f",
        "accent": "#ecfccb",
        "base_hp": 92,
        "speed": 0.85,
        "damage": 16,
        "attack_rate": 52,
        "reward": 20,
        "radius": 25,
        "shape": "brute",
    },
]


class ModernLaneDefenseGame:
    def __init__(self, root):
        self.root = root
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        self.field_width = self.screen_width
        self.field_height = self.screen_height - TOP_BAR_HEIGHT - BOTTOM_BAR_HEIGHT
        self.lane_height = self.field_height / LANE_COUNT
        self.base_line_x = 120
        self.tile_start_x = 180
        self.tile_gap = 12
        self.tile_width = 112
        self.tile_height = max(88, int(self.lane_height - 28))
        self.spawn_x = self.screen_width - 120
        self.sky_color = "#93c5fd"

        self.root.title("Stormwall: Humans vs Zombies")
        self.root.geometry(f"{self.screen_width}x{self.screen_height}")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="#07111d")
        self.root.bind("<Escape>", self.exit_fullscreen)
        self.root.bind("<space>", self.force_start_wave)
        for key_index in range(5):
            self.root.bind(str(key_index + 1), lambda event, idx=key_index: self.select_unit(idx))

        self.gold_var = tk.StringVar()
        self.lives_var = tk.StringVar()
        self.wave_var = tk.StringVar()
        self.speed_var = tk.StringVar()
        self.message_var = tk.StringVar()
        self.unit_title_var = tk.StringVar()

        self.speed_options = [1, 2, 3]
        self.speed_index = 0
        self.selected_unit_index = 0
        self.running = True
        self.frame_count = 0
        self.sound_paths = self.ensure_sound_files()
        self.last_sound_frame = -999

        self.unit_cards = []
        self.unit_buttons = []
        self.ambient_clouds = []
        self.progress_fill = None
        self.progress_label = None

        self._build_layout()
        self.reset_game(show_message=False)
        self.show_message("Press 1-5 to choose a unit. The first wave starts in 5 seconds.")
        self.game_loop()

    def exit_fullscreen(self, event=None):
        self.root.attributes("-fullscreen", False)
        self.root.state("zoomed")

    def ensure_sound_files(self):
        os.makedirs(SOUND_DIR, exist_ok=True)
        zombie_sound = os.path.join(SOUND_DIR, "zombie.wav")
        brute_sound = os.path.join(SOUND_DIR, "brute.wav")
        if not os.path.exists(zombie_sound):
            self.write_growl_sound(zombie_sound, base_frequency=170, wobble=42, duration=0.28)
        if not os.path.exists(brute_sound):
            self.write_growl_sound(brute_sound, base_frequency=110, wobble=26, duration=0.4)
        return {"Zombie": zombie_sound, "Brute": brute_sound}

    def write_growl_sound(self, path, base_frequency, wobble, duration):
        sample_rate = 22050
        frames = []
        total_samples = int(sample_rate * duration)
        for index in range(total_samples):
            time_pos = index / sample_rate
            envelope = max(0.0, 1.0 - (time_pos / duration))
            frequency = base_frequency + math.sin(time_pos * 32) * wobble
            sample = (
                math.sin(2 * math.pi * frequency * time_pos)
                + 0.6 * math.sin(2 * math.pi * (frequency * 0.48) * time_pos)
                + 0.2 * math.sin(2 * math.pi * (frequency * 1.9) * time_pos)
            )
            value = int(max(-1.0, min(1.0, sample * 0.45 * envelope)) * 32767)
            frames.append(struct.pack("<h", value))
        with wave.open(path, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(b"".join(frames))

    def play_enemy_sound(self, enemy_kind):
        if self.frame_count - self.last_sound_frame < 14:
            return
        sound_path = self.sound_paths.get(enemy_kind)
        if sound_path:
            self.last_sound_frame = self.frame_count
            winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)

    def _build_layout(self):
        self.top_bar = tk.Frame(self.root, bg="#0f172a", height=TOP_BAR_HEIGHT)
        self.top_bar.pack(side="top", fill="x")
        self.top_bar.pack_propagate(False)

        self.field_canvas = tk.Canvas(
            self.root,
            width=self.field_width,
            height=self.field_height,
            bg="#8ec5ff",
            highlightthickness=0,
        )
        self.field_canvas.pack(side="top", fill="both", expand=True)
        self.field_canvas.bind("<Button-1>", self.on_field_left_click)
        self.field_canvas.bind("<Button-3>", self.on_field_right_click)

        self.bottom_bar = tk.Frame(self.root, bg="#0b1220", height=BOTTOM_BAR_HEIGHT, padx=22, pady=14)
        self.bottom_bar.pack(side="bottom", fill="x")
        self.bottom_bar.pack_propagate(False)

        self._build_top_bar()
        self._build_bottom_bar()

    def _build_top_bar(self):
        left = tk.Frame(self.top_bar, bg="#0f172a")
        left.pack(side="left", fill="y", padx=18, pady=14)

        tk.Label(
            left,
            text="Stormwall",
            bg="#0f172a",
            fg="#fb923c",
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w")
        tk.Label(
            left,
            text="Modern Lane Defense",
            bg="#0f172a",
            fg="#f8fafc",
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w")

        stats = tk.Frame(self.top_bar, bg="#0f172a")
        stats.pack(side="left", padx=16, pady=12)

        self._make_stat_card(stats, "Gold", self.gold_var).pack(side="left", padx=6)
        self._make_stat_card(stats, "Lives", self.lives_var).pack(side="left", padx=6)
        self._make_stat_card(stats, "Wave", self.wave_var).pack(side="left", padx=6)
        self._make_stat_card(stats, "Speed", self.speed_var).pack(side="left", padx=6)

        right = tk.Frame(self.top_bar, bg="#0f172a")
        right.pack(side="right", fill="both", expand=True, padx=22, pady=14)

        top_row = tk.Frame(right, bg="#0f172a")
        top_row.pack(fill="x")

        tk.Label(
            top_row,
            text="Wave Progress",
            bg="#0f172a",
            fg="#cbd5e1",
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left")

        tk.Button(
            top_row,
            text="Restart",
            command=self.reset_game,
            bg="#0f766e",
            fg="white",
            relief="flat",
            activebackground="#115e59",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=4,
        ).pack(side="right", padx=(0, 6))

        tk.Button(
            top_row,
            text="Change Speed",
            command=self.cycle_speed,
            bg="#1d4ed8",
            fg="white",
            relief="flat",
            activebackground="#1e40af",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=4,
        ).pack(side="right")

        self.progress_canvas = tk.Canvas(right, width=420, height=22, bg="#0f172a", highlightthickness=0)
        self.progress_canvas.pack(anchor="e", pady=(8, 4))
        self.progress_canvas.create_rectangle(0, 2, 420, 20, fill="#1e293b", outline="#334155", width=1)
        self.progress_fill = self.progress_canvas.create_rectangle(2, 4, 2, 18, fill="#38bdf8", outline="")
        self.progress_label = self.progress_canvas.create_text(
            210,
            11,
            text="Preparing wave",
            fill="#e2e8f0",
            font=("Segoe UI", 9, "bold"),
        )

        tk.Label(
            right,
            textvariable=self.message_var,
            bg="#0f172a",
            fg="#fde68a",
            font=("Segoe UI", 10, "bold"),
            anchor="e",
            justify="right",
        ).pack(anchor="e")

    def _make_stat_card(self, parent, label, variable):
        card = tk.Frame(parent, bg="#162235", width=96, height=58, highlightthickness=1, highlightbackground="#23324a")
        card.pack_propagate(False)
        tk.Label(card, text=label, bg="#162235", fg="#94a3b8", font=("Segoe UI", 9)).pack(anchor="w", padx=10, pady=(8, 0))
        tk.Label(card, textvariable=variable, bg="#162235", fg="#f8fafc", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=10)
        return card

    def _build_bottom_bar(self):
        header = tk.Frame(self.bottom_bar, bg="#0b1220")
        header.pack(fill="x")

        tk.Label(
            header,
            textvariable=self.unit_title_var,
            bg="#0b1220",
            fg="#f8fafc",
            font=("Segoe UI", 12, "bold"),
        ).pack(side="left")

        tk.Label(
            header,
            text="Keys 1-5 select units. Left-click place/upgrade. Right-click sell.",
            bg="#0b1220",
            fg="#94a3b8",
            font=("Segoe UI", 10),
        ).pack(side="right")

        cards = tk.Frame(self.bottom_bar, bg="#0b1220")
        cards.pack(fill="both", expand=True, pady=(12, 0))

        for index, unit in enumerate(UNIT_TYPES):
            canvas = tk.Canvas(
                cards,
                width=200,
                height=116,
                bg="#111827",
                highlightthickness=2,
                highlightbackground="#1f2937",
            )
            canvas.pack(side="left", padx=8)
            canvas.bind("<Button-1>", lambda event, idx=index: self.select_unit(idx))
            self.unit_cards.append(canvas)

    def reset_game(self, show_message=True):
        self.gold = 320
        self.lives = 15
        self.wave = 1
        self.selected_unit_index = 0
        self.units = []
        self.enemies = []
        self.projectiles = []
        self.particles = []
        self.spawn_queue = []
        self.spawning = False
        self.game_over = False
        self.next_unit_id = 1
        self.countdown_frames = WAVE_DELAY_SECONDS * FRAMES_PER_SECOND
        self.wave_total = 0
        self.wave_spawned = 0
        self.wave_defeated = 0
        self.ambient_clouds = self.make_clouds()
        self.tiles = self.make_tiles()
        self.update_selected_ui()
        self.update_hud()
        if show_message:
            self.show_message("Battle restarted. The first wave starts in 5 seconds.")

    def make_clouds(self):
        clouds = []
        for index in range(5):
            clouds.append({
                "x": random.randint(80, self.field_width - 200),
                "y": random.randint(28, 115),
                "speed": 0.2 + index * 0.05,
                "size": 34 + index * 7,
            })
        return clouds

    def make_tiles(self):
        tiles = []
        for lane in range(LANE_COUNT):
            lane_y = self.lane_center(lane)
            for column in range(COLUMN_COUNT):
                x = self.tile_start_x + column * (self.tile_width + self.tile_gap)
                y = lane_y
                tiles.append({
                    "lane": lane,
                    "column": column,
                    "x": x,
                    "y": y,
                    "unit_id": None,
                })
        return tiles

    def lane_center(self, lane):
        return (lane * self.lane_height) + (self.lane_height / 2)

    def show_message(self, text):
        self.message_var.set(text)

    def cycle_speed(self):
        self.speed_index = (self.speed_index + 1) % len(self.speed_options)
        self.update_hud()
        self.show_message(f"Game speed set to {self.speed_options[self.speed_index]}x.")

    def select_unit(self, index):
        if 0 <= index < len(UNIT_TYPES):
            self.selected_unit_index = index
            self.update_selected_ui()
            self.show_message(f"{UNIT_TYPES[index]['name']} selected.")

    def update_selected_ui(self):
        unit = UNIT_TYPES[self.selected_unit_index]
        self.unit_title_var.set(
            f"Selected: {self.selected_unit_index + 1}. {unit['name']}  |  Cost {unit['cost']}  |  Upgrade {unit['upgrade_cost']}  |  {unit['short']}"
        )
        self.draw_unit_cards()

    def draw_unit_cards(self):
        for index, canvas in enumerate(self.unit_cards):
            unit = UNIT_TYPES[index]
            selected = index == self.selected_unit_index
            canvas.configure(highlightbackground="#fb923c" if selected else "#1f2937")
            canvas.delete("all")
            canvas.create_rectangle(0, 0, 200, 116, fill="#111827", outline="")
            canvas.create_text(14, 14, text=str(index + 1), anchor="w", fill="#e2e8f0", font=("Segoe UI", 12, "bold"))
            canvas.create_text(36, 14, text=unit["name"], anchor="w", fill="#f8fafc", font=("Segoe UI", 11, "bold"))
            canvas.create_text(188, 14, text=f"{unit['cost']}g", anchor="e", fill="#facc15", font=("Segoe UI", 11, "bold"))
            self.draw_unit_portrait(canvas, 18, 32, unit, facing="right")
            canvas.create_text(98, 50, text=unit["short"], anchor="w", fill="#cbd5e1", font=("Segoe UI", 9, "bold"))
            canvas.create_text(98, 70, text=f"Range {unit['base_range']}", anchor="w", fill="#94a3b8", font=("Segoe UI", 9))
            canvas.create_text(98, 88, text=f"Upgrade {unit['upgrade_cost']}", anchor="w", fill="#94a3b8", font=("Segoe UI", 9))
            if selected:
                canvas.create_text(188, 100, text="READY", anchor="e", fill="#fb923c", font=("Segoe UI", 10, "bold"))

    def update_hud(self):
        self.gold_var.set(str(self.gold))
        self.lives_var.set(str(self.lives))
        self.wave_var.set(str(min(self.wave, MAX_WAVES)))
        self.speed_var.set(f"{self.speed_options[self.speed_index]}x")
        self.update_progress_bar()

    def update_progress_bar(self):
        if self.game_over and self.wave > MAX_WAVES:
            progress = 1.0
            label = "All waves survived"
        elif self.spawning or self.wave_total > 0:
            progress = 0 if self.wave_total == 0 else self.wave_defeated / self.wave_total
            label = f"Wave {min(self.wave, MAX_WAVES)}  |  {self.wave_defeated}/{self.wave_total} cleared"
        else:
            progress = 0 if self.wave > MAX_WAVES else 1 - (self.countdown_frames / (WAVE_DELAY_SECONDS * FRAMES_PER_SECOND))
            seconds = max(0, math.ceil(self.countdown_frames / FRAMES_PER_SECOND))
            label = f"Next wave in {seconds}s"
        fill_width = 2 + int(416 * max(0.0, min(1.0, progress)))
        self.progress_canvas.coords(self.progress_fill, 2, 4, fill_width, 18)
        self.progress_canvas.itemconfigure(self.progress_label, text=label)

    def force_start_wave(self, event=None):
        if not self.spawning and not self.game_over and self.wave <= MAX_WAVES:
            self.countdown_frames = 0
            self.update_hud()
            self.show_message("Wave starting now.")

    def create_wave(self):
        self.spawn_queue = []
        self.wave_total = 4 + (self.wave * 2)
        self.wave_spawned = 0
        self.wave_defeated = 0
        for index in range(self.wave_total):
            lane = random.randint(0, LANE_COUNT - 1)
            enemy_blueprint = self.pick_enemy_type(index)
            enemy = self.create_enemy(enemy_blueprint, lane)
            delay_gap = 42 if self.wave <= 2 else 34 if self.wave <= 4 else 28
            self.spawn_queue.append({"delay": index * delay_gap, "enemy": enemy})
        self.spawning = True
        self.update_hud()
        self.show_message(f"Wave {self.wave} has started. Zombies are entering from the right.")

    def pick_enemy_type(self, index):
        if self.wave >= 5 and index % 5 == 0:
            return ENEMY_TYPES[2]
        if self.wave >= 3 and index % 3 == 0:
            return ENEMY_TYPES[1]
        return ENEMY_TYPES[0]

    def create_enemy(self, blueprint, lane):
        hp_scale = 1 + ((self.wave - 1) * 0.16)
        speed_scale = 1 + ((self.wave - 1) * 0.04)
        radius = blueprint["radius"]
        return {
            "lane": lane,
            "x": self.spawn_x + random.randint(0, 80),
            "y": self.lane_center(lane),
            "radius": radius,
            "shape": blueprint["shape"],
            "color": blueprint["color"],
            "accent": blueprint["accent"],
            "name": blueprint["name"],
            "kind": blueprint["kind"],
            "hp": int(blueprint["base_hp"] * hp_scale),
            "max_hp": int(blueprint["base_hp"] * hp_scale),
            "speed": blueprint["speed"] * speed_scale,
            "damage": blueprint["damage"] + (self.wave // 3),
            "attack_rate": max(14, blueprint["attack_rate"] - self.wave),
            "attack_cooldown": 0,
            "reward": blueprint["reward"] + self.wave,
            "bob": random.random() * math.pi * 2,
        }

    def on_field_left_click(self, event):
        if self.game_over:
            return
        tile = self.get_tile_at(event.x, event.y)
        if not tile:
            return
        if tile["unit_id"] is None:
            self.place_unit(tile)
        else:
            self.upgrade_unit(tile["unit_id"])

    def on_field_right_click(self, event):
        if self.game_over:
            return
        tile = self.get_tile_at(event.x, event.y)
        if tile and tile["unit_id"] is not None:
            self.sell_unit(tile)

    def get_tile_at(self, x, y):
        for tile in self.tiles:
            left = tile["x"] - (self.tile_width / 2)
            right = tile["x"] + (self.tile_width / 2)
            top = tile["y"] - (self.tile_height / 2)
            bottom = tile["y"] + (self.tile_height / 2)
            if left <= x <= right and top <= y <= bottom:
                return tile
        return None

    def place_unit(self, tile):
        unit_type = UNIT_TYPES[self.selected_unit_index]
        if self.gold < unit_type["cost"]:
            self.show_message("Not enough gold to place that unit.")
            return

        unit_id = f"unit-{self.next_unit_id}"
        self.next_unit_id += 1
        self.gold -= unit_type["cost"]
        tile["unit_id"] = unit_id
        self.units.append({
            "id": unit_id,
            "lane": tile["lane"],
            "column": tile["column"],
            "x": tile["x"] - 4,
            "y": tile["y"] + 10,
            "unit_index": self.selected_unit_index,
            "name": unit_type["name"],
            "level": 1,
            "hp": unit_type["max_hp"],
            "max_hp": unit_type["max_hp"],
            "damage": unit_type["base_damage"],
            "range": unit_type["base_range"],
            "fire_rate": unit_type["base_fire_rate"],
            "projectile_speed": unit_type["projectile_speed"],
            "cooldown": random.randint(0, 8),
            "color": unit_type["color"],
            "accent": unit_type["accent"],
            "projectile_color": unit_type["projectile_color"],
            "upgrade_cost": unit_type["upgrade_cost"],
            "total_spent": unit_type["cost"],
            "shadow": 26,
        })
        self.update_hud()
        self.show_message(f"{unit_type['name']} deployed in lane {tile['lane'] + 1}.")

    def upgrade_unit(self, unit_id):
        unit = self.get_unit(unit_id)
        if not unit:
            return
        if unit["level"] >= 3:
            self.show_message(f"{unit['name']} is already max level.")
            return
        if self.gold < unit["upgrade_cost"]:
            self.show_message(f"You need {unit['upgrade_cost']} gold to upgrade {unit['name']}.")
            return

        self.gold -= unit["upgrade_cost"]
        unit["total_spent"] += unit["upgrade_cost"]
        unit["level"] += 1
        unit["damage"] += 7
        unit["range"] += 18
        unit["max_hp"] += 20
        unit["hp"] = min(unit["max_hp"], unit["hp"] + 15)
        unit["fire_rate"] = max(6, unit["fire_rate"] - 3)
        if unit["level"] >= 3:
            unit["upgrade_cost"] = 0
        else:
            unit["upgrade_cost"] += 15
        self.update_hud()
        self.show_message(f"{unit['name']} upgraded to level {unit['level']}.")

    def sell_unit(self, tile):
        unit = self.get_unit(tile["unit_id"])
        if not unit:
            return
        refund = unit["total_spent"] // 2
        self.gold += refund
        self.units = [item for item in self.units if item["id"] != tile["unit_id"]]
        self.projectiles = [item for item in self.projectiles if item["source_id"] != tile["unit_id"]]
        tile["unit_id"] = None
        self.update_hud()
        self.show_message(f"{unit['name']} sold for {refund} gold.")

    def get_unit(self, unit_id):
        for unit in self.units:
            if unit["id"] == unit_id:
                return unit
        return None

    def get_unit_by_lane_column(self, lane, column):
        for unit in self.units:
            if unit["lane"] == lane and unit["column"] == column:
                return unit
        return None

    def game_loop(self):
        if self.running:
            self.frame_count += 1
            steps = self.speed_options[self.speed_index]
            for _ in range(steps):
                if not self.game_over:
                    self.update_world()
            self.draw()
            self.root.after(16, self.game_loop)

    def update_world(self):
        self.update_countdown()
        self.update_spawning()
        self.update_units()
        self.update_enemies()
        self.update_projectiles()
        self.update_particles()
        self.update_clouds()
        self.check_wave_end()

    def update_countdown(self):
        if self.spawning or self.wave > MAX_WAVES:
            return
        if self.countdown_frames > 0:
            self.countdown_frames -= 1
            if self.countdown_frames % FRAMES_PER_SECOND == 0:
                self.update_hud()
            return
        self.create_wave()

    def update_spawning(self):
        if not self.spawning:
            return
        ready = []
        for item in self.spawn_queue:
            item["delay"] -= 1
            if item["delay"] <= 0:
                ready.append(item)
        for item in ready:
            self.spawn_queue.remove(item)
            self.enemies.append(item["enemy"])
            self.wave_spawned += 1
            self.play_enemy_sound(item["enemy"]["kind"])
        if ready:
            self.update_hud()

    def update_units(self):
        for unit in list(self.units):
            if unit["cooldown"] > 0:
                unit["cooldown"] -= 1
                continue
            target = self.find_target_for_unit(unit)
            if not target:
                continue
            unit["cooldown"] = unit["fire_rate"]
            self.projectiles.append({
                "x": unit["x"] + 26,
                "y": unit["y"] - 20,
                "lane": unit["lane"],
                "target": target,
                "speed": unit["projectile_speed"],
                "damage": unit["damage"],
                "color": unit["projectile_color"],
                "source_id": unit["id"],
            })

    def find_target_for_unit(self, unit):
        chosen = None
        for enemy in self.enemies:
            if enemy["lane"] != unit["lane"]:
                continue
            distance = enemy["x"] - unit["x"]
            if distance < 0 or distance > unit["range"]:
                continue
            if chosen is None or enemy["x"] < chosen["x"]:
                chosen = enemy
        return chosen

    def update_enemies(self):
        remaining = []
        for enemy in self.enemies:
            if enemy["attack_cooldown"] > 0:
                enemy["attack_cooldown"] -= 1

            blocker = self.find_blocking_unit(enemy)
            if blocker:
                if enemy["attack_cooldown"] <= 0:
                    blocker["hp"] -= enemy["damage"]
                    enemy["attack_cooldown"] = enemy["attack_rate"]
                    self.add_hit_particles(blocker["x"] + 10, blocker["y"] - 12, blocker["accent"])
                    if blocker["hp"] <= 0:
                        self.remove_unit(blocker["id"])
                remaining.append(enemy)
                continue

            enemy["x"] -= enemy["speed"]
            enemy["bob"] += 0.08
            if enemy["x"] <= self.base_line_x:
                self.lives -= 1
                self.add_hit_particles(self.base_line_x, enemy["y"] - 8, "#fca5a5")
                if self.lives <= 0:
                    self.lives = 0
                    self.game_over = True
                    self.show_message("The zombies broke through the village. Game over.")
                self.update_hud()
                continue
            remaining.append(enemy)
        self.enemies = remaining

    def find_blocking_unit(self, enemy):
        blockers = []
        for unit in self.units:
            if unit["lane"] != enemy["lane"]:
                continue
            if 0 <= enemy["x"] - unit["x"] <= 58:
                blockers.append(unit)
        if not blockers:
            return None
        return max(blockers, key=lambda item: item["x"])

    def remove_unit(self, unit_id):
        self.units = [unit for unit in self.units if unit["id"] != unit_id]
        for tile in self.tiles:
            if tile["unit_id"] == unit_id:
                tile["unit_id"] = None
        self.projectiles = [item for item in self.projectiles if item["source_id"] != unit_id]

    def update_projectiles(self):
        active = []
        for projectile in self.projectiles:
            target = projectile["target"]
            if target not in self.enemies or target["hp"] <= 0:
                continue
            dx = target["x"] - projectile["x"]
            dy = (target["y"] - 18) - projectile["y"]
            distance = math.hypot(dx, dy)
            if distance <= projectile["speed"] or distance == 0:
                target["hp"] -= projectile["damage"]
                self.add_hit_particles(projectile["x"], projectile["y"], projectile["color"])
                if target["hp"] <= 0:
                    self.gold += target["reward"]
                    self.wave_defeated += 1
                    self.add_death_particles(target["x"], target["y"], target["accent"])
                    self.enemies = [enemy for enemy in self.enemies if enemy is not target]
                    self.update_hud()
                continue
            projectile["x"] += (dx / distance) * projectile["speed"]
            projectile["y"] += (dy / distance) * projectile["speed"]
            active.append(projectile)
        self.projectiles = active

    def add_hit_particles(self, x, y, color):
        for _ in range(4):
            self.particles.append({
                "x": x,
                "y": y,
                "vx": random.uniform(-1.8, 1.8),
                "vy": random.uniform(-1.4, 1.4),
                "life": 16,
                "color": color,
                "size": random.randint(3, 5),
            })

    def add_death_particles(self, x, y, color):
        for _ in range(9):
            self.particles.append({
                "x": x,
                "y": y - 16,
                "vx": random.uniform(-2.4, 2.4),
                "vy": random.uniform(-2.8, 0.3),
                "life": 24,
                "color": color,
                "size": random.randint(4, 7),
            })

    def update_particles(self):
        active = []
        for particle in self.particles:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["vy"] += 0.06
            particle["life"] -= 1
            if particle["life"] > 0:
                active.append(particle)
        self.particles = active

    def update_clouds(self):
        for cloud in self.ambient_clouds:
            cloud["x"] += cloud["speed"]
            if cloud["x"] - cloud["size"] > self.field_width + 50:
                cloud["x"] = -80

    def check_wave_end(self):
        if self.wave > MAX_WAVES:
            if not self.spawning and not self.enemies and not self.game_over:
                self.game_over = True
                self.show_message("You survived every wave. The village is safe.")
                self.update_hud()
            return
        if self.spawning and not self.spawn_queue and not self.enemies:
            self.spawning = False
            self.wave += 1
            if self.wave <= MAX_WAVES:
                self.countdown_frames = WAVE_DELAY_SECONDS * FRAMES_PER_SECOND
                self.show_message("Wave cleared. The next wave starts automatically in 5 seconds.")
            self.update_hud()

    def draw(self):
        self.field_canvas.delete("all")
        self.draw_background()
        self.draw_lanes()
        self.draw_tiles()
        self.draw_props()
        self.draw_units()
        self.draw_enemies()
        self.draw_projectiles()
        self.draw_particles()
        self.draw_front_fx()
        self.update_progress_bar()
        if self.game_over:
            self.draw_game_over_overlay()

    def draw_background(self):
        self.field_canvas.create_rectangle(0, 0, self.field_width, self.field_height, fill="#a8d8f0", outline="")
        self.field_canvas.create_rectangle(0, 0, self.field_width, 120, fill="#c9eeff", outline="")
        sun_rotate = (self.frame_count * 0.5) % 360
        for ray in range(8):
            angle = math.radians((ray * 45) + sun_rotate)
            self.field_canvas.create_line(
                72 + math.cos(angle) * 44, 54 + math.sin(angle) * 44,
                72 + math.cos(angle) * 64, 54 + math.sin(angle) * 64,
                fill="#fde047", width=5, capstyle="round",
            )
        self.field_canvas.create_oval(32, 14, 112, 94, fill="#fde047", outline="#facc15", width=3)
        self.field_canvas.create_oval(46, 28, 82, 60, fill="#fef9c3", outline="")
        for cloud in self.ambient_clouds:
            cx = cloud["x"]
            cy = min(cloud["y"], 92)
            size = cloud["size"]
            self.field_canvas.create_oval(cx - size, cy, cx + size, cy + 28, fill="white", outline="")
            self.field_canvas.create_oval(cx - int(size * 0.65), cy - 16, cx + int(size * 0.52), cy + 20, fill="white", outline="")
            self.field_canvas.create_oval(cx - int(size * 0.1), cy - 12, cx + int(size * 0.88), cy + 18, fill="white", outline="")

    def draw_lanes(self):
        for lane in range(LANE_COUNT):
            top = lane * self.lane_height
            bottom = top + self.lane_height
            shade = "#6abf31" if lane % 2 == 0 else "#5aaa28"
            self.field_canvas.create_rectangle(0, top, self.field_width, bottom, fill=shade, outline="")
            self.field_canvas.create_line(0, bottom, self.field_width, bottom, fill="#3d8b1a", width=3)

    def draw_tiles(self):
        for tile in self.tiles:
            x = tile["x"]
            y = tile["y"]
            hw = self.tile_width / 2 - 6
            hh = self.tile_height / 2 - 14
            occupied = tile["unit_id"] is not None
            if occupied:
                self.field_canvas.create_oval(x - hw, y - hh, x + hw, y + hh, fill="#8b5e3c", outline="#5c3d1e", width=2)
                self.field_canvas.create_arc(x - hw + 8, y - hh + 8, x + hw - 8, y + hh - 8, start=210, extent=120, style="arc", outline="#6b4226", width=2)
            else:
                self.field_canvas.create_oval(x - hw, y - hh, x + hw, y + hh, fill="#4aad4a", outline="#3a9a3a", width=2)
                self.field_canvas.create_oval(x - hw + 6, y - hh + 6, x + hw - 6, y + hh - 6, fill="#55bf55", outline="")

    def draw_props(self):
        hx = 58
        hy = int(self.field_height * 0.18)
        self.field_canvas.create_rectangle(hx - 34, hy + 10, hx + 34, hy + 78, fill="#fef9c3", outline="#ca8a04", width=2)
        self.field_canvas.create_polygon(hx - 40, hy + 12, hx + 40, hy + 12, hx, hy - 32, fill="#dc2626", outline="#991b1b", width=2)
        self.field_canvas.create_rectangle(hx - 12, hy + 44, hx + 12, hy + 78, fill="#92400e", outline="#78350f", width=1)
        self.field_canvas.create_oval(hx - 2, hy + 57, hx + 2, hy + 61, fill="#fde68a", outline="")
        self.field_canvas.create_rectangle(hx - 26, hy + 16, hx - 8, hy + 34, fill="#bae6fd", outline="#7dd3fc", width=1)
        self.field_canvas.create_rectangle(hx + 8, hy + 16, hx + 26, hy + 34, fill="#bae6fd", outline="#7dd3fc", width=1)
        self.field_canvas.create_rectangle(hx + 14, hy - 32, hx + 22, hy + 12, fill="#94a3b8", outline="#64748b", width=1)

        wx = self.base_line_x
        rail1 = int(self.field_height * 0.28)
        rail2 = int(self.field_height * 0.72)
        self.field_canvas.create_rectangle(wx - 10, rail1, wx + 10, rail1 + 8, fill="#f5f5dc", outline="#d4b896", width=1)
        self.field_canvas.create_rectangle(wx - 10, rail2, wx + 10, rail2 + 8, fill="#f5f5dc", outline="#d4b896", width=1)
        for fy in range(16, self.field_height - 16, 22):
            self.field_canvas.create_polygon(
                wx - 7, fy, wx + 7, fy, wx + 7, fy + 16, wx, fy + 22, wx - 7, fy + 16,
                fill="#fafaf0", outline="#d4b896", width=1,
            )

    def draw_units(self):
        for unit in self.units:
            self.field_canvas.create_oval(
                unit["x"] - 24,
                unit["y"] + 10,
                unit["x"] + 24,
                unit["y"] + 24,
                fill="#2f5130",
                outline="",
            )
            self.draw_unit_portrait(self.field_canvas, unit["x"], unit["y"] - 38, unit, facing="right")
            self.draw_health_bar(unit["x"] - 30, unit["y"] - 56, 60, unit["hp"], unit["max_hp"], unit["accent"])
            self.field_canvas.create_text(
                unit["x"],
                unit["y"] - 68,
                text=f"{unit['name']} L{unit['level']}",
                fill="#f8fafc",
                font=("Segoe UI", 8, "bold"),
            )
            refund = unit["total_spent"] // 2
            upgrade_text = "MAX" if unit["level"] >= 3 else f"{unit['upgrade_cost']}g"
            self.field_canvas.create_text(
                unit["x"],
                unit["y"] + 36,
                text=f"Upgrade {upgrade_text} | Sell {refund}g",
                fill="#1f2937",
                font=("Segoe UI", 8, "bold"),
            )

    def draw_unit_portrait(self, canvas, x, y, unit, facing="right"):
        d = 1 if facing == "right" else -1
        canvas.create_rectangle(x - 12, y + 32, x - 2, y + 52, fill="#374151", outline="")
        canvas.create_rectangle(x + 2, y + 32, x + 12, y + 52, fill="#374151", outline="")
        canvas.create_rectangle(x - 16, y + 4, x + 16, y + 36, fill=unit["color"], outline="")
        canvas.create_oval(x - 18, y - 32, x + 18, y + 6, fill="#fde68a", outline="#f59e0b", width=2)
        canvas.create_arc(x - 18, y - 40, x + 18, y - 14, start=0, extent=180, fill=unit["color"], outline=unit["color"])
        canvas.create_oval(x - 10, y - 22, x - 2, y - 14, fill="white", outline="")
        canvas.create_oval(x + 2, y - 22, x + 10, y - 14, fill="white", outline="")
        canvas.create_oval(x - 9 + d, y - 21, x - 3 + d, y - 15, fill="#111827", outline="")
        canvas.create_oval(x + 3 + d, y - 21, x + 9 + d, y - 15, fill="#111827", outline="")
        canvas.create_arc(x - 7, y - 8, x + 7, y + 2, start=200, extent=140, style="arc", outline="#92400e", width=2)
        canvas.create_line(x + (12 * d), y + 12, x + (38 * d), y + 2, fill="#64748b", width=5, capstyle="round")
        canvas.create_oval(x + (34 * d) - 5, y - 3, x + (34 * d) + 5, y + 7, fill="#475569", outline="")

    def draw_enemies(self):
        for enemy in self.enemies:
            bounce = math.sin(enemy["bob"]) * 2.5
            x = enemy["x"]
            y = enemy["y"] + bounce
            self.field_canvas.create_oval(
                x - enemy["radius"] + 4,
                y + 12,
                x + enemy["radius"] - 4,
                y + 28,
                fill="#355e2f",
                outline="",
            )
            self.draw_enemy(enemy, x, y - 8)
            self.draw_health_bar(x - 28, y - 58, 56, enemy["hp"], enemy["max_hp"], enemy["accent"])

    def draw_enemy(self, enemy, x, y):
        c = self.field_canvas
        color = enemy["color"]
        if enemy["shape"] == "runner":
            skin = "#d9f99d"
            c.create_oval(x - 11, y - 22, x + 11, y + 2, fill=skin, outline="#4d7c0f", width=2)
            c.create_oval(x - 7, y - 18, x - 1, y - 12, fill="white", outline="")
            c.create_oval(x + 1, y - 18, x + 7, y - 12, fill="white", outline="")
            c.create_oval(x - 6, y - 17, x - 2, y - 13, fill="#111", outline="")
            c.create_oval(x + 2, y - 17, x + 6, y - 13, fill="#111", outline="")
            c.create_rectangle(x - 12, y + 2, x + 12, y + 22, fill=color, outline="")
            c.create_line(x - 12, y + 8, x - 32, y + 6, fill=skin, width=5, capstyle="round")
            c.create_line(x - 12, y + 14, x - 28, y + 22, fill=skin, width=4, capstyle="round")
            c.create_rectangle(x - 10, y + 22, x - 2, y + 44, fill="#3f3f46", outline="")
            c.create_rectangle(x + 2, y + 22, x + 10, y + 44, fill="#3f3f46", outline="")
        elif enemy["shape"] == "brute":
            skin = "#bef264"
            c.create_oval(x - 18, y - 34, x + 18, y - 2, fill=skin, outline="#365314", width=2)
            c.create_oval(x - 11, y - 26, x - 3, y - 18, fill="#fbbf24", outline="")
            c.create_oval(x + 3, y - 26, x + 11, y - 18, fill="#fbbf24", outline="")
            c.create_oval(x - 10, y - 25, x - 4, y - 19, fill="#111", outline="")
            c.create_oval(x + 4, y - 25, x + 10, y - 19, fill="#111", outline="")
            c.create_arc(x - 9, y - 10, x + 9, y - 2, start=200, extent=140, style="arc", outline="#365314", width=2)
            c.create_rectangle(x - 26, y - 2, x + 26, y + 34, fill=color, outline="")
            c.create_line(x - 26, y + 10, x - 52, y + 8, fill=skin, width=8, capstyle="round")
            c.create_line(x - 26, y + 18, x - 46, y + 28, fill=skin, width=6, capstyle="round")
            c.create_rectangle(x - 22, y + 34, x - 6, y + 60, fill="#3f3f46", outline="")
            c.create_rectangle(x + 6, y + 34, x + 22, y + 60, fill="#3f3f46", outline="")
        else:
            skin = "#bbf7d0"
            c.create_oval(x - 13, y - 28, x + 13, y, fill=skin, outline="#4d7c0f", width=2)
            c.create_oval(x - 8, y - 20, x - 2, y - 14, fill="white", outline="")
            c.create_oval(x + 2, y - 20, x + 8, y - 14, fill="white", outline="")
            c.create_oval(x - 7, y - 19, x - 3, y - 15, fill="#111", outline="")
            c.create_oval(x + 3, y - 19, x + 7, y - 15, fill="#111", outline="")
            c.create_arc(x - 7, y - 7, x + 7, y + 1, start=200, extent=140, style="arc", outline="#365314", width=2)
            c.create_rectangle(x - 14, y, x + 14, y + 26, fill=color, outline="")
            c.create_line(x - 14, y + 8, x - 38, y + 6, fill=skin, width=6, capstyle="round")
            c.create_line(x - 14, y + 16, x - 34, y + 24, fill=skin, width=4, capstyle="round")
            c.create_rectangle(x - 12, y + 26, x - 2, y + 52, fill="#3f3f46", outline="")
            c.create_rectangle(x + 2, y + 26, x + 12, y + 52, fill="#3f3f46", outline="")

    def draw_health_bar(self, x, y, width, hp, max_hp, fill_color):
        self.field_canvas.create_rectangle(x, y, x + width, y + 7, fill="#111827", outline="")
        ratio = 0 if max_hp == 0 else max(0.0, min(1.0, hp / max_hp))
        self.field_canvas.create_rectangle(x, y, x + (width * ratio), y + 7, fill=fill_color, outline="")

    def draw_projectiles(self):
        for projectile in self.projectiles:
            self.field_canvas.create_oval(
                projectile["x"] - 5,
                projectile["y"] - 5,
                projectile["x"] + 5,
                projectile["y"] + 5,
                fill=projectile["color"],
                outline="",
            )
            self.field_canvas.create_oval(
                projectile["x"] - 10,
                projectile["y"] - 10,
                projectile["x"] + 10,
                projectile["y"] + 10,
                outline=projectile["color"],
            )

    def draw_particles(self):
        for particle in self.particles:
            size = particle["size"]
            self.field_canvas.create_oval(
                particle["x"] - size,
                particle["y"] - size,
                particle["x"] + size,
                particle["y"] + size,
                fill=particle["color"],
                outline="",
            )

    def draw_game_over_overlay(self):
        cx = self.field_width / 2
        cy = self.field_height / 2
        self.field_canvas.create_rectangle(cx - 260, cy - 80, cx + 260, cy + 80, fill="#0f172a", outline="#334155", width=3)
        won = self.wave > MAX_WAVES
        title = "YOU WIN!" if won else "GAME OVER"
        title_color = "#4ade80" if won else "#f87171"
        self.field_canvas.create_text(cx, cy - 30, text=title, fill=title_color, font=("Segoe UI", 32, "bold"))
        self.field_canvas.create_text(cx, cy + 20, text="Press Restart to play again.", fill="#cbd5e1", font=("Segoe UI", 14))

    def draw_front_fx(self):
        for lane in range(LANE_COUNT):
            lane_bottom = (lane + 1) * self.lane_height
            self.field_canvas.create_rectangle(0, lane_bottom - 10, self.field_width, lane_bottom + 8, fill="#3d8b1a", outline="")
            for tx in range(0, self.field_width, 20):
                sway = math.sin((self.frame_count * 0.05) + (tx * 0.03) + lane) * 3
                self.field_canvas.create_line(tx + 5, lane_bottom + 6, tx + 3 + sway, lane_bottom - 4, fill="#2d6e0f", width=2)


def main():
    root = tk.Tk()
    ModernLaneDefenseGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
