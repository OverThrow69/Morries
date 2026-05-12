# Tower Defence

Hierdie is 'n plaaslike Python Tkinter desktop game met zombies en mense.

## Main development path

The main game is the Python Tkinter desktop version.

Future development should focus on:

- `main.py` - main desktop game loop, UI, rendering, and gameplay systems
- `game_config.py` - balance, constants, unit data, and enemy data
- `game_rules.py` - small testable gameplay rules
- `tests/` - automated tests for rules and game behavior

`index.html` is only an old browser prototype / legacy version. Keep it for reference for now, but do not treat it as the main game.

## Hoe om oop te maak

1. Dubbelklik `start_game.vbs`
2. Dit maak oop sonder `cmd`

## Hoe om te speel

1. Waves begin outomaties elke 5 sekondes
2. Klik op 'n groen bouplek om 'n mens te plaas
3. Klik weer op dieselfde plek om daardie mens te upgrade
4. Gebruik die nommerknoppies `1` tot `5` om tussen mense te wissel
5. Regsklik op 'n mens om hom te verkoop
6. Hou die zombies weg van jou basis vir 12 waves

## Mense

- Soldier - burst fire vanaf level 2
- Hunter - vertraag zombies
- Sniper - skote kan deur zombies pierce
- Flamethrower - doen area damage
- Engineer - herstel beseerde mense in dieselfde lane

## Vyande

- Walker - gewone zombie
- Runner - vinnig maar swakker
- Brute - stadig en taai
- Armored - verminder inkomende skade
- Medic - herstel nabygelee zombies

## Leers

- `main.py` - die hoof Python Tkinter desktop game
- `game_config.py` - balans, constants en tipe-data
- `game_rules.py` - klein toetsbare spelreels
- `tests/` - automated tests
- `launch.pyw` - stille Python launcher
- `start_game.vbs` - maak die game oop sonder `cmd`
- `index.html` - ouer browser prototype / legacy version, nie die hoof game nie
