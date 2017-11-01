import pygame as pg
from random import uniform, choice, randint, random
import settings as st
from tilemap import collide_hit_rect
import pytweening as tween
from itertools import chain
from pygame.math import Vector2 as vec
from itertools import cycle


def collide_with_walls(sprite, group, dir):
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2    
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = st.PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_img[0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = st.PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.rot = 0
        self.last_shot = 0
        self.last_anim = 0
        self.current_image = self.game.player_img[0]
        self.pool = cycle(self.game.player_img)
        self.health = st.PLAYER_HEALTH
        self.weapon = 'pistol'
        self.damaged = False

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.last_anim > 20:
            self.current_image = next(self.pool)
            self.last_anim = now

    def get_keys(self):
        self.rot_speed = 0
        self.vel = vec(0, 0)

        keys = pg.key.get_pressed()

        if keys[pg.K_LEFT]:
            self.rot_speed = st.PLAYER_ROT_SPEED
            self.game.set_mask(self.rot)

        elif keys[pg.K_RIGHT]:
            self.rot_speed = -st.PLAYER_ROT_SPEED
            self.game.set_mask(self.rot)

        elif keys[pg.K_UP]:
            self.vel = vec(st.PLAYER_SPEED, 0).rotate(-self.rot)

        elif keys[pg.K_DOWN]:
            self.vel = vec(-st.PLAYER_SPEED / 2, 0).rotate(-self.rot)

        elif keys[pg.K_SPACE]:
            self.shoot()

        if any([keys[pg.K_DOWN], keys[pg.K_UP], keys[pg.K_LEFT], keys[pg.K_RIGHT]]):
            self.animate()

    def shoot(self):
        now = pg.time.get_ticks()
        if now - self.last_shot > st.WEAPONS[self.weapon]['rate']:
            self.last_shot = now
            dir = vec(1, 0).rotate(-self.rot)
            pos = self.pos + st.BARREL_OFFSET.rotate(-self.rot)
            self.vel = vec(-st.WEAPONS[self.weapon]
                           ['kickback'], 0).rotate(-self.rot)
            for i in range(st.WEAPONS[self.weapon]['bullet_count']):
                spread = uniform(-st.WEAPONS[self.weapon]
                                 ['spread'], st.WEAPONS[self.weapon]['spread'])
                Bullet(self.game, pos, dir.rotate(spread),
                       st.WEAPONS[self.weapon]['damage'])
                snd = self.game.weapon_sounds[self.weapon]
                if snd.get_num_channels() > 2:
                    snd.stop()
                snd.play()
            MuzzleFlash(self.game, pos)

    def hit(self):
        self.damaged = True
        self.damage_alpha = chain(st.DAMAGE_ALPHA * 4)

    def update(self):
        self.get_keys()
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360

        self.image = pg.transform.rotate(self.current_image, self.rot)

        if self.damaged:
            try:
                self.image.fill((255, 255, 255, next(
                    self.damage_alpha)), special_flags=pg.BLEND_RGBA_MULT)
            except:
                self.damaged = False
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center

    def add_health(self, amount):
        self.health += amount
        if self.health > st.PLAYER_HEALTH:
            self.health = st.PLAYER_HEALTH


class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = st.MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob_img[0].copy()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = st.MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.rot = 0
        self.health = st.MOB_HEALTH
        self.speed = choice(st.MOB_SPEEDS)
        self.target = game.player
        self.last_anim = 0
        self.current_image = game.mob_img[0]
        self.pool = cycle(game.mob_img)

    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < st.AVOID_RADIUS:
                    self.acc += dist.normalize()

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.last_anim > 20:
            self.current_image = next(self.pool)
            self.last_anim = now

    def update(self):
        target_dist = self.target.pos - self.pos
        if target_dist.length_squared() < st.DETECT_RADIUS**2:
            if random() < 0.002:
                choice(self.game.zombie_moan_sounds).play()
            self.rot = target_dist.angle_to(vec(1, 0))
            # self.image = pg.transform.rotate(self.game.mob_img, self.rot)
            self.image = pg.transform.rotate(self.current_image, self.rot)
            self.rect.center = self.pos
            self.acc = vec(1, 0).rotate(-self.rot)
            self.avoid_mobs()
            self.acc.scale_to_length(self.speed)
            self.acc += self.vel * -1
            self.vel += self.acc * self.game.dt
            self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
            self.hit_rect.centerx = self.pos.x
            collide_with_walls(self, self.game.walls, 'x')
            self.hit_rect.centery = self.pos.y
            collide_with_walls(self, self.game.walls, 'y')
            self.rect.center = self.hit_rect.center
        if self.health <= 0:
            choice(self.game.zombie_hit_sounds).play()
            self.kill()
            self.game.map_img.blit(self.game.splat, self.pos - vec(32, 32))
        self.animate()

    def draw_health(self):
        if self.health > 60:
            col = st.GREEN
        elif self.health > 30:
            col = st.YELLOW
        else:
            col = st.RED
        width = int(self.rect.width * self.health / st.MOB_HEALTH)
        self.health_bar = pg.Rect(0, 0, width, 7)
        if self.health < st.MOB_HEALTH:
            pg.draw.rect(self.image, col, self.health_bar)


class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir, damage):
        self._layer = st.BULLET_LAYER
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.bullet_images[st.WEAPONS[game.player.weapon]['bullet_size']]
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = vec(pos)
        self.dir = dir
        self.rect.center = pos
        #spread = uniform(-GUN_SPREAD, GUN_SPREAD)
        self.vel = dir * \
            st.WEAPONS[game.player.weapon]['bullet_speed'] * uniform(0.9, 1.1)
        self.spawn_time = pg.time.get_ticks()
        self.damage = damage

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        if pg.time.get_ticks() - self.spawn_time > st.WEAPONS[self.game.player.weapon]['bullet_lifetime']:
            self.kill()


class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y


class MuzzleFlash(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self._layer = st.EFFECTS_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        size = randint(20, 50)
        self.image = pg.transform.scale(choice(game.gun_flashes), (size, size))
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = pos
        self.rect.center = pos
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        if pg.time.get_ticks() - self.spawn_time > st.FLASH_DURATION:
            self.kill()


class Item(pg.sprite.Sprite):
    def __init__(self, game, pos, type, link=None):
        self._layer = st.ITEMS_LAYER
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.item_images[type]
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.type = type
        self.link = link
        self.pos = pos
        self.rect.center = pos
        self.tween = tween.easeInOutSine
        self.step = 0
        self.dir = 1

    def update(self):
        # bobbing motion
        # offset = st.BOB_RANGE * (self.tween(self.step / st.BOB_RANGE) - 0.5)
        # self.rect.centery = self.pos.y + offset * self.dir
        # self.step += st.BOB_SPEED
        # if self.step > st.BOB_RANGE:
        #     self.step = 0
        #     self.dir *= -1
        pass


class Door(pg.sprite.Sprite):
    def __init__(self, game, pos, type, image, link=None):
        self._layer = st.ITEMS_LAYER
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = image # game.item_images[type]
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.rect_origin = self.rect
        self.type = type
        self.link = link
        self.pos = pos
        self.rect.center = pos
        self.tween = tween.easeInOutSine
        self.step = 0
        self.dir = 1
        self.rot = 0
        self.rot_speed = 5
        self.last_update = pg.time.get_ticks()
        self.new_image = image

    def animate(self):      
        # if self.rot < 90:
        #     now = pg.time.get_ticks()
        #     if now - self.last_update > 100:
        #         # self.current_image = next(self.pool)
        #         # self.last_anim = now
        #         # self.rot = (self.rot + self.rot_speed) % 360
        #         # self.image = pg.transform.rotate(self.image, self.rot)
        #         self.last_update = now
        #         self.rot = (self.rot + self.rot_speed) % 90
        #         self.new_image = pg.transform.rotate(self.image, self.rot)
        #         old_center = self.rect.center
        #         # self.image = new_image
        #         self.hit_rect = self.new_image.get_rect()
        #         # self.rect.center = old_center
        #         self.hit_rect.bottomright = self.rect_origin.bottomleft
        #         self.rect = self.hit_rect
        #         # self.new_image.bottomright = self.rect.bottomleft
        #         # self.hit_rect = self.rect
        # elif self.rot >= 90:
        #     self.rot = 0
        self.new_image = pg.transform.rotate(self.image, 90)
        self.hit_rect = self.new_image.get_rect()
        # self.hit_rect.height /=2
        self.hit_rect.topright = self.rect_origin.bottomleft
        
        self.rect = self.hit_rect

    def update(self):
        # self.animate()
        #pg.draw.rect(screen, WHITE, p_rect, 2)
        # bobbing motion
        # offset = st.BOB_RANGE * (self.tween(self.step / st.BOB_RANGE) - 0.5)
        # self.rect.centery = self.pos.y + offset * self.dir
        # self.step += st.BOB_SPEED
        # if self.step > st.BOB_RANGE:
        #     self.step = 0
        #     self.dir *= -1
        pass
    

class Light(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
