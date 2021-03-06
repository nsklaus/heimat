import pygame as pg
from pygame.math import Vector2 as vec


# ===========================================================================================
#  define some colors (R, G, B)
# ===========================================================================================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (106, 55, 5)
CYAN = (0, 255, 255)

# ===========================================================================================
#  game settings
# ===========================================================================================
WIDTH = 1024   # 16 * 64 or 32 * 32 or 64 * 16
HEIGHT = 768  # 16 * 48 or 32 * 24 or 64 * 12
FPS = 60
TITLE = "Tilemap Demo"
BGCOLOR = BROWN
TILESIZE = 16
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

# ===========================================================================================
#  Player settings
# ===========================================================================================
PLAYER_HEALTH = 100
PLAYER_SPEED = 280
PLAYER_ROT_SPEED = 200
PLAYER_IMG = ['survivor_handgun_0.png', 'survivor_handgun_1.png', 'survivor_handgun_3.png',
              'survivor_handgun_4.png', 'survivor_handgun_4.png', 'survivor_handgun_6.png',
              'survivor_handgun_7.png', 'survivor_handgun_8.png', 'survivor_handgun_9.png',
              'survivor_handgun_10.png', 'survivor_handgun_11.png', 'survivor_handgun_12.png',
              'survivor_handgun_13.png', 'survivor_handgun_14.png', 'survivor_handgun_15.png',
              'survivor_handgun_16.png', 'survivor_handgun_17.png', 'survivor_handgun_18.png',
              'survivor_handgun_19.png']
PLAYER_HIT_RECT = pg.Rect(0, 0, 35, 35)
BARREL_OFFSET = vec(50, 15)

# ===========================================================================================
#  Weapon settings
# ===========================================================================================
BULLET_IMG = 'bullet.png'
WEAPONS = {}
WEAPONS['pistol'] = {'bullet_speed': 500,
                     'bullet_lifetime': 1000,
                     'rate': 600,
                     'kickback': 200,
                     'spread': 5,
                     'damage': 20,
                     'bullet_size': 'lg',
                     'bullet_count': 1}
WEAPONS['shotgun'] = {'bullet_speed': 400,
                      'bullet_lifetime': 500,
                      'rate': 900,
                      'kickback': 300,
                      'spread': 20,
                      'damage': 5,
                      'bullet_size': 'sm',
                      'bullet_count': 12}

AMMO = 12
# ===========================================================================================
# Mob settings
# ===========================================================================================
MOB_IMG = [ 'zombie-move_0.png','zombie-move_1.png','zombie-move_2.png','zombie-move_3.png',
            'zombie-move_4.png','zombie-move_5.png','zombie-move_6.png','zombie-move_7.png',
            'zombie-move_8.png','zombie-move_9.png','zombie-move_10.png','zombie-move_11.png',
            'zombie-move_12.png','zombie-move_13.png','zombie-move_14.png','zombie-move_15.png',
            'zombie-move_16.png']
MOB_SPEEDS = [150, 100, 75, 125]
MOB_HIT_RECT = pg.Rect(0, 0, 30, 30)
MOB_HEALTH = 100
MOB_DAMAGE = 10
MOB_KNOCKBACK = 20
AVOID_RADIUS = 50
DETECT_RADIUS = 400

# ===========================================================================================
# Effects
# ===========================================================================================
MUZZLE_FLASHES = ['whitePuff15.png', 'whitePuff16.png', 'whitePuff17.png', 'whitePuff18.png']
SPLAT_IMG = 'splat green.png'
FLASH_DURATION = 50
DAMAGE_ALPHA = [i for i in range(0, 255, 55)]
NIGHT_COLOR = (60, 60, 60)
LIGHT_RADIUS = (500, 500)
LIGHT_MASK = "torch2.png" 

# ===========================================================================================
#  Layers
# ===========================================================================================
WALL_LAYER = 1
PLAYER_LAYER = 2
BULLET_LAYER = 3
MOB_LAYER = 2
EFFECTS_LAYER = 4
ITEMS_LAYER = 1

# ===========================================================================================
#  Doors
# ===========================================================================================
DOORS_IMG = 'doors.png'

# ===========================================================================================
#  Items
# ===========================================================================================
ITEM_IMG = {'health': 'health_pack.png',
            'shotgun': 'obj_shotgun.png',
            'key': 'key.png',
            'ammo': 'ammo.png'}
HEALTH_PACK_AMOUNT = 20
BOB_RANGE = 10
BOB_SPEED = 0.3
GOT_KEY = False
# ===========================================================================================
#  Sounds
# ===========================================================================================
ZOMBIE_MOAN_SOUNDS = ['brains2.ogg', 'brains3.ogg', 'zombie-roar-1.ogg', 'zombie-roar-2.ogg',
                      'zombie-roar-3.ogg','zombie-roar-6.ogg', 'zombie-roar-7.ogg', 
                      'zombie-roar-8.ogg']
PLAYER_HIT_SOUNDS = ['pain/8.ogg', 'pain/9.ogg', 'pain/10.ogg', 'pain/11.ogg']
ZOMBIE_HIT_SOUNDS = ['splat-15.ogg']
EFFECTS_SOUNDS = {'level_start': 'level_start.ogg',
                  'health_up': 'health_pack.ogg',
                  'gun_pickup': 'gun_pickup.ogg',
                  'door': 'door.ogg'}
WEAPON_SOUNDS = {'pistol': 'pistol.ogg',
                 'shotgun': 'shotgun.ogg'}
BG_MUSIC = 'espionage.ogg'

