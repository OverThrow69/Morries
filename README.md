# Tower Defence

Hierdie is 'n plaaslike desktop game met zombies en mense.

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
- Medic - herstel nabygeleë zombies

## Lêers

- `main.py` - die desktop game
- `game_config.py` - balans, constants en tipe-data
- `game_rules.py` - klein toetsbare spelreëls
- `launch.pyw` - stille Python launcher
- `start_game.vbs` - maak die game oop sonder `cmd`
- `index.html` - ouer webweergawe/prototipe
