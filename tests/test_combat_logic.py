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


if __name__ == "__main__":
    unittest.main()
