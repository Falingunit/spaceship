from spaceship.render.entity import Entity
from spaceship.game import Game
from spaceship.input.input import *
from spaceship.render.hud import HUDAlignment, HUDElement
from spaceship.render.camera import CameraMode
from spaceship.utils.math import Vector
from spaceship.utils.constants import *

class Rock(Entity):
	
	def __init__(self, game: Game, position: Vector = Vector()):
		super().__init__(game, position)
		self.sprite.load((
"""
⢀⡴⠑⡄⠀⠀⠀⠀⠀⠀⠀⣀⣀⣤⣤⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ 
⠸⡇⠀⠿⡀⠀⠀⠀⣀⡴⢿⣿⣿⣿⣿⣿⣿⣿⣷⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠑⢄⣠⠾⠁⣀⣄⡈⠙⣿⣿⣿⣿⣿⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⢀⡀⠁⠀⠀⠈⠙⠛⠂⠈⣿⣿⣿⣿⣿⠿⡿⢿⣆⠀⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⢀⡾⣁⣀⠀⠴⠂⠙⣗⡀⠀⢻⣿⣿⠭⢤⣴⣦⣤⣹⠀⠀⠀⢀⢴⣶⣆ 
⠀⠀⢀⣾⣿⣿⣿⣷⣮⣽⣾⣿⣥⣴⣿⣿⡿⢂⠔⢚⡿⢿⣿⣦⣴⣾⠁⠸⣼⡿ 
⠀⢀⡞⠁⠙⠻⠿⠟⠉⠀⠛⢹⣿⣿⣿⣿⣿⣌⢤⣼⣿⣾⣿⡟⠉⠀⠀⠀⠀⠀ 
⠀⣾⣷⣶⠇⠀⠀⣤⣄⣀⡀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀ 
⠀⠉⠈⠉⠀⠀⢦⡈⢻⣿⣿⣿⣶⣶⣶⣶⣤⣽⡹⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⠀⠉⠲⣽⡻⢿⣿⣿⣿⣿⣿⣿⣷⣜⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣷⣶⣮⣭⣽⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⣀⣀⣈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠻⠿⠿⠿⠿⠛⠉
"""
))
		self.sprite.load(
"""
  _._
.'--.`.
|  \t.' |
 `--`'
"""
		)
		
		self.position = Vector(10, 0)
		self.velocity = Vector()

	def update(self, dt):
		
		held_keys = self.game.input.keys_held

		speed = 2

		if 's' in held_keys:
			self.velocity += Vector(0, 1) * speed
		if 'w' in held_keys:
			self.velocity += Vector(0, -1) * speed
		if 'a' in held_keys:
			self.velocity += Vector(-1, 0) * speed
		if 'd' in held_keys:
			self.velocity += Vector(1, 0) * speed

		self.velocity += Vector(0, 20) * dt
		if self.position.y >= SIZE_Y - 6:
			self.position.y = SIZE_Y - 6
			self.velocity.y *= -0.5

		self.position += self.velocity * dt

		return super().update(dt)

class SpaceInveders():
	def __init__(self):
		self.game = Game(init_hook = self.init, update_hook = self.update, border = True)
		self.game.run()



	def init(self):
		self.game.add_entity(Rock(self.game, Vector(10, 10)))

		self.game.camera.mode = CameraMode.CENTER

		self.game.hud.add_top_hud(
			HUDElement(
				template='Player Name: `player_name`',
				values={'player_name': 'Player1'},
				align=HUDAlignment.CENTER
			))
		self.game.hud.add_bottom_hud(
			HUDElement(
				template='Score: `score`',
				values={'score': '0'},
				align=HUDAlignment.RIGHT
			))

	def update(self, dt: float):
		held_keys = self.game.input.keys_held

		if 'q' in held_keys:
			exit()
if __name__ == '__main__':
	SpaceInveders()