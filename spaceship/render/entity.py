from __future__ import annotations
from abc import ABC, abstractmethod


import typing
if typing.TYPE_CHECKING:
    from ..game import Game
from ..utils.math import Vector
from ..render.sprite import Sprite

class Entity(ABC):
    def __init__(self, game: "Game" , position: Vector = Vector(), type = ''):
        self.game  = game
        self._position = position
        self._type = type
        self._sprite = Sprite()

    @property
    def position(self):
        return self._position
    @position.setter
    def position(self, value):
        self._position = value
        self._sprite.position = value

    @property
    def sprite(self):
        return self._sprite
    @sprite.setter
    def sprite(self, value: Sprite):
        self._sprite = value
        self._sprite.position = self.position

    @property
    def type(self):
        return self._type
    
    def kill(self):
        self.game.remove_entity(self)

    @abstractmethod
    def update(self):
        pass

    def render(self) -> Sprite:
        return self.sprite