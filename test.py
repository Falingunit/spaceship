from spaceship.render.entity import Entity
from spaceship.game import Game
from spaceship.input.input import *
from spaceship.utils.math import Vector

class Rock(Entity):
	
	def __init__(self, game: Game, position: Vector = Vector(), type=''):
		super().__init__(game, position, type)
		self.sprite.load("      _____      \n"
						 "   .-'     '-.   \n"
						 "  /   ~`      \\  \n"
						 " |   `         |\n"
						 " |    _____    |\n"
						 " \\   /     \\  /\n"
						 "  '-.\t###   /~- \n"
						 "     '-----~`     ")
		
		self.position = Vector(10, 0)

	def update(self):
		
		held_keys = self.game.input.keys_held

		if 's' in held_keys:
			self.position += Vector(0, 1)
		if 'w' in held_keys:
			self.position += Vector(0, -1)
		if 'a' in held_keys:
			self.position += Vector(-1, 0)
		if 'd' in held_keys:
			self.position += Vector(1, 0)		
		
		return super().update()

game = Game()

def init():
	game.add_entity(Rock(game, type='rock'))

def update():
	pass

if __name__ == '__main__':
	game.register_hooks(init = init, update = update)
	game.run()