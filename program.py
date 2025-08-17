from spaceship.game import Game
from spaceship.render.entity import Entity
from spaceship.utils import constants
from spaceship.utils.math import Vector

import random

class SnowParticle(Entity):
	
	def __init__(self, game: Game, position: Vector = Vector(), speed: Vector = Vector(), char=''):
		super().__init__(game, position)
		self.sprite.load((char))
		
		self.position = Vector(10, 0)
		self.speed = speed

	def update(self, dt):
		
		held_keys = self.game.input.keys_held

		self.position += self.speed * dt
		
		return super().update(dt)

class SnowScape:
	def __init__(self):
		self.game = Game(init_hook=self.init, update_hook=self.update)
		self.game.run()
	
	def init(self):
		for i in range(random.randint(50, 100)):
			
			  

	def update(self, dt: float):
		pass

if __name__ == '__main__':
	constants.SIZE_X = 100
	constants.SIZE_Y = 30
	SnowScape()