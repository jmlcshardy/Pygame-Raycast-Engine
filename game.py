import pygame
import numpy as np
import numba as nb
from numba.typed import List
from random import randint
import os

pygame.init()

screen_width = 1152
screen_height = 768
halfheight = screen_height // 2
tile_size = 16
screen = pygame.display.set_mode((screen_width, screen_height))

clock = pygame.time.Clock()

font = pygame.font.SysFont('arial', 30)
title_font = pygame.font.SysFont('arial', 100)

renderMode = False
canChange = 0

rows = 3
layers = []

draw_line = True

assets = os.listdir("C:\\Users\\lrhar\\PycharmProjects\\3DRaycast\\Assets")

textures = []

for i in assets:
    if ".png" in i:
        textures.append(pygame.transform.scale(pygame.image.load("Assets\\" + i), (tile_size, tile_size)))

map_created = False

map1_file = open("Map", "r")
map1_lines = map1_file.readlines()
map1_file.close()


level = List()
tile_map = []
for line in map1_lines:
    map_row = []
    for char in line.strip():
        map_row.append(int(char))
    if map_row:
        level.append(map_row)
        tile_map.append(map_row)


class Player:
    def __init__(self):
        self.x = 192
        self.y = 192
        self.v = 0
        self.oldx = self.x
        self.oldy = self.y
        self.speed = 6
        self.rotation = 0
        self.ray_angle = 270
        self.fov = 60
        self.hitbox = pygame.Rect(self.x - 25, self.y - 25, 16, 16)
        self.you_win = False

    def update_hitbox(self):
        self.hitbox.centerx = self.x
        self.hitbox.centery = self.y


class Button:
    def __init__(self, x, y, text, width, height):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.text = text
        self.color = (0, 0, 0)

    def draw(self, color):
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height), 0, 3)
        text = font.render(self.text, True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text, text_rect)


play = Button((screen_width//2 - 100), (screen_height//2 - 50), 'Start', 200, 50)
edit = Button((screen_width//2 - 100), (screen_height//2 + 50), 'Level Editor', 200, 50)
help = Button(1098, 714, '?', 28, 28)
done = Button((screen_width//2 - 100), (screen_height//2 + 100), 'Done', 200, 50)
win = Button((screen_width//2 - 100), (screen_height//2 + 100), "WINNER!!!", 200, 50)

buttons = [play, edit]


@nb.jit(nopython=True)
def cast_ray(angle, iteration, lvlMap, x, y, fov, player_rot, layer, vertical):
    x = x
    y = y
    dist = 0
    nextDist = 1
    casting = True
    end = [x, y]
    cos_angle = np.cos(angle)
    sin_angle = np.sin(angle)
    rdx = np.sin(np.deg2rad(player_rot))
    rdy = np.cos(np.deg2rad(player_rot))
    dot_product = rdx * cos_angle + rdy * sin_angle
    for i in range(len(lvlMap[0]) * tile_size + 1):
        row_index = int(end[1] / tile_size)
        col_index = int(end[0] / tile_size)
        dist += nextDist
        nextDist = 1
        end[0] = x + dist * cos_angle
        end[1] = y + dist * sin_angle
        if lvlMap[row_index][col_index] > 0:
            dist *= dot_product
            dist = int(abs(dist))
            casting = False

        if not casting:

            wall_height = int(10000 / (dist + 1))

            wall_top = int(screen_height / 2 - wall_height / 2)
            wall_bottom = wall_top + wall_height

            wall_top -= (wall_height * (layer - vertical))
            wall_bottom -= (wall_height * (layer - vertical))

            ray_x = iteration * (screen_width / fov)

            type = lvlMap[row_index][col_index]

            return ray_x, wall_top, wall_bottom, wall_height, end[0], end[1], dist, type


def collision():
    if tile_map[int(player.y/tile_size)][int(player.x/tile_size)] > 0:
        if tile_map[int(player.y/tile_size)][int(player.x/tile_size)] == 5:
            player.you_win = True
        else:
            player.x = player.oldx
            player.y = player.oldy


def save():
    global level
    with open('Map', 'w') as f:
        for i in tile_map:
            f.write(''.join(map(str, i)) + '\n')
        level = List(tile_map)
    return True


def refresh_window():
    global tile_type, rgb_values
    if not player.you_win:
        screen.fill((3, 37, 126))
        if not renderMode:
            pygame.draw.rect(screen, (0, 128, 0), (0, screen_height / 2, screen_width, screen_height / 2))

        if renderMode:
            x = 0
            y = 0
            for i in tile_map:
                if i:
                    for j in i:
                        if level[int(y / tile_size)][int(x / tile_size)] > 0:
                            try:
                                map_color = textures[level[int(y / tile_size)][int(x / tile_size)] - 1].get_at((1, 0))
                            except IndexError:
                                level[int(y / tile_size)][int(x / tile_size)] = 0
                                map_color = textures[0].get_at((1, 0))
                            pygame.draw.rect(screen, map_color, (x, y, tile_size, tile_size))
                        x += tile_size
                x = 0
                y += tile_size

        it = 0
        deg = player.ray_angle - (player.fov//2)
        for i in range(screen_width + 1):
            x, y = player.hitbox.centerx, player.hitbox.centery
            it += player.fov / screen_width
            deg += player.fov / screen_width

            if renderMode:
                info = cast_ray(np.deg2rad(deg), it, level, x, y, player.fov, player.rotation, 0, 0)
                lineColor = pygame.Color(255, 255, 255)
                if draw_line:
                    pygame.draw.line(screen, lineColor, (player.hitbox.x, player.hitbox.y), (info[4], info[5]), 2)
                else:
                    pygame.draw.rect(screen, lineColor, (info[4], info[5], 2, 2))
                pygame.draw.rect(screen, (255, 0, 0), (player.hitbox.x, player.hitbox.y, 10, 10))
                dirRay = cast_ray(np.deg2rad(player.ray_angle), 1, level, x, y, player.fov, player.rotation, 0, 0)
                pygame.draw.line(screen, (255, 0, 0), (player.hitbox.x, player.hitbox.y), (dirRay[4], dirRay[5]), 1)
            else:
                for r in range(rows):
                    row = cast_ray(np.deg2rad(deg), it, level, x, y, player.fov, player.rotation, r, player.v)
                    tile_type = textures[row[7] - 1]
                    tile_x = (row[4] + row[5]) % tile_size
                    wall_surf = tile_type.subsurface((tile_x, 0, 1, tile_type.get_height()))
                    transWallSurf = pygame.transform.scale(wall_surf, (1, row[3]))
                    pygame.draw.line(screen, (0, 0, 0), (row[0], row[1]), (row[0], row[2]), 2)
                    screen.blit(transWallSurf, (row[0], row[1]))

    if player.you_win:

        win_screen = title_font.render('YOU WIN!!!!!', True, 0)
        win_rect = win_screen.get_rect(center=(screen_width // 2, 150))
        screen.blit(win_screen, win_rect)

    pygame.display.set_caption("Fps: " + str(cf) + "/30")
    pygame.display.update()


running = True

player = Player()


def menu():
    pygame.display.set_caption("Raycaster (Move Mouse)")
    while True:
        screen.fill((100, 100, 100))
        title = title_font.render('Raycast Engine', True, 0)
        title_rect = title.get_rect(center=(screen_width // 2, 150))
        screen.blit(title, title_rect)
        player.x = player.y = 192
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save()
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play.x <= event.pos[0] <= play.x + play.width and play.y <= event.pos[1] <= play.y + play.height:
                    main()
                if edit.x <= event.pos[0] <= edit.x + edit.width and edit.y <= event.pos[1] <= edit.y + edit.height:
                    from level_editor import map_maker
                    map_maker()
            elif event.type == pygame.MOUSEMOTION:
                pygame.display.set_caption("Raycaster")
                for button in buttons:
                    if button.x <= event.pos[0] <= button.x + button.width and button.y <= event.pos[1] <= button.y + button.height:
                        button_color = (64, 64, 64)
                    else:
                        button_color = (255, 255, 255)

                    button.draw(button_color)
                pygame.display.update()


def main():
    global running, canChange, renderMode, cf, draw_line
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                quit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if win.x <= event.pos[0] <= win.x + win.width and win.y <= event.pos[1] <= win.y + win.height and player.you_win:
                    player.you_win = False
                    player.x = player.y = 192
                    player.rotation = 0
                    player.ray_angle = 270
            elif event.type == pygame.MOUSEMOTION:
                if player.you_win:
                    if win.x <= event.pos[0] <= win.x + win.width and win.y <= event.pos[1] <= win.y + win.height:
                        win.draw((randint(0, 255), randint(0, 255), randint(0, 255)))
                    else:
                        win.draw((255, 255, 255))

        cf = str(int(clock.get_fps()))

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            player.rotation += player.speed/2
            player.ray_angle -= player.speed/2
        elif keys[pygame.K_d]:
            player.rotation -= player.speed/2
            player.ray_angle += player.speed/2

        if keys[pygame.K_ESCAPE]:
            save()
            menu()

        dx = player.speed * np.sin(np.deg2rad(player.rotation))
        dy = player.speed * np.cos(np.deg2rad(player.rotation))
        player.speed = 6
        if keys[pygame.K_w]:
            player.oldx = player.x
            player.x -= dx
            player.oldy = player.y
            player.y -= dy
        elif keys[pygame.K_s]:
            player.oldx = player.x
            player.x += dx
            player.oldy = player.y
            player.y += dy


        if keys[pygame.K_f]:
            player.speed *= 2

        if canChange >= 30 and keys[pygame.K_r]:
            renderMode = not renderMode
            canChange = 0

        if keys[pygame.K_SPACE]:
            player.v += 1
        if keys[pygame.K_LCTRL] and player.v > 0:
            player.v -= 1

        player.update_hitbox()

        collision()
        refresh_window()

        canChange += 1
        clock.tick(30)