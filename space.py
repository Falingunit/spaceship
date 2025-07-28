import random
import json
import math
import sys

from spaceship.input.input import SIZE_X, SIZE_Y, CHAR_MAP, get_index
from spaceship.game import Game
from spaceship.logic.sprite import Sprite

# ————————————————————————————————————— SETUP ENGINE —————————————————————————————————————

game = Game()


# ————————————————————————————————————— HELPERS —————————————————————————————————————

def move_player(dx, dy, p):
    """Move player within grid bounds."""
    p['x'] = max(0, min(SIZE_X - 1, p['x'] + dx))
    p['y'] = max(0, min(SIZE_Y - 1, p['y'] + dy))


def distance(o1, o2):
    """Euclidean distance between two objects."""
    return math.hypot(o1['x'] - o2['x'], o1['y'] - o2['y'])


# Update engine character map
CHAR_MAP.update({
   #'a': '👾',
    'b': '⏺',
    'r': 'A',
    'e': '👽',
    '':  ' '
})


# ————————————————————————————————————— HUD ELEMENTS —————————————————————————————————————

title_element     = {"content": "TERMINAL INVADERS", "align": "c"}
max_score_element = {"content": "High Score: 0",     "align": "r"}
score_element     = {"content": "Score: 0",          "align": "r"}
energy_element    = {"content": "Energy: ",          "align": "r"}
health_element    = {"content": "Health: ",          "align": "l"}


# ————————————————————————————————————— STATE & SETTINGS —————————————————————————————————————

score = 0
spawn_asteroid = 0
spawn_alien    = 0

energy = 1.0
health = 1.0

settings = {
    "max_score": 0,
    # asteroid settings
    "asteroid_timer_min": 10,
    "asteroid_timer_max": 100,
    "asteroid_init_y_disp": 3,
    "asteroid_clump_size_min": 4,
    "asteroid_clump_size_max": 7,
    "asteroid_clump_size_y_disp": 4,
    "asteroid_blast_anim_base_delay": 0.25,
    "asteroid_blast_size_min": 4,
    "asteroid_blast_size_max": 7,
    "asteroid_blast_no_min": 4,
    "asteroid_blast_no_max": 5,
    "asteroid_move_frames": 5,
    # alien settings
    "alien_timer_min": 10,
    "alien_timer_max": 100,
    "alien_blast_anim_base_delay": 0.25,
    "alien_blast_size_min": 4,
    "alien_blast_size_max": 7,
    "alien_blast_no_min": 4,
    "alien_blast_no_max": 5,
    "alien_move_frames": 5,
    # HUD bars
    "energy_bar_size": 20,
    "health_bar_size": 20,
}


# ————————————————————————————————————— ANIMATIONS —————————————————————————————————————

def start_blast_animation(x, y, speed=1.0):
    game.animations.append({
        'x': x, 'y': y, 't': 0,
        'speed': speed, 'draw': draw_blast
    })


def draw_blast(a):
    """Frame-based blast effect."""
    blast_chars = ['●', '⏺', '⦿', '⦾', '⚬', '']
    idx = int(a['t'] * a['speed'])
    if idx >= len(blast_chars):
        game.animations.remove(a)
        return
    game.renderer.grid[get_index(a['x'], a['y'])] = blast_chars[idx]
    a['t'] += 1


# ————————————————————————————————————— INIT & END —————————————————————————————————————

def init():
    global settings
    # HUD setup
    game.renderer.top_hud.clear()
    game.renderer.top_hud.extend([title_element, score_element, max_score_element])
    game.renderer.bottom_hud.clear()
    game.renderer.bottom_hud.extend([energy_element, health_element])
    # full redraw
    game.renderer.update_full()

    # Load or initialize settings file
    try:
        with open("settings.dat", 'r') as f:
            loaded = json.load(f)
        for k in settings:
            settings[k] = loaded.get(k, settings[k])
    except (FileNotFoundError, json.JSONDecodeError):
        with open("settings.dat", 'w') as f:
            json.dump(settings, f, indent=1)

    # Update HUD values
    max_score_element["content"] = f"High Score: {settings['max_score']}"
    update_energy_bar()
    update_health_bar()

    summon_player()



def end():
    # Persist high score
    if score > settings['max_score']:
        settings['max_score'] = score
    with open("settings.dat", 'w') as f:
        json.dump(settings, f, indent=1)

    # Clean exit
    game.input.restore()
    game.renderer.clear_screen()
    sys.exit()


# ————————————————————————————————————— GAME LOGIC —————————————————————————————————————

def update():
    global spawn_asteroid, spawn_alien
    # Spawn asteroids
    spawn_asteroid -= 1
    if spawn_asteroid <= 0:
        spawn_asteroid = random.randint(
            settings['asteroid_timer_min'], settings['asteroid_timer_max']
        )
        clump = random.randint(
            settings['asteroid_clump_size_min'], settings['asteroid_clump_size_max']
        )
        x = random.randint(clump, SIZE_X - 1 - clump)
        y = random.randint(0, settings['asteroid_init_y_disp'])
        for _ in range(clump):
            dx = random.randint(-clump, clump)
            dy = random.randint(0, settings['asteroid_clump_size_y_disp'])
            summon_asteroid_pos(x + dx, y + dy)

    # Spawn aliens
    spawn_alien -= 1
    if spawn_alien <= 0:
        spawn_alien = random.randint(
            settings['alien_timer_min'], settings['alien_timer_max']
        )
        summon_alien()

    # HUD updates
    update_score_and_max_score()
    update_energy_bar()
    update_health_bar()


# Asteroid functions

def blast_asteroids(obj):
    global score, energy
    obj['dead'] = True
    start_blast_animation(
        obj['x'], obj['y'],
        settings['asteroid_blast_anim_base_delay'] + random.random()
    )
    radius = random.randint(
        settings['asteroid_blast_size_min'], settings['asteroid_blast_size_max']
    )
    for other in list(game.entities):
        if other['char'] in ('r','b') and distance(other, obj) <= radius:
            other['dead'] = True
            if other['char'] == 'r':
                score += 1
                energy = min(1.0, energy + 0.01)
            start_blast_animation(other['x'], other['y'])

    # Secondary blasts
    for _ in range(random.randint(
        settings['asteroid_blast_no_min'], settings['asteroid_blast_no_max']
    )):
        dx = random.randint(-radius, radius)
        dy = random.randint(-radius, radius)
        nx = max(0, min(SIZE_X - 1, obj['x'] + dx))
        ny = max(0, min(SIZE_Y - 1, obj['y'] + dy))
        start_blast_animation(nx, ny, settings['asteroid_blast_anim_base_delay'] + random.random())


def summon_asteroid():
    game.add_object({
        'x': random.randint(0, SIZE_X - 1),
        'y': 0, 'time': 0,
        'update': update_asteroid,
        'char': 'r', 'dead': False
    })


def summon_asteroid_pos(x, y):
    game.add_object({
        'x': x, 'y': y, 'time': 0,
        'update': update_asteroid,
        'char': 'r', 'dead': False
    })


def update_asteroid(a):
    global health
    a['time'] += 1
    if a['time'] > settings['asteroid_move_frames']:
        a['y'] += 1
        a['time'] = 0
    if a['y'] >= SIZE_Y:
        a['dead'] = True
        health = max(0.0, health - 0.05)


# Alien functions
def summon_alien():
    game.add_object({
        'x': random.randint(0, SIZE_X - 1),
        'y': 0, 'time': 0,
        'update': update_alien,
        'char': 'e', 'dead': False
    })


def update_alien(a):
    global health
    a['time'] += 1
    if a['time'] > settings['alien_move_frames']:
        a['y'] += 1
        a['time'] = 0
    if a['y'] >= SIZE_Y:
        a['dead'] = True
        health = max(0.0, health - 0.05)


# Player & bullets

def summon_player():
    sprite_raw = '/-----\\\n|--\t---|\n\\-----/'
    sprite = Sprite()
    sprite.load(sprite_raw)

    game.add_object({
        'x': random.randint(0, SIZE_X - 1),
        'y': SIZE_Y - 2,
        'update': update_player,
        'char': 'a',
        'sprite': sprite,
        'dead': False
    })

    sprite.position_x = game.entities[-1]['x']
    sprite.position_y = game.entities[-1]['y']


def update_player(p):
    global energy
    keys = game.input.get_keys_held()
    if 'q' in keys:
        end()
    if 'a' in keys or 'LEFT' in keys:
        move_player(-1, 0, p)
    if 'd' in keys or 'RIGHT' in keys:
        move_player(1, 0, p)
    if 'w' in keys or 'UP' in keys:
        summon_asteroid()
    if ' ' in keys:
        player_shoot(p)
    energy = min(1.0, energy + 0.0075)


def player_shoot(p):
    global energy
    if energy >= 0.1:
        energy -= 0.1
        summon_bullet(p)


def summon_bullet(p):
    game.add_object({
        'x': p['x'], 'y': p['y'] - 1,
        'update': update_bullet,
        'char': 'b', 'dead': False
    })


def update_bullet(b):
    if b['y'] - 1 < 0:
        b['dead'] = True
        return
    b['y'] -= 1
    for obj in list(game.entities):
        if obj['char'] == 'r' and obj['x'] == b['x'] and abs(obj['y'] - b['y']) <= 1:
            blast_asteroids(obj)
            b['dead'] = True
            break


# HUD update functions

def update_health_bar():
    bar = int(health * settings['health_bar_size'])
    health_element['content'] = (
        "Health: " +
        "#" * bar +
        " " * (settings['health_bar_size'] - bar) +
        "|"
    )


def update_energy_bar():
    bar = int(energy * settings['energy_bar_size'])
    energy_element['content'] = (
        "Energy: " +
        "#" * bar +
        " " * (settings['energy_bar_size'] - bar) +
        "|"
    )


def update_score_and_max_score():
    global score
    score_element['content'] = f"Score: {score}"
    if score > settings['max_score']:
        score_element['content'] = f"(NEW HIGH!) Score: {score}"


# ————————————————————————————————————— ENTRYPOINT —————————————————————————————————————

if __name__ == '__main__':
    # Wire up to engine hooks
    game.register_hooks(init=init, update=update)
    # Start game loop
    game.run()
