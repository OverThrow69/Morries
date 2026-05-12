from game_config import ENEMY_TYPES


def choose_enemy_type(wave, index):
    if wave >= 8 and index % 9 == 0:
        return ENEMY_TYPES[4]
    if wave >= 6 and index % 4 == 0:
        return ENEMY_TYPES[3]
    if wave >= 5 and index % 5 == 0:
        return ENEMY_TYPES[2]
    if wave >= 3 and index % 3 == 0:
        return ENEMY_TYPES[1]
    return ENEMY_TYPES[0]


def damage_after_armor(raw_damage, armor):
    return max(1, raw_damage - armor)
