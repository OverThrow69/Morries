import unittest

from main import ModernLaneDefenseGame


def make_game():
    game = ModernLaneDefenseGame.__new__(ModernLaneDefenseGame)
    game.enemies = []
    game.units = []
    game.projectiles = []
    game.particles = []
    game.tiles = []
    game.gold = 0
    game.wave_defeated = 0
    game.wave_resolved = 0
    game.lives = 15
    game.base_line_x = 120
    game.game_over = False
    game.update_hud = lambda: None
    game.show_message = lambda text: None
    return game


def enemy(**overrides):
    data = {
        "lane": 0,
        "x": 200,
        "y": 100,
        "hp": 10,
        "max_hp": 10,
        "speed": 1,
        "damage": 1,
        "attack_rate": 10,
        "attack_cooldown": 5,
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


def unit(**overrides):
    data = {
        "id": "unit-1",
        "lane": 0,
        "x": 170,
        "y": 100,
        "hp": 20,
        "max_hp": 20,
        "level": 1,
        "name": "Soldier",
        "damage": 10,
        "range": 1,
        "fire_rate": 20,
        "projectile_speed": 15,
        "projectile_color": "#ffffff",
        "ability": "burst",
        "accent": "#ffffff",
    }
    data.update(overrides)
    return data


class CombatLogicTests(unittest.TestCase):
    def test_slow_timer_decreases_while_enemy_is_blocked(self):
        game = make_game()
        blocked_enemy = enemy(x=200, slow_frames=5, slow_multiplier=0.62)
        game.enemies = [blocked_enemy]
        game.units = [{
            "id": "unit-1",
            "lane": 0,
            "x": 170,
            "y": 100,
            "hp": 20,
            "accent": "#ffffff",
        }]

        game.update_enemies()

        self.assertEqual(blocked_enemy["slow_frames"], 4)
        self.assertEqual(blocked_enemy["x"], 200)

    def test_splash_damage_kills_multiple_enemies_and_counts_once(self):
        game = make_game()
        primary = enemy(x=200, hp=20, reward=3)
        splash_one = enemy(x=220, hp=4, reward=5)
        splash_two = enemy(x=235, hp=4, reward=6)
        outside_radius = enemy(x=320, hp=4, reward=11)
        game.enemies = [primary, splash_one, splash_two, outside_radius]
        projectile = {
            "damage": 10,
            "slow_frames": 0,
            "splash_radius": 50,
            "color": "#ffffff",
        }

        game.damage_enemy(primary, projectile)

        self.assertIn(primary, game.enemies)
        self.assertIn(outside_radius, game.enemies)
        self.assertNotIn(splash_one, game.enemies)
        self.assertNotIn(splash_two, game.enemies)
        self.assertEqual(game.gold, 11)
        self.assertEqual(game.wave_defeated, 2)
        self.assertEqual(game.wave_resolved, 2)

    def test_unit_targets_enemy_anywhere_in_same_lane(self):
        game = make_game()
        tower = unit(x=500, range=1)
        advanced_enemy = enemy(lane=0, x=140)
        far_enemy = enemy(lane=0, x=900)
        game.enemies = [far_enemy, advanced_enemy]

        target = game.find_target_for_unit(tower)

        self.assertIs(target, advanced_enemy)

    def test_unit_does_not_target_enemy_in_other_lane(self):
        game = make_game()
        tower = unit(lane=0, x=500, range=9999)
        other_lane_enemy = enemy(lane=1, x=100)
        game.enemies = [other_lane_enemy]

        self.assertIsNone(game.find_target_for_unit(tower))

    def test_engineer_repairs_damaged_ally_anywhere_in_same_lane(self):
        game = make_game()
        engineer = unit(id="engineer", name="Engineer", ability="repair", lane=0, x=180, hp=20, max_hp=20)
        damaged_ally = unit(id="ally", lane=0, x=900, hp=5, max_hp=20)
        game.units = [engineer, damaged_ally]

        game.repair_lane_unit(engineer)

        self.assertGreater(damaged_ally["hp"], 5)
        self.assertLessEqual(damaged_ally["hp"], damaged_ally["max_hp"])
        self.assertEqual(engineer["hp"], 20)

    def test_engineer_does_not_repair_units_in_other_lanes(self):
        game = make_game()
        engineer = unit(id="engineer", name="Engineer", ability="repair", lane=0, x=180)
        other_lane_ally = unit(id="ally", lane=1, x=180, hp=5, max_hp=20)
        game.units = [engineer, other_lane_ally]

        game.repair_lane_unit(engineer)

        self.assertEqual(other_lane_ally["hp"], 5)

    def test_upgraded_projectiles_include_level_type_and_style_for_drawing(self):
        game = make_game()
        target = enemy()
        sniper = unit(name="Sniper", ability="pierce", level=3)

        projectile = game.make_projectile(sniper, target)

        self.assertEqual(projectile["level"], 3)
        self.assertEqual(projectile["unit_name"], "Sniper")
        self.assertEqual(projectile["ability"], "pierce")
        self.assertEqual(projectile["projectile_style"], "long_tracer")


if __name__ == "__main__":
    unittest.main()
