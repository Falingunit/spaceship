import time

from spaceship.utils import *
from spaceship.render import Renderer
from spaceship.sprite import Sprite

class Game:
    """Encapsulates game objects, animations, hooks, and the main loop."""
    def __init__(self):
        self.objects    = []
        self.animations = []
        self.sprites    = []

        # User‐defined hooks (can be replaced)
        self.init_hook   = lambda: None
        self.update_hook = lambda: None

        # Core subsystems
        self.renderer = Renderer()
        self.console  = ConsoleController()

    def register_hooks(self, init=None, update=None):
        """Optionally provide custom init/update callbacks."""
        if init:
            self.init_hook = init
        if update:
            self.update_hook = update

    def update_cycle(self):
        # 1) user update hook
        self.update_hook()

        object_sprites = []

        # 2) clear old positions & apply object updates
        for o in list(self.objects):
            o['update'](o)
            if o.get('dead'):
                self.objects.remove(o)
            else:
                if 'sprite' in o.keys():
                    o['sprite'].set_position(o['x'], o['y'])
                    object_sprites.append(o['sprite'])
                idx = get_index(o['x'], o['y'])
                self.renderer.grid[idx] = o['char']

        # 3) animations
        for a in list(self.animations):
            a['t'] += 1
            a['draw'](a)

        # 4) sprites
        self.renderer.draw_sprites(self.sprites)
        self.renderer.draw_sprites(object_sprites)

        # 5) draw everything
        grid_start   = self.renderer.top_row + len(self.renderer.top_hud) + TOP_MARGIN
        self.renderer.draw_diff(grid_start)
        bottom_start = grid_start + SIZE_Y + BOTTOM_MARGIN
        self.renderer.draw_hud(self.renderer.bottom_hud, self.renderer.prev_bottom, bottom_start)

        # 6) handle terminal resize
        self.renderer.check_resize()

    def run(self):
        """Set up console, do a full redraw, call init hook, then loop."""
        self.console.setup()
        self.renderer.update_full()
        self.init_hook()

        try:
            while True:
                self.update_cycle()
                time.sleep(0.05)
        except KeyboardInterrupt:
            pass
        finally:
            self.console.restore()
            self.renderer.clear_screen()
            print("Shutting down…")


if __name__ == '__main__':
    game = Game()
    # e.g. game.register_hooks(init=your_init_fn, update=your_update_fn)
    game.run()
