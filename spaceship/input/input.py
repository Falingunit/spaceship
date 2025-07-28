import keyboard

class Input:
    def __init__(self) -> None:
        self._cache = []
        self._dirty = True

    def get_keys_held(self):

        held = []

        keys_to_check = (
            [chr(i) for i in range(32, 127)] +
            list(keyboard.all_modifiers)
        )

        for key in keys_to_check:
            try:
                if keyboard.is_pressed(key):
                    held.append(key)
            except:
                pass

        return held
    
    @property
    def keys_held(self):
        if self._dirty:
            self._cache = self.get_keys_held()
            self._dirty = False
        
        return self._cache

    def make_dirty(self):
        self._dirty = True