import time

from .render.camera import Camera
from .input.input import *
from .utils.math import Vector
from .utils.constants import SIZE_X, SIZE_Y, TOP_MARGIN, BOTTOM_MARGIN
from .render.render import Renderer
from .render.entity import Entity
class Game:
    def __init__(self):

        # Set up all the lists for entities
        self.entities: list[Entity] = []

        # User‐defined hooks (can be replaced)
        self.init_hook   = lambda: None
        self.update_hook = lambda: None

        # Core subsystems
        self.renderer = Renderer()
        self.input  = Input()
        self.camera = Camera()

        self.renderer.top_hud.clear()
        self.renderer.bottom_hud.clear()

        self.renderer.update_full()

    def register_hooks(self, init=None, update=None):
        if init:
            self.init_hook = init
        if update:
            self.update_hook = update

    # Functions for adding and removing entities
    def add_entity(self, entity: Entity) -> Entity:
        self.entities.append(entity)
        return entity
    def remove_entity(self, entity: Entity):
        self.entities.remove(entity)

    def update_cycle(self):

        self.input.make_dirty()

        # 1) user update hook
        self.update_hook()

        # 2) Update all objects
        for o in list(self.entities):
            o.update()

        # 3) Draw everything
        grid_start   = self.renderer.top_row + len(self.renderer.top_hud) + TOP_MARGIN
        self.renderer.draw_diff(grid_start, self.camera.get_render(Vector(SIZE_X, SIZE_Y), self.entities))
        bottom_start = grid_start + SIZE_Y + BOTTOM_MARGIN
        self.renderer.draw_hud(self.renderer.bottom_hud, self.renderer.prev_bottom, bottom_start)

        # 6) Handle terminal resize
        self.renderer.check_resize()
        
    def run(self):

        # Clear screen and call init_hoot
        self.renderer.update_full()
        self.init_hook()

        # Main loop
        try:
            while True:
                self.update_cycle()
                time.sleep(0.05)
        except KeyboardInterrupt:
            pass
        finally:
            self.renderer.clear_screen()
            print("Shutting down…")