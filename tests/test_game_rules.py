import unittest

from game_rules import choose_enemy_type, damage_after_armor


class GameRulesTests(unittest.TestCase):
    def test_wave_progression_unlocks_enemy_types(self):
        self.assertEqual(choose_enemy_type(1, 0)["name"], "Walker")
        self.assertEqual(choose_enemy_type(3, 3)["name"], "Runner")
        self.assertEqual(choose_enemy_type(5, 5)["name"], "Brute")
        self.assertEqual(choose_enemy_type(6, 4)["name"], "Armored")
        self.assertEqual(choose_enemy_type(8, 9)["name"], "Medic")

    def test_armor_never_reduces_damage_below_one(self):
        self.assertEqual(damage_after_armor(10, 4), 6)
        self.assertEqual(damage_after_armor(3, 8), 1)


if __name__ == "__main__":
    unittest.main()
