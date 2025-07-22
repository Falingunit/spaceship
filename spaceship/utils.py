import ctypes
from ctypes import wintypes

# --- Global settings ---
SIZE_X, SIZE_Y = 30, 30
CELL_WIDTH = 2
LEFT_MARGIN, RIGHT_MARGIN = 4, 4
TOP_MARGIN, BOTTOM_MARGIN = 1, 1

# Virtual-Key codes
VK_LEFT, VK_UP, VK_RIGHT, VK_DOWN, VK_SPACE = 0x25, 0x26, 0x27, 0x28, 0x20

# Character map for custom drawing (map grid values to chars)
CHAR_MAP = {}

# --- WinAPI handles for console mode ---
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
GetStdHandle    = kernel32.GetStdHandle
GetConsoleMode  = kernel32.GetConsoleMode
SetConsoleMode  = kernel32.SetConsoleMode
FlushConsoleInputBuffer = kernel32.FlushConsoleInputBuffer

STD_INPUT_HANDLE     = -10
ENABLE_ECHO_INPUT    = 0x0004
ENABLE_LINE_INPUT    = 0x0002

# --- Input polling via GetAsyncKeyState ---
user32 = ctypes.WinDLL('user32', use_last_error=True)
GetAsyncKeyState = user32.GetAsyncKeyState
GetAsyncKeyState.argtypes = (wintypes.INT,)
GetAsyncKeyState.restype  = wintypes.SHORT

def get_index(x, y):
    return x + y * SIZE_X

class ConsoleController:
    """Handles console mode setup, teardown, and key polling."""
    def __init__(self):
        self.hStdin = GetStdHandle(STD_INPUT_HANDLE)
        self._old_mode = wintypes.DWORD()
    
    def setup(self):
        """Disable echo & line-buffering for real-time key reads."""
        if not GetConsoleMode(self.hStdin, ctypes.byref(self._old_mode)):
            raise ctypes.WinError(ctypes.get_last_error())
        new_mode = self._old_mode.value & ~(ENABLE_ECHO_INPUT | ENABLE_LINE_INPUT)
        if not SetConsoleMode(self.hStdin, new_mode):
            raise ctypes.WinError(ctypes.get_last_error())

    def restore(self):
        """Restore original console settings and clear input."""
        SetConsoleMode(self.hStdin, self._old_mode.value)
        FlushConsoleInputBuffer(self.hStdin)

    def get_keys_held(self):
        """Polls and returns a list of currently pressed keys."""
        held = []
        # WASD
        for code, name in [(ord('A'), 'a'), (ord('S'), 's'),
                           (ord('W'), 'w'), (ord('D'), 'd')]:
            if GetAsyncKeyState(code) & 0x8000:
                held.append(name)

        # Arrows and space
        for vk, name in [(VK_LEFT, 'LEFT'), (VK_RIGHT, 'RIGHT'),
                         (VK_UP, 'UP'), (VK_DOWN, 'DOWN'),
                         (VK_SPACE, ' ')]:
            if GetAsyncKeyState(vk) & 0x8000:
                held.append(name)

        # Quit
        if GetAsyncKeyState(ord('Q')) & 0x8000:
            held.append('q')

        return held
