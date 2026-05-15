import unittest

from game_config import MAX_WAVES, UNIT_TYPES, WAVE_DELAY_SECONDS, FRAMES_PER_SECOND
from main import ModernLaneDefenseGame


def make_game():
    game = ModernLaneDefenseGame.__new__(ModernLaneDefenseGame)
    game.gold = 0
    game.lives = 15
    game.wave = 1
    game.selected_unit_index = 0
    game.units = []
    game.enemies = []
    game.projectiles = []
    game.particles = []
    game.tiles = []
    game.spawn_queue = []
    game.spawning = False
    game.game_over = False
    game.next_unit_id = 1
    game.countdown_frames = 0
    game.wave_total = 0
    game.wave_spawned = 0
    game.wave_defeated = 0
    game.wave_resolved = 0
    game.base_line_x = 120
    game.messages = []
    game.update_hud = lambda: None
    game.show_message = game.messages.append
    return game


def make_tile(lane=0, column=0):
    return {
        "lane": lane,
        "column": column,
        "x": 180 + (column * 100),
        "y": 120 + (lane * 100),
        "unit_id": None,
    }


def make_enemy(**overrides):
    data = {
        "lane": 0,
        "x": 100,
        "y": 100,
        "hp": 10,
        "max_hp": 10,
        "speed": 1,
        "damage": 1,
        "attack_rate": 10,
        "attack_cooldown": 0,
        "reward": 7,
        "armor": 0,
        "heal": 0,
        "slow_frames": 0,
        "slow_multiplier": 1,
        "bob": 0,
        "accent": "#ffffff",
    }
    data.update(overrides)
    return data


class GameplaySmokeTests(unittest.TestCase):
    def test_can_place_each_unit_type_with_enough_gold(self):
        for index, unit_type in enumerate(UNIT_TYPES):
            with self.subTest(unit=unit_type["name"]):
                game = make_game()
                tile = make_tile(column=index)
                game.tiles = [tile]
                game.selected_unit_index = index
                game.gold = unit_type["cost"]

                game.place_unit(tile)

                self.assertEqual(game.gold, 0)
                self.assertEqual(len(game.units), 1)
                self.assertEqual(game.units[0]["name"], unit_type["name"])
                self.assertEqual(game.units[0]["level"], 1)
                self.assertEqual(tile["unit_id"], game.units[0]["id"])

    def test_cannot_place_unit_if_gold_is_too_low(self):
        game = make_game()
        tile = make_tile()
        game.tiles = [tile]
        game.selected_unit_index = 0
        game.gold = UNIT_TYPES[0]["cost"] - 1

        game.place_unit(tile)

        self.assertEqual(game.units, [])
        self.assertIsNone(tile["unit_id"])
        self.assertEqual(game.gold, UNIT_TYPES[0]["cost"] - 1)

    def test_upgrade_unit_to_max_level_three(self):
        game = make_game()
        tile = make_tile()
        game.tiles = [tile]
        game.gold = 999
        game.place_unit(tile)
        unit = game.units[0]
        first_upgrade_cost = unit["upgrade_cost"]

        game.upgrade_unit(unit["id"])
        second_upgrade_cost = unit["upgrade_cost"]
        game.upgrade_unit(unit["id"])

        self.assertEqual(unit["level"], 3)
        self.assertEqual(unit["upgrade_cost"], 0)
        self.assertEqual(unit["total_spent"], UNIT_TYPES[0]["cost"] + first_upgrade_cost + second_upgrade_cost)

    def test_cannot_upgrade_past_level_three(self):
        game = make_game()
        tile = make_tile()
        game.tiles = [tile]
        game.gold = 999
        game.place_unit(tile)
        unit = game.units[0]
        game.upgrade_unit(unit["id"])
        game.upgrade_unit(unit["id"])
        gold_before_extra_upgrade = game.gold
        total_spent_before_extra_upgrade = unit["total_spent"]

        game.upgrade_unit(unit["id"])

        self.assertEqual(unit["level"], 3)
        self.assertEqual(game.gold, gold_before_extra_upgrade)
        self.assertEqual(unit["total_spent"], total_spent_before_extra_upgrade)

    def test_selling_refunds_half_of_total_spent(self):
        game = make_game()
        tile = make_tile()
        game.tiles = [tile]
        game.gold = 999
        game.place_unit(tile)
        unit = game.units[0]
        game.upgrade_unit(unit["id"])
        total_spent = unit["total_spent"]
        game.gold = 0

        game.sell_unit(tile)

        self.assertEqual(game.gold, total_spent // 2)
        self.assertEqual(game.units, [])
        self.assertIsNone(tile["unit_id"])

    def test_enemy_leak_reduces_lives_and_resolves_enemy(self):
        game = make_game()
        game.lives = 3
        game.wave_resolved = 1
        leaking_enemy = make_enemy(x=game.base_line_x)
        game.enemies = [leaking_enemy]

        game.update_enemies()

        self.assertEqual(game.lives, 2)
        self.assertEqual(game.wave_resolved, 2)
        self.assertNotIn(leaking_enemy, game.enemies)
        self.assertFalse(game.game_over)

    def test_game_over_triggers_at_zero_lives(self):
        game = make_game()
        game.lives = 1
        game.enemies = [make_enemy(x=game.base_line_x)]

        game.update_enemies()

        self.assertEqual(game.lives, 0)
        self.assertTrue(game.game_over)
        self.assertIn("The zombies broke through the village. Game over.", game.messages)

    def test_wave_progression_after_all_spawned_enemies_are_resolved(self):
        game = make_game()
        game.wave = 2
        game.spawning = True
        game.spawn_queue = []
        game.enemies = []
        game.wave_total = 8
        game.wave_resolved = 8

        game.check_wave_end()

        self.assertFalse(game.spawning)
        self.assertEqual(game.wave, 3)
        self.assertEqual(game.countdown_frames, WAVE_DELAY_SECONDS * FRAMES_PER_SECOND)

    def test_resolve_enemy_updates_reward_and_wave_counters(self):
        game = make_game()
        target = make_enemy(reward=11)
        game.enemies = [target]

        game.resolve_enemy(target)

        self.assertEqual(game.gold, 11)
        self.assertEqual(game.wave_defeated, 1)
        self.assertEqual(game.wave_resolved, 1)
        self.assertNotIn(target, game.enemies)

    def test_victory_triggers_after_final_wave_is_cleared(self):
        game = make_game()
        game.wave = MAX_WAVES + 1
        game.spawning = False
        game.enemies = []
        game.game_over = False

        game.check_wave_end()

        self.assertTrue(game.game_over)
        self.assertIn("You survived every wave. The village is safe.", game.messages)


if __name__ == "__main__":
    unittest.main()
