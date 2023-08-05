import json
import math
import pygame
from numba import njit


class Sprite:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.dist = 0
        self.hitbox = pygame.Rect(self.x, self.y, 4, 4)

    def update(self, _, __, ___):
        self.hitbox = pygame.Rect(self.x, self.y, 4, 4)

    def to_json(self):
        return {
            "x_pos": self.x,
            "y_pos": self.y,
            "type": self.type
        }

    @classmethod
    def from_json(cls, json_data):
        return cls(
            x=json_data["x_pos"],
            y=json_data["y_pos"],
            type=json_data["type"],
        )


def render_sprites(sp_list, player, screen, type2sprite, level, projectiles, tile_map):

    for sp in sp_list:
        sp.dist = math.dist([sp.x, sp.y], [player.x, player.y])
        sp.update(sp_list, projectiles, tile_map)

    new_sp_list = sorted(sp_list, key=lambda x: x.dist, reverse=True)

    for sp in new_sp_list:

        sp_info = sprite_calcs(sp.x, sp.y, player.x, player.y, player.z, player.ray_angle, level)

        if sp_info[0] is not None:
            screen.blit(pygame.transform.scale(type2sprite[sp.type], (sp_info[0], sp_info[0])), (sp_info[1], sp_info[2]))


def load_sprites():
    try:
        with open("sprite_positions.json", 'r') as file:
            json_data = json.load(file)
            sprite_list = [Sprite.from_json(data) for data in json_data]
    except json.JSONDecodeError:
        sprite_list = []
    return sprite_list


@njit(fastmath=True)
def normalize_angle(angle):
    if angle < 0:
        return angle + 360
    elif angle >= 360:
        return angle - 360
    return angle


@njit(fastmath=True)
def sprite_calcs(sx, sy, px, py, pz, p_rot, lvl):
    h_angle = math.degrees(math.atan2(sy - py, sx - px))
    h_angle_diff = h_angle - p_rot

    while h_angle_diff < -180:
        h_angle_diff += 360
    while h_angle_diff >= 180:
        h_angle_diff -= 360

    dist = math.sqrt((sx - px) ** 2 + (sy - py) ** 2)
    sh = int(10000 / (dist + 1) / 2)

    if can_see_sprite(px, py, sx, sy, lvl, dist):
        screen_x = int(576 + h_angle_diff * 19.2)
        st = int(768 / 2 - sh / 2)
        st -= sh * pz
        return sh, screen_x, st

    return None, None, None

@njit(fastmath=True)
def can_see_sprite(px, py, sx, sy, lvl_map, dist):

    dx = sx - px
    dy = sy - py
    dx /= dist
    dy /= dist

    steps = int(dist)

    for i in range(steps):
        x = int(px + dx * i)
        y = int(py + dy * i)
        row_index = int(y / 16)
        col_index = int(x / 16)
        if lvl_map[row_index][col_index] > 0 and lvl_map[row_index][col_index] != 4:
            return False
    return True
