# Spaceship Engine

Spaceship Engine is a small Python engine for real-time ASCII/terminal games. It provides a fixed-timestep game loop, entity + sprite rendering with z-order, a basic HUD system, and keyboard input via `pynput`.

## Install

From a checkout of this repo:

```bash
python -m pip install -e .
```

Or, if published to PyPI:

```bash
python -m pip install spaceship-engine
```

Requires Python 3.8+.

## Quick start

Create a game, add an entity, and run:

```python
from spaceship.game import Game
from spaceship.render.entity import Entity
from spaceship.utils.math import Vector


class Player(Entity):
    def __init__(self, game: Game):
        super().__init__(game, Vector(0, 0))
        self.sprite.load(
            " O \n"
            "/|\\\n"
            "/ \\",
            priority=10,
        )

    def update(self, dt: float):
        speed = 30
        if self.game.input.is_char_held("w"):
            self.position += Vector(0, -speed) * dt
        if self.game.input.is_char_held("s"):
            self.position += Vector(0, speed) * dt
        if self.game.input.is_char_held("a"):
            self.position += Vector(-speed, 0) * dt
        if self.game.input.is_char_held("d"):
            self.position += Vector(speed, 0) * dt
        if self.game.input.is_char_held("q"):
            raise SystemExit(0)


def init():
    game.add_entity(Player(game))


def update(dt: float):
    pass


game = Game(init_hook=init, update_hook=update, border=True)
game.run()
```

## Core concepts

### Game loop (`spaceship.game.Game`)

- Fixed-timestep updates at 60 Hz (`fixed_dt = 1/60`), with a cap to avoid runaway catch-up after long stalls.
- Rendering runs as fast as possible and uses a terminal diff to redraw only changed cells.
- Add/remove world objects with `game.add_entity(entity)` / `entity.kill()`.

### Entities (`spaceship.render.entity.Entity`)

- Subclass `Entity` and implement `update(self, dt: float)`.
- Use `self.position` (a `Vector`) to move in world space.
- Each entity owns a `Sprite` (`self.sprite`) that is rendered by the `Camera`.

### Sprites (`spaceship.render.sprite.Sprite`)

- Load ASCII art via `sprite.load(raw_string, priority=1)`.
- Z-order: `sprite.priority` (higher numbers render on top).
- Center marker: include exactly one `\t` in the raw art to mark the sprite center (the tab is removed).
- Transparency: the engine treats the bell character `\a` as transparent (that cell is skipped during rendering).

### Camera (`spaceship.render.camera.Camera` / `CameraMode`)

The camera transforms world positions into screen positions. Available modes:

- `CameraMode.CENTER`
- `CameraMode.TOP_LEFT`, `CameraMode.TOP_RIGHT`
- `CameraMode.BOT_LEFT`, `CameraMode.BOT_RIGHT`

### HUD (`spaceship.render.hud.HUD`, `HUDElement`, `HUDAlignment`)

HUD elements are templated strings with backtick-delimited placeholders:

```python
from spaceship.render.hud import HUDElement, HUDAlignment

score_hud = HUDElement(
    template="Score: `score`",
    values={"score": "0"},
    align=HUDAlignment.RIGHT,
)
game.hud.add_bottom_hud(score_hud)

# Later:
score_hud.set_value("score", "123")
```

Top HUD height is computed automatically based on alignment groups; bottom HUD renders one line per element.

### Input (`spaceship.input.input.Input`)

- Check held keys: `game.input.is_char_held("w")`, or `game.input.is_key_held(key)` for special keys.
- Register callbacks: `hook_to_keypress(fn)` / `hook_to_keyrelease(fn)` (and unhook variants).

## Configure the playfield

The grid size and margins live in `spaceship.utils.constants`:

- `SIZE_X`, `SIZE_Y`: logical grid dimensions (characters)
- `LEFT_MARGIN`, `RIGHT_MARGIN`, `TOP_MARGIN`
- `CELL_WIDTH`: terminal columns per cell
- `CHAR_ASPECT`: used by camera Y scaling

There is also `spaceship.utils.constants.configure(...)`, but note that many engine modules import these constants at import time. For best results, set constants before importing/constructing the engine (or edit `constants.py` in a fork).

## Run the demo

After `pip install -e .`:

```bash
python -m spaceship.demo.demo
```

Controls: `WASD` to move the rock, `Q` to quit.

## Notes / limitations

- Keyboard input uses `pynput`, which may require accessibility permissions (macOS) or an active desktop session (some Linux setups).
- ANSI escape codes are used for rendering; use a modern terminal (Windows Terminal, iTerm2, etc.).
