import pygame as pg
import pytmx
import settings as st

def collide_hit_rect(one, two):
    """ -> bool """
    return one.hit_rect.colliderect(two.rect)

class Map:
    def __init__(self, filename):
        self.data = []
        with open(filename, 'rt') as f:
            for line in f:
                self.data.append(line.strip())

        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth * st.TILESIZE
        self.height = self.tileheight * st.TILESIZE

class TiledMap:
    def __init__(self, filename):
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm

    def render(self, surface):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth,
                                            y * self.tmxdata.tileheight))

    def make_map(self):
        """ -> pg.Surface """
        temp_surface = pg.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface

class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        """ -> pg.Rect """
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        """ -> pg.Rect """
        return rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(st.WIDTH / 2)
        y = -target.rect.centery + int(st.HEIGHT / 2)

        # limit scrolling to map size
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(self.width - st.WIDTH), x)  # right
        y = max(-(self.height - st.HEIGHT), y)  # bottom
        self.camera = pg.Rect(x, y, self.width, self.height)
