from __future__ import annotations

from spaceship.game import Game
from spaceship.render.camera import CameraMode
from spaceship.render.entity import Entity
from spaceship.render.hud import HUDAlignment, HUDElement
from spaceship.save import Manager
from spaceship.utils.constants import SIZE_Y
from spaceship.utils.math import Vector

# Fill these values to enable MySQL-backed saves.
DB_CONFIG = {
	"host": "localhost",
	"user": "root",
	"password": "91008",
	"database": "qwe",
}


class Rock(Entity):
	def __init__(self, game: Game, bounce_hook, velocity_hud: HUDElement, position: Vector = Vector()):
		super().__init__(game, position)
		self.vel_hud = velocity_hud
		self.bounce_hook = bounce_hook
		self.sprite.load((
"""
               _._
             .'--.`.
             |  .' |
              `-\t-`'
"""
))		
		self.position = Vector(10, 0)
		self.velocity = Vector()

	def update(self, dt):
		
		held_keys = self.game.input.is_char_held

		speed = 2

		if held_keys('s'):
			self.velocity += Vector(0, 1) * speed
		if held_keys('w'):
			self.velocity += Vector(0, -1) * speed
		if held_keys('a'):
			self.velocity += Vector(-1, 0) * speed
		if held_keys('d'):
			self.velocity += Vector(1, 0) * speed

		self.velocity += Vector(0, 20) * dt
		if self.position.y >= SIZE_Y - 2:
			self.position.y = SIZE_Y - 2
			self.velocity.y *= -1
			self.bounce_hook()

		self.vel_hud.set_value('x', str(int(self.velocity.x)))
		self.vel_hud.set_value('y', str(int(self.velocity.y)))

		self.position += self.velocity * dt

		return super().update(dt)

class DemoGame:
	def __init__(self):
		self.profile_id: int | None = None
		self.bounce_count = 0
		self.input_hook_registered = False
		self.save_manager = self._create_save_manager()
		self.game = Game(init_hook=self.init, update_hook=self.update, border=True, database=self.save_manager)
		self.game.run()

	def _create_save_manager(self):
		if not all(DB_CONFIG.values()):
			print("Save system disabled: set DB_CONFIG to enable saving.")
			return None
		try:
			manager = Manager(**DB_CONFIG)
			manager.initialize_database()
			return manager
		except Exception as exc:
			print(f"Save system disabled: {exc}")
			return None

	def init(self):
		vel_hud = HUDElement(template='Velocity: (`x`,`y`)', values={'x': '0', 'y': '0'}, align=HUDAlignment.LEFT)
		self.rock = Rock(self.game, self.bounced, vel_hud, Vector(10, 10))
		self.game.add_entity(self.rock)

		self.game.camera.mode = CameraMode.CENTER

		self.game.hud.add_bottom_hud(vel_hud)
		self.game.hud.add_top_hud(
			HUDElement(
				template='Bounce',
				values={},
				align=HUDAlignment.CENTER
			))
		self.bottom_hud = HUDElement(
				template='Number of bounces: `score`',
				values={'score': '0'},
				align=HUDAlignment.RIGHT
		)
		self.game.hud.add_bottom_hud(self.bottom_hud)
		self._initialize_save_system()

	def bounced(self):
		self.bounce_count += 1
		self.bottom_hud.set_value('score', str(self.bounce_count))
		self._persist_state(event='bounce')

	def update(self, dt: float):
		if self.game.input.is_char_held('q'):
			self._persist_state(event='quit')
			exit()

	def _initialize_save_system(self):
		if not self.save_manager:
			return

		self.profile_id = self.save_manager.get_or_create_profile(
			'demo',
			{'description': 'Bouncing rock demo'},
		)

		if not self.input_hook_registered:
			self.game.input.hook_to_keypress(self._handle_keypress)
			self.input_hook_registered = True

		if not self._apply_saved_state():
			self._persist_state(event='init')

	# Keybindings for the save system: P = save, L = load, C = clear/reset.
	def _handle_keypress(self, key):
		try:
			char = key.char
		except AttributeError:
			return

		if char == 'p':
			self._persist_state(event='manual')
		elif char == 'l':
			self._apply_saved_state()
		elif char == 'c':
			self._reset_state()

	def _persist_state(self, event: str):
		if not (self.save_manager and self.profile_id is not None):
			return

		state = {
			'bounces': self.bounce_count,
			'position': {'x': self.rock.position.x, 'y': self.rock.position.y},
			'velocity': {'x': self.rock.velocity.x, 'y': self.rock.velocity.y},
		}
		self.save_manager.save_state(self.profile_id, state, event=event)

	def _apply_saved_state(self) -> bool:
		if not (self.save_manager and self.profile_id is not None):
			return False

		latest = self.save_manager.get_latest_state(self.profile_id)
		if latest is None:
			return False

		data = latest['data']
		self.bounce_count = int(data.get('bounces', 0))
		self.bottom_hud.set_value('score', str(self.bounce_count))

		pos = data.get('position', {})
		vel = data.get('velocity', {})
		self.rock.position = Vector(
			pos.get('x', self.rock.position.x),
			pos.get('y', self.rock.position.y),
		)
		self.rock.velocity = Vector(
			vel.get('x', self.rock.velocity.x),
			vel.get('y', self.rock.velocity.y),
		)
		return True

	def _reset_state(self):
		self.bounce_count = 0
		self.bottom_hud.set_value('score', '0')
		self.rock.position = Vector(10, 0)
		self.rock.velocity = Vector()

		if self.save_manager and self.profile_id is not None:
			self.save_manager.clear_profile_states(self.profile_id)
			self._persist_state(event='reset')
		
if __name__ == '__main__':
	DemoGame()
