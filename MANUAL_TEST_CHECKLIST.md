# Manual Gameplay Test Checklist

Use the Python Tkinter desktop game, not `index.html`.

## Startup

- [ ] Start the game with `start_game.vbs` or `py main.py`.
- [ ] Game opens fullscreen.
- [ ] HUD shows gold, lives, wave, speed, and wave progress.
- [ ] Press `Esc`; game exits fullscreen or becomes windowed.
- [ ] Restart button resets the game state.

## Unit Placement

- [ ] Press `1`, place Soldier on an empty green build tile.
- [ ] Press `2`, place Hunter.
- [ ] Press `3`, place Sniper.
- [ ] Press `4`, place Flamethrower.
- [ ] Press `5`, place Engineer.
- [ ] Gold decreases by the correct unit cost.
- [ ] Cannot place a unit if gold is too low.

## Unit Upgrades

- [ ] Click an existing Soldier to upgrade it.
- [ ] Upgrade Hunter.
- [ ] Upgrade Sniper.
- [ ] Upgrade Flamethrower.
- [ ] Upgrade Engineer.
- [ ] Gold decreases by upgrade cost.
- [ ] Unit level increases.
- [ ] Unit cannot upgrade past level 3.
- [ ] Max-level unit shows or behaves as maxed.

## Selling

- [ ] Right-click Soldier to sell.
- [ ] Right-click Hunter to sell.
- [ ] Right-click Sniper to sell.
- [ ] Right-click Flamethrower to sell.
- [ ] Right-click Engineer to sell.
- [ ] Gold increases by refund amount.
- [ ] Sold unit disappears from the tile.
- [ ] Sold unit no longer fires.
- [ ] Its tile can be reused.

## Wave Flow

- [ ] First wave starts automatically after countdown.
- [ ] Later waves start automatically after previous wave clears.
- [ ] Press `Space` during countdown to force-start a wave.
- [ ] Pressing `Space` during an active wave does not break anything.
- [ ] Wave counter progresses correctly.

## Speed Toggle

- [ ] Click speed button to switch from `1x` to `2x`.
- [ ] Click again to switch to `3x`.
- [ ] Click again to return to `1x`.
- [ ] Enemies, projectiles, countdown, and combat visibly speed up.

## Enemy Blocking / Attacking

- [ ] Let an enemy reach a unit in the same lane.
- [ ] Enemy stops moving at the unit.
- [ ] Enemy attacks the unit.
- [ ] Unit HP decreases.
- [ ] Unit is removed when HP reaches 0.
- [ ] Enemy continues moving after destroying the unit.

## Unit Abilities

- [ ] Soldier at level 1 fires normally.
- [ ] Soldier at level 2+ fires burst shots.
- [ ] Hunter shots slow enemies.
- [ ] Slowed enemies move slower.
- [ ] Slowed enemies' slow timer expires normally, even while blocked.
- [ ] Sniper shots pierce to another enemy in the same lane.
- [ ] Flamethrower splash damages nearby enemies in the same lane.
- [ ] Flamethrower splash can kill multiple enemies without duplicate rewards.
- [ ] Engineer repairs damaged allied units in the same lane.
- [ ] Engineer does not repair enemies or units in other lanes.

## Special Enemies

- [ ] Armored enemies take reduced damage.
- [ ] Armored enemies still take at least 1 damage per hit.
- [ ] Medic enemies heal nearby damaged enemies in the same lane.
- [ ] Medic healing does not exceed max HP.

## Lives / Lose Condition

- [ ] Let enemies leak past the base line.
- [ ] Lives decrease by 1 per leaked enemy.
- [ ] Wave progress treats leaked enemies as resolved.
- [ ] At 0 lives, game over appears.
- [ ] After game over, waves/combat stop updating.
- [ ] Restart works after game over.

## Victory

- [ ] Survive through wave 12.
- [ ] After all wave 12 enemies are defeated or resolved, victory message appears.
- [ ] Game shows win overlay.
- [ ] Restart works after victory.
