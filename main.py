import pygame as pg
import sys
from random import choice, random
from os import path
import settings as st
import sprites as sp
import tilemap as tm


class Game:
    def __init__(self):
        pg.mixer.pre_init(44100, -16, 4, 2048)
        pg.init()
        self.screen = pg.display.set_mode((st.WIDTH, st.HEIGHT))
        pg.display.set_caption(st.TITLE)
        self.clock = pg.time.Clock()
        self.game_folder = path.dirname(__file__)
        self.img_folder = path.join(self.game_folder, 'img')
        self.snd_folder = path.join(self.game_folder, 'snd')
        self.music_folder = path.join(self.game_folder, 'music')
        self.map_folder = path.join(self.game_folder, 'maps')
        self.title_font = path.join(self.img_folder, 'ZOMBIE.TTF')
        self.hud_font = path.join(self.img_folder, 'Impacted2.0.ttf')
        self.player_rot = 0
        self.previous_room = None
        self.current_room = 'map1.tmx'
        self.next_room =''
        self.room_switch = False
        self.initial = True
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))

    def draw_text(self, text, font_name, size, color, x, y):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center= (x, y))
        self.screen.blit(text_surface, text_rect)

    def set_mask(self, rot=None):
        self.fog = pg.Surface((st.WIDTH, st.HEIGHT))
        self.fog.fill(st.NIGHT_COLOR)
        if rot is None:
            self.light_mask = pg.image.load(
                path.join(self.img_folder, st.LIGHT_MASK)).convert_alpha()
            self.light_rect = self.light_mask.get_rect()
        else:
            self.light_mask = pg.image.load(
                path.join(self.img_folder, st.LIGHT_MASK)).convert_alpha()
            self.light_mask = pg.transform.rotate(self.light_mask, rot)
            self.light_rect = self.light_mask.get_rect()

    def load_image(self):
        # self.player_img = pg.image.load(path.join(self.img_folder, st.PLAYER_IMG)).convert_alpha()
        self.bullet_images = {}
        self.bullet_images['lg'] = pg.image.load(path.join(self.img_folder, st.BULLET_IMG)).convert_alpha()
        self.bullet_images['sm'] = pg.transform.scale(self.bullet_images['lg'], (10, 10))
        self.mob_img = pg.image.load(path.join(self.img_folder, st.MOB_IMG)).convert_alpha()
        self.splat = pg.image.load(path.join(self.img_folder, st.SPLAT)).convert_alpha()
        self.splat = pg.transform.scale(self.splat, (64, 64))

        self.player_img = []
        for img in st.PLAYER_IMG:
            self.player_img.append(pg.image.load(path.join(self.img_folder, img)).convert_alpha())

        self.gun_flashes = []
        for img in st.MUZZLE_FLASHES:
            self.gun_flashes.append(pg.image.load(path.join(self.img_folder, img)).convert_alpha())

        self.item_images = {}
        for item in st.ITEM_IMAGES:
            self.item_images[item] = pg.image.load(path.join(self.img_folder, st.ITEM_IMAGES[item])).convert_alpha()

    def load_sound(self):
        # Sound loading
        pg.mixer.music.load(path.join(self.music_folder, st.BG_MUSIC))
        self.effects_sounds = {}
        for mytype in st.EFFECTS_SOUNDS:
            self.effects_sounds[mytype] = pg.mixer.Sound(
                path.join(self.snd_folder, st.EFFECTS_SOUNDS[mytype]))
        self.weapon_sounds = {}
        for weapon in st.WEAPON_SOUNDS:
            self.weapon_sounds[weapon] = []
            for snd in st.WEAPON_SOUNDS[weapon]:
                s = pg.mixer.Sound(path.join(self.snd_folder, snd))
                s.set_volume(0.1)
                self.weapon_sounds[weapon].append(s)
        self.zombie_moan_sounds = []
        for snd in st.ZOMBIE_MOAN_SOUNDS:
            s = pg.mixer.Sound(path.join(self.snd_folder, snd))
            s.set_volume(0.2)
            self.zombie_moan_sounds.append(s)
        self.player_hit_sounds = []
        for snd in st.PLAYER_HIT_SOUNDS:
            self.player_hit_sounds.append(
                pg.mixer.Sound(path.join(self.snd_folder, snd)))
        self.zombie_hit_sounds = []
        for snd in st.ZOMBIE_HIT_SOUNDS:
            s = pg.mixer.Sound(path.join(self.snd_folder, snd))
            s.set_volume(0.1)
            self.zombie_hit_sounds.append(s)

    def new(self, map_name = None):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.load_image()
        self.load_sound()
        self.player = sp.Player(self, 128, 128)
        self.player.rot = self.player_rot # remember facing direction when entering new rooms
        self.load_map(map_name)
        self.camera = tm.Camera(self.map.width, self.map.height)
        self.set_mask() # torchlight
        self.draw_debug = False
        self.paused = False
        self.night = False

    def load_map(self, map_name):
        if map_name is None:
            # initial map loading
            self.map = tm.TiledMap(path.join(self.map_folder, 'map1.tmx'))
            self.current_room = 'map1.tmx'
        else:
            # dynamic map loading
            self.map = tm.TiledMap(path.join(self.map_folder, map_name))
            self.current_room = map_name

        self.map_img = self.map.make_map()
        self.map.rect = self.map_img.get_rect()

        for tmx_obj in self.map.tmxdata.objects:

            center_x = (tmx_obj.x + tmx_obj.width / 2)
            center_y = (tmx_obj.y + tmx_obj.height / 2)
            obj_center = sp.vec(center_x, center_y)

            if tmx_obj.name == 'door':
                sp.Item(self, obj_center, tmx_obj.name, tmx_obj.link)
                if tmx_obj.link+'.tmx' == self.previous_room:
                    newpos = self.pos_in_newmap(tmx_obj)
                    self.player.pos = sp.vec(newpos)
                    self.room_switch = False

            if tmx_obj.name == 'zombie':
                sp.Mob(self, obj_center.x, obj_center.y)

            if tmx_obj.name == 'wall':
                sp.Obstacle(self, tmx_obj.x, tmx_obj.y, tmx_obj.width, tmx_obj.height)

            if tmx_obj.name in ['health', 'shotgun']:
                sp.Item(self, obj_center, tmx_obj.name)

    def pos_in_newmap(self, door):
        tempx = 0
        tempy = 0
        # door on left side
        if door.x == 0:
            tempx = (door.x + 128)
            tempy = (door.y + 64)
        # door on top side
        elif door.x > 0 and door.y == 0:
            tempx = (door.x + 64)
            tempy = (door.y + 128)
        # door on bottom side
        elif door.x > 0 and door.y == self.map.height - 64:
            tempx = (door.x + 64)
            tempy = (door.y - 64)
        # door on right side
        elif door.x == self.map.width - 64 and door.y > 0:
            tempx = (door.x - 64)
            tempy = (door.y + 64)

        newpos = (tempx, tempy)
        return newpos

    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        pg.mixer.music.play(loops=-1)
        while self.playing:
            self.dt = self.clock.tick(st.FPS) / 1000.0  # fix for Python 2.x
            self.events()
            if not self.paused:
                if not self.room_switch:
                    self.update()
            self.draw()

    def quit(self):
        self.playing = False
        pg.quit()
        sys.exit()

    def hit_item(self):
        # player hits items
        hits = pg.sprite.spritecollide(self.player, self.items, False)
        for hit in hits:

            if hit.type == 'health' and self.player.health < st.PLAYER_HEALTH:
                hit.kill()
                self.effects_sounds['health_up'].play()
                self.player.add_health(st.HEALTH_PACK_AMOUNT)

            if hit.type == 'door' and not self.room_switch:
                new_map = hit.link+'.tmx'
                if path.exists(path.join(self.map_folder, new_map)):
                    self.room_switch = True
                    self.previous_room = self.current_room
                    self.next_room = new_map
                    self.player_rot = self.player.rot
                    self.new(new_map)
                else:
                    print(f"room ---{new_map} doesn't exist yet")

    def hit_mob(self):
        if self.player:
            # mobs hit player
            hits = pg.sprite.spritecollide(self.player, self.mobs, False, tm.collide_hit_rect)
            for hit in hits:
                if random() < 0.7:
                    choice(self.player_hit_sounds).play()
                self.player.health -= st.MOB_DAMAGE
                hit.vel = sp.vec(0, 0)
                if self.player.health <= 0:
                    self.playing = False
            if hits:
                self.player.hit()
                self.player.pos += sp.vec(st.MOB_KNOCKBACK, 0).rotate(-hits[0].rot)

    def hit_bullet(self):
        # bullets hit mobs
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for mob in hits:
            # hit.health -= WEAPONS[self.player.weapon]['damage']
            #            * len(hits[hit])
            for bullet in hits[mob]:
                mob.health -= bullet.damage
                # mob.vel += sp.vec(bullet.dir[0]*100, bullet.dir[1]*100)
            # mob gets stopped
            mob.vel = sp.vec(0, 0)
            # mob get knockback from bullet
            mob.pos += sp.vec(bullet.dir[0]*10, bullet.dir[1]*10)

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()
        self.camera.update(self.player)
        self.hit_item()
        self.hit_mob()
        self.hit_bullet()

    def render_fog(self):
        # draw the light mask (gradient) onto fog image
        self.fog.fill(st.NIGHT_COLOR)
        self.light_rect.center = self.camera.apply(self.player).center
        self.fog.blit(self.light_mask, self.light_rect)
        self.screen.blit(self.fog, (0, 0), special_flags=pg.BLEND_MULT)

    def draw(self):
        # pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        self.screen.blit(self.map_img, self.camera.apply(self.map))
        for sprite in self.all_sprites:
            if isinstance(sprite, sp.Mob):
                sprite.draw_health()
                if self.draw_debug:
                    my_x = self.camera.apply(sprite).centerx
                    my_y = self.camera.apply(sprite).centery
                    pg.draw.circle(self.screen, st.RED, (my_x, my_y), st.DETECT_RADIUS, 2)
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            if self.draw_debug:
                self.draw_text("{:.2f}".format(self.clock.get_fps()), self.hud_font, 30, st.WHITE, 50, 30)
                pg.draw.rect(self.screen, st.CYAN, self.camera.apply_rect(sprite.hit_rect), 1)
        if self.draw_debug:
            for wall in self.walls:
                pg.draw.rect(self.screen, st.CYAN, self.camera.apply_rect(wall.rect), 1)
        if self.night:
            self.render_fog()
        if self.paused:
            self.screen.blit(self.dim_screen, (0, 0))
            self.draw_text('Zombies: {}'.format(len(self.mobs)),
                            self.hud_font, 30, st.WHITE, st.WIDTH - 100, 10)
        pg.display.flip()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_h:
                    self.draw_debug = not self.draw_debug
                if event.key == pg.K_p:
                    self.paused = not self.paused
                if event.key == pg.K_n:
                    self.night = not self.night
                if event.key == pg.K_f:
                    if pg.display.get_driver()=='x11':
                        pg.display.toggle_fullscreen()
                if event.key == pg.K_d:
                    # debug output:
                    print("all_sprite_size={}".format(len(self.all_sprites.sprites())))
                    print(f"current_room={self.current_room} || previous_room={self.previous_room}")
                    print(f"self.player_rot={self.player_rot}")
                    mob_nbr = 0
                    player_nbr = 0
                    for sprite in self.all_sprites:
                        if isinstance(sprite, sp.Player):
                            player_nbr +=1
                        if isinstance(sprite, sp.Mob):
                            mob_nbr +=1
                            print(f"mob_nbr={mob_nbr}\
                                    || player_nbr={player_nbr}\
                                    || target_pos={sprite.target.pos}\
                                    || player_pos={self.player.pos}")

    def show_start_screen(self):
        pass

    def show_go_screen(self):
        self.screen.fill(st.BLACK)
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        pg.event.wait()
        waiting = True
        while waiting:
            self.clock.tick(st.FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP:
                    waiting = False


# create the game object
g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
    g.show_go_screen()
