# Wizard Rush Game

A polished 2D endless runner built with `pygame` (tested with `pygame-ce`), featuring a wizard-themed visual style, dynamic VFX, menu flow, and skill-based movement.

## Highlights
- Atmospheric 2D art direction (night sky, parallax depth, castle silhouettes, magical palette)
- Responsive runner gameplay with jump + double-tap long jump
- Two obstacle types (standard hurdles and cursed walls)
- Spell casting system for obstacle control
- Layered VFX stack:
  - Dust and spark trails
  - Hit bursts
  - Screen shake
  - Chromatic impact flash
- Full game state flow:
  - Main Menu
  - Pause
  - Settings
  - Game Over / Retry

## Controls
- `Enter` / `Space` (from menu): Start
- `Space` / `Up Arrow`: Jump
- `Space` double-tap: Long jump
- `E`: Cast spell
- `Esc`: Pause / Resume
- `R`: Restart run

## Requirements
- Python 3.10+ (project currently used with Python 3.14)
- `pygame-ce` (imported as `pygame`)

## Installation
```powershell
python -m pip install pygame-ce
```

If you run multiple Python versions, install with your target interpreter:
```powershell
& "C:\path\to\python.exe" -m pip install pygame-ce
```

## Run
From the project directory:
```powershell
python wizard_rush.py
```

Or with an explicit interpreter:
```powershell
& "C:\path\to\python.exe" "d:\My projects\Wizard Rush Game\wizard_rush.py"
```

## Project Structure
- `wizard_rush.py` - main game source (states, gameplay loop, rendering, VFX)
- `assets/` - local game assets
- `path.txt` - helper command used locally to launch the game

## Gameplay Notes
- Long jump is intentionally timing-based: press `Space` twice quickly.
- Cursed walls are visually distinct and designed to force better reactions.
- Effects intensity can be changed in `Settings`.

## Development Ideas
- Audio layer (music + SFX + adaptive mixing)
- Collectibles, missions, and progression
- Additional enemy behavior and scripted encounters
- Character skins / wand variants

## License
No license file is currently included. Add one before public reuse/distribution if needed.
