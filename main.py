import math
import os
import random
import tkinter as tk
import winsound

from game_config import (
    BOTTOM_BAR_HEIGHT,
    COLUMN_COUNT,
    FRAMES_PER_SECOND,
    LANE_COUNT,
    MAX_WAVES,
    SOUND_DIR,
    TOP_BAR_HEIGHT,
    UNIT_TYPES,
    WAVE_DELAY_SECONDS,
)
from game_rules import choose_enemy_type, damage_after_armor


class ModernLaneDefenseGame:
    def __init__(self, root):
        self.root = root
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        self.field_width = self.screen_width
        self.field_height = self.screen_height - TOP_BAR_HEIGHT - BOTTOM_BAR_HEIGHT
        self.lane_height = self.field_height / LANE_COUNT
        self.base_line_x = 120
        self.tile_start_x = min(180, max(140, int(self.screen_width * 0.15)))
        self.tile_gap = max(8, min(12, int(self.screen_width * 0.01)))
        available_tile_width = max(420, self.screen_width - self.tile_start_x - 180)
        self.tile_width = min(112, int((available_tile_width - (self.tile_gap * (COLUMN_COUNT - 1))) / COLUMN_COUNT))
        self.tile_height = max(88, int(self.lane_height - 28))
        self.spawn_x = self.screen_width - 120
        self.unit_card_width = max(150, min(200, int((self.screen_width - 124) / len(UNIT_TYPES))))
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
        zombie_sound = os.path.join(SOUND_DIR, "zombie.wav")
        brute_sound = os.path.join(SOUND_DIR, "brute.wav")
        return {"Zombie": zombie_sound, "Brute": brute_sound}

    def play_enemy_sound(self, enemy_kind):
        if self.frame_count - self.last_sound_frame < 14:
            return
        sound_path = self.sound_paths.get(enemy_kind)
        if sound_path and os.path.exists(sound_path):
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
                width=self.unit_card_width,
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
        self.wave_resolved = 0
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
            width = self.unit_card_width
            info_x = min(98, int(width * 0.48))
            canvas.configure(highlightbackground="#fb923c" if selected else "#1f2937")
            canvas.delete("all")
            canvas.create_rectangle(0, 0, width, 116, fill="#111827", outline="")
            canvas.create_text(14, 14, text=str(index + 1), anchor="w", fill="#e2e8f0", font=("Segoe UI", 12, "bold"))
            canvas.create_text(36, 14, text=unit["name"], anchor="w", fill="#f8fafc", font=("Segoe UI", 11, "bold"))
            canvas.create_text(width - 12, 14, text=f"{unit['cost']}g", anchor="e", fill="#facc15", font=("Segoe UI", 11, "bold"))
            self.draw_unit_portrait(canvas, 18, 32, unit, facing="right")
            canvas.create_text(info_x, 50, text=unit["short"], anchor="w", fill="#cbd5e1", font=("Segoe UI", 9, "bold"))
            canvas.create_text(info_x, 70, text=f"Range {unit['base_range']}", anchor="w", fill="#94a3b8", font=("Segoe UI", 9))
            canvas.create_text(info_x, 88, text=f"Upgrade {unit['upgrade_cost']}", anchor="w", fill="#94a3b8", font=("Segoe UI", 9))
            if selected:
                canvas.create_text(width - 12, 100, text="READY", anchor="e", fill="#fb923c", font=("Segoe UI", 10, "bold"))

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
            progress = 0 if self.wave_total == 0 else self.wave_resolved / self.wave_total
            label = f"Wave {min(self.wave, MAX_WAVES)}  |  {self.wave_resolved}/{self.wave_total} resolved"
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
        self.wave_resolved = 0
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
        return choose_enemy_type(self.wave, index)

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
            "armor": blueprint.get("armor", 0),
            "heal": blueprint.get("heal", 0),
            "slow_frames": 0,
            "slow_multiplier": 1,
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
            "ability": unit_type["ability"],
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
            if unit["ability"] == "repair":
                self.repair_lane_unit(unit)
            if unit["cooldown"] > 0:
                unit["cooldown"] -= 1
                continue
            target = self.find_target_for_unit(unit)
            if not target:
                continue
            unit["cooldown"] = unit["fire_rate"]
            shots = 2 if unit["ability"] == "burst" and unit["level"] >= 2 else 1
            for shot_index in range(shots):
                self.projectiles.append(self.make_projectile(unit, target, shot_index))

    def repair_lane_unit(self, engineer):
        candidates = [
            unit for unit in self.units
            if unit["lane"] == engineer["lane"] and unit["id"] != engineer["id"] and unit["hp"] < unit["max_hp"]
        ]
        if not candidates:
            return
        target = min(candidates, key=lambda item: item["hp"] / item["max_hp"])
        target["hp"] = min(target["max_hp"], target["hp"] + 0.12 + (engineer["level"] * 0.04))

    def make_projectile(self, unit, target, shot_index=0):
        ability = unit["ability"]
        return {
            "x": unit["x"] + 26,
            "y": unit["y"] - 20 + (shot_index * 8),
            "lane": unit["lane"],
            "target": target,
            "speed": unit["projectile_speed"],
            "damage": unit["damage"],
            "color": unit["projectile_color"],
            "source_id": unit["id"],
            "ability": ability,
            "splash_radius": 42 + (unit["level"] * 7) if ability == "splash" else 0,
            "pierce_left": unit["level"] if ability == "pierce" else 0,
            "slow_frames": 80 + (unit["level"] * 20) if ability == "slow" else 0,
        }

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
            if enemy["slow_frames"] > 0:
                enemy["x"] += enemy["speed"] * (1 - enemy["slow_multiplier"])
                enemy["slow_frames"] -= 1
            if enemy["heal"]:
                self.heal_nearby_enemies(enemy)
            enemy["bob"] += 0.08
            if enemy["x"] <= self.base_line_x:
                self.lives -= 1
                self.wave_resolved += 1
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

    def heal_nearby_enemies(self, medic):
        for enemy in self.enemies:
            if enemy is medic or enemy["lane"] != medic["lane"] or enemy["hp"] >= enemy["max_hp"]:
                continue
            if abs(enemy["x"] - medic["x"]) <= 130:
                enemy["hp"] = min(enemy["max_hp"], enemy["hp"] + medic["heal"])

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
                self.damage_enemy(target, projectile)
                self.add_hit_particles(projectile["x"], projectile["y"], projectile["color"])
                if target["hp"] <= 0:
                    self.resolve_enemy(target)
                if projectile["pierce_left"] > 0:
                    projectile["pierce_left"] -= 1
                    next_target = self.find_pierce_target(projectile, target)
                    if next_target:
                        projectile["target"] = next_target
                        active.append(projectile)
                continue
            projectile["x"] += (dx / distance) * projectile["speed"]
            projectile["y"] += (dy / distance) * projectile["speed"]
            active.append(projectile)
        self.projectiles = active

    def damage_enemy(self, enemy, projectile):
        enemy["hp"] -= damage_after_armor(projectile["damage"], enemy["armor"])
        if projectile["slow_frames"] > 0:
            enemy["slow_frames"] = max(enemy["slow_frames"], projectile["slow_frames"])
            enemy["slow_multiplier"] = 0.62
        if projectile["splash_radius"] > 0:
            for splash_target in self.enemies:
                if splash_target is enemy or splash_target["lane"] != enemy["lane"]:
                    continue
                if abs(splash_target["x"] - enemy["x"]) <= projectile["splash_radius"]:
                    splash_target["hp"] -= damage_after_armor(max(1, projectile["damage"] // 2), splash_target["armor"])
                    self.add_hit_particles(splash_target["x"], splash_target["y"] - 18, projectile["color"])
                    if splash_target["hp"] <= 0:
                        self.resolve_enemy(splash_target)

    def resolve_enemy(self, enemy):
        if enemy not in self.enemies:
            return
        self.gold += enemy["reward"]
        self.wave_defeated += 1
        self.wave_resolved += 1
        self.add_death_particles(enemy["x"], enemy["y"], enemy["accent"])
        self.enemies = [item for item in self.enemies if item is not enemy]
        self.update_hud()

    def find_pierce_target(self, projectile, previous_target):
        candidates = [
            enemy for enemy in self.enemies
            if enemy["lane"] == projectile["lane"] and enemy is not previous_target and enemy["x"] > previous_target["x"]
        ]
        if not candidates:
            return None
        return min(candidates, key=lambda enemy: enemy["x"])

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
        elif enemy["shape"] == "armored":
            skin = "#bbf7d0"
            c.create_oval(x - 14, y - 28, x + 14, y, fill=skin, outline="#334155", width=2)
            c.create_rectangle(x - 20, y - 30, x + 20, y - 16, fill="#64748b", outline="#334155", width=2)
            c.create_oval(x - 8, y - 20, x - 2, y - 14, fill="#f8fafc", outline="")
            c.create_oval(x + 2, y - 20, x + 8, y - 14, fill="#f8fafc", outline="")
            c.create_rectangle(x - 18, y, x + 18, y + 28, fill=color, outline="#1e293b", width=2)
            c.create_rectangle(x - 22, y + 6, x + 22, y + 20, fill="#94a3b8", outline="#475569", width=1)
            c.create_line(x - 18, y + 10, x - 44, y + 9, fill=skin, width=6, capstyle="round")
            c.create_rectangle(x - 14, y + 28, x - 4, y + 54, fill="#3f3f46", outline="")
            c.create_rectangle(x + 4, y + 28, x + 14, y + 54, fill="#3f3f46", outline="")
        elif enemy["shape"] == "medic":
            skin = "#ccfbf1"
            c.create_oval(x - 13, y - 28, x + 13, y, fill=skin, outline="#0f766e", width=2)
            c.create_oval(x - 8, y - 20, x - 2, y - 14, fill="white", outline="")
            c.create_oval(x + 2, y - 20, x + 8, y - 14, fill="white", outline="")
            c.create_rectangle(x - 15, y, x + 15, y + 28, fill=color, outline="")
            c.create_rectangle(x - 4, y + 6, x + 4, y + 22, fill="#f8fafc", outline="")
            c.create_rectangle(x - 11, y + 12, x + 11, y + 16, fill="#f8fafc", outline="")
            c.create_line(x - 15, y + 9, x - 38, y + 7, fill=skin, width=6, capstyle="round")
            c.create_rectangle(x - 12, y + 28, x - 2, y + 52, fill="#3f3f46", outline="")
            c.create_rectangle(x + 2, y + 28, x + 12, y + 52, fill="#3f3f46", outline="")
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
        if enemy["slow_frames"] > 0:
            c.create_oval(x - 24, y - 36, x + 24, y + 60, outline="#67e8f9", width=2)

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
