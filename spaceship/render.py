import shutil
from sys import stdout

from spaceship.utils import *

class Renderer:
    """Manages the grid, HUD buffers, and efficient redraws."""
    def __init__(self):
        # Buffers
        self.grid      = [''] * (SIZE_X * SIZE_Y)
        self.prev_grid = [''] * (SIZE_X * SIZE_Y)
        self.prev_term = shutil.get_terminal_size()

        # HUD containers (populated by Game)
        self.top_hud    = []
        self.bottom_hud = []
        self.prev_top    = []
        self.prev_bottom = []

        # Row calculations
        self.top_row = 1

    def move_to(self, r, c):
        return f"\033[{r};{c}H"

    def clear_screen(self):
        stdout.write("\033[2J\033[H")
        stdout.flush()
    
    def draw_sprites(self, sprites):
        sprite_grid = [{'char': '', 'priority': 0}] * (SIZE_X * SIZE_Y)

        for sprite in sprites:
            for y, line in enumerate(sprite.decoded_string):
                for x, c in enumerate(line):
                    wrtc_x = x - sprite.center_x
                    wrtc_y = y - sprite.center_y

                    global_x = wrtc_x + sprite.position_x
                    global_y = wrtc_y + sprite.position_y

                    idx = get_index(global_x, global_y)
                    
                    if global_x < 0 or global_x >= SIZE_X:
                        continue
                    if global_y < 0 or global_y >= SIZE_Y:
                        continue

                    if (sprite_grid[idx])['priority'] < sprite.priority:
                        sprite_grid[idx] = {'char': c, 'priority': sprite.priority}
        
        for i, c in enumerate(sprite_grid):
            if not sprite_grid[i]['char'] == '':
                self.grid[i] = sprite_grid[i]['char'] + '\t'

    def draw_diff(self, grid_start):
        """Only redraw cells that changed since last frame."""
        stdout.write("\033[?25l")  # hide cursor
        for i, cell in enumerate(self.grid):
            if cell != self.prev_grid[i]:
                y, x = divmod(i, SIZE_X)
                r = grid_start + y
                c = LEFT_MARGIN + x * CELL_WIDTH + 1
                ch = CHAR_MAP.get(cell, cell)
                stdout.write(self.move_to(r, c) + ch)
                self.prev_grid[i] = cell
        stdout.flush()

        self.grid = [''] * (SIZE_X * SIZE_Y)

    def draw_hud(self, hud, prev_buf, start_row):
        """Render HUD entries (left/center/right aligned)."""
        counts = {'l': 0, 'c': 0, 'r': 0}
        for idx, entry in enumerate(hud):
            txt, align = entry['content'], entry['align']
            row = start_row + counts[align]
            counts[align] += 1

            # Only redraw if changed
            if idx < len(prev_buf) and txt != prev_buf[idx]:
                if align == 'l':
                    col = LEFT_MARGIN + 1
                elif align == 'c':
                    col = LEFT_MARGIN + (SIZE_X * CELL_WIDTH)//2 - len(txt)//2 + 1
                else:  # 'r'
                    col = LEFT_MARGIN + SIZE_X * CELL_WIDTH + RIGHT_MARGIN - len(txt) + 1

                stdout.write(self.move_to(row, col))
                stdout.write(' ' * max(len(prev_buf[idx]), len(txt)))
                stdout.write(self.move_to(row, col) + txt)
                prev_buf[idx] = txt

        stdout.flush()

    def update_full(self):
        """Full clear & redraw of HUD + grid + recalc term size."""
        self.prev_top    = [''] * len(self.top_hud)
        self.prev_bottom = [''] * len(self.bottom_hud)
        self.prev_term   = shutil.get_terminal_size()

        self.clear_screen()

        grid_start   = self.top_row + len(self.top_hud) + TOP_MARGIN
        bottom_start = grid_start + SIZE_Y + BOTTOM_MARGIN

        self.draw_hud(self.top_hud, self.prev_top,    self.top_row)
        self.draw_diff(grid_start)
        self.draw_hud(self.bottom_hud, self.prev_bottom, bottom_start)

    def check_resize(self):
        """Trigger a full redraw if the terminal size changed."""
        if shutil.get_terminal_size() != self.prev_term:
            self.update_full()
