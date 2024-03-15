import pygame as pg
from pygame.locals import *
from lvls import *
pg.init()

clock = pg.time.Clock()
fps = 60

WIN_W = 1000
WIN_H = 1000

# цвета фона уровней
BLUE = '#6185f8'
VIOLET = '#645f89'
BLACK = '#000000'

sc = pg.display.set_mode((WIN_W, WIN_H))
pg.display.set_caption("Super Guido Adventure")

font = pg.font.SysFont('Bauhaus 93', 70)
font_score = pg.font.SysFont('Bauhaus 93', 30)

TILE_SIZE = 50
BLOCK = (TILE_SIZE, TILE_SIZE)
lvl = 2
#player = 0
game_over = 0
main_menu = True
score = 0

#загрузка картинки
restart_img = pg.image.load('skins/buttons/restart_btn.png')
restart_img = pg.transform.scale(restart_img, (181, 100))
start_img = pg.image.load('skins/buttons/start_btn.png')
start_img = pg.transform.scale(start_img, (181, 100))
exit_img = pg.image.load('skins/buttons/exit_btn.png')
exit_img = pg.transform.scale(exit_img, (181, 100))
menu_bg = pg.image.load('skins/menu_bg.PNG')

#load sounds
pg.mixer.music.load('sounds/music.wav')
pg.mixer.music.play(-1, 0.0, 5000)
coin_fx = pg.mixer.Sound('sounds/coin.wav')
coin_fx.set_volume(0.5)
jump_fx = pg.mixer.Sound('sounds/jump.wav')
jump_fx.set_volume(0.5)
game_over_fx = pg.mixer.Sound('sounds/game_over.wav')
game_over_fx.set_volume(0.5)
game_won_fx = pg.mixer.Sound('sounds/game_won.wav')
game_won_fx.set_volume(0.5)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    sc.blit(img, (x, y))


def reset_lvl(lvl):
    player1.reset(100, WIN_H-130)
    enemy_group.empty()
    water_group.empty()
    lava_group.empty()
    door_group.empty()

    if lvl == 1:
        world_data = lvl1
    elif lvl == 2:
        world_data = lvl2
    elif lvl == 3:
        world_data = lvl3
    world = World(world_data)

    return world


class Button():
    def __init__(self, image, x, y):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        pos = pg.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pg.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pg.mouse.get_pressed()[0] == 0:
            self.clicked = False

        sc.blit(self.image, self.rect)

        return action


class Player():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 5

        if game_over == 0:
            keys = pg.key.get_pressed()
            if keys[pg.K_SPACE] and self.jumped == False and self.in_air == False:
                jump_fx.play()
                self.vel_y = -15
                self.jumped = True
            if keys[pg.K_SPACE] == False:
                self.jumped = False
            if keys[pg.K_a] and 4 < self.rect.x:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if keys[pg.K_d] and self.rect.x < 970:
                dx += 5
                self.counter += 1
                self.direction = 1
            if keys[pg.K_a] == False and keys[pg.K_d] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            #обработка анимации
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # гравитация
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y


            self.in_air = True
            for tile in world.tile_list:
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            # соприкосновение с врагами
            if pg.sprite.spritecollide(self, enemy_group, False):
                game_over = -1
                game_over_fx.play()

            # соприкосновение с водой
            if pg.sprite.spritecollide(self, water_group, False):
                game_over = -1
                game_over_fx.play()

            # соприкосновение с лавой
            if pg.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                game_over_fx.play()

            # соприкосновение с дверью
            if pg.sprite.spritecollide(self, door_group, False):
                game_over = 1

            # соприкосновение с дверью
            if pg.sprite.spritecollide(self, piper_group, False):
                game_over = 1

            # обновление координат игрока
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.image = self.dead_image
            draw_text('GAME OVER!', font, '#ffffff', (WIN_W // 2) - 200, WIN_H // 2 - 100)
            if self.rect.y > -50:
                self.rect.y -= 5

        # отрисовка
        sc.blit(self.image, self.rect)

        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
                img_right = pg.image.load(f'skins/guido/guido{num}.png')
                img_right = pg.transform.scale(img_right, (32, 52))
                img_left = pg.transform.flip(img_right, True, False)
                self.images_right.append(img_right)
                self.images_left.append(img_left)
        self.dead_image = pg.image.load('skins/dead.png')
        self.dead_image = pg.transform.scale(self.dead_image, BLOCK)
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True


class World():
    def __init__(self, data):
        self.tile_list = []
        block1_img = pg.image.load('skins/blocks/block1.png')
        block2_img = pg.image.load('skins/blocks/block2.png')
        block3_img = pg.image.load('skins/blocks/block3.png')
        block4_img = pg.image.load('skins/blocks/block4.png')


        row = 0
        for line in data:
            col = 0
            for tile in line:
                if tile == 1:
                    img = pg.transform.scale(block1_img, BLOCK)
                    img_rect = img.get_rect()
                    img_rect.x = col * TILE_SIZE
                    img_rect.y = row * TILE_SIZE
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    water = Water(col * TILE_SIZE, row * TILE_SIZE)
                    water_group.add(water)
                if tile == 3:
                    img = pg.transform.scale(block3_img, BLOCK)
                    img_rect = img.get_rect()
                    img_rect.x = col * TILE_SIZE
                    img_rect.y = row * TILE_SIZE
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 4:
                    img = pg.transform.scale(block2_img, BLOCK)
                    img_rect = img.get_rect()
                    img_rect.x = col * TILE_SIZE
                    img_rect.y = row * TILE_SIZE
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 5:
                    img = pg.transform.scale(block4_img, BLOCK)
                    img_rect = img.get_rect()
                    img_rect.x = col * TILE_SIZE
                    img_rect.y = row * TILE_SIZE
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 6:
                    img = pg.image.load('skins/sprites/enemy3.png')
                    img = pg.transform.scale(img, BLOCK)
                    enemy = Enemy(img, col * TILE_SIZE, row * TILE_SIZE)
                    enemy_group.add(enemy)
                if tile == 7:
                    img = pg.image.load('skins/sprites/enemy2.png')
                    img = pg.transform.scale(img, BLOCK)
                    enemy = Enemy(img, col * TILE_SIZE, row * TILE_SIZE)
                    enemy_group.add(enemy)
                if tile == 8:
                    img = pg.image.load('skins/sprites/enemy1.png')
                    img = pg.transform.scale(img, BLOCK)
                    enemy = Enemy(img, col * TILE_SIZE, row * TILE_SIZE)
                    enemy_group.add(enemy)
                if tile == 9:
                    lava = Lava(col * TILE_SIZE, row * TILE_SIZE)
                    lava_group.add(lava)
                if tile == 10:
                    door = Door(col * TILE_SIZE, row * TILE_SIZE - (TILE_SIZE // 2))
                    door_group.add(door)
                if tile == 11:
                    coin = Coin(col * TILE_SIZE + (TILE_SIZE // 2), row * TILE_SIZE + (TILE_SIZE // 2))
                    coin_group.add(coin)
                if tile == 12:
                    img = pg.image.load('skins/sprites/fire1.png')
                    img = pg.transform.scale(img, BLOCK)
                    enemy = Enemy(img, col * TILE_SIZE, row * TILE_SIZE)
                    enemy_group.add(enemy)
                if tile == 13:
                    piper = Piper(col * TILE_SIZE, row * TILE_SIZE)
                    piper_group.add(piper)
                col += 1
            row += 1

    def draw(self):
        for tile in self.tile_list:
            sc.blit(tile[0], tile[1])
            #pg.draw.rect(sc, (255, 255, 255), tile[1], 2)


class Enemy(pg.sprite.Sprite):
    def __init__(self, img, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


class Water(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        img = pg.image.load('skins/blocks/water.png')
        self.image = pg.transform.scale(img, BLOCK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Lava(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        img = pg.image.load('skins/blocks/lava.png')
        self.image = pg.transform.scale(img, BLOCK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Door(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        img = pg.image.load('skins/blocks/exit.png')
        self.image = pg.transform.scale(img, (TILE_SIZE, int(TILE_SIZE * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Piper(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        img = pg.image.load('skins/sprites/princess_l.png')
        self.image = pg.transform.scale(img, (TILE_SIZE*3/5, TILE_SIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Coin(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        img = pg.image.load('skins/blocks/coin.png')
        self.image = pg.transform.scale(img, (TILE_SIZE // 2, TILE_SIZE // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


bg = pg.Surface((WIN_W, WIN_H))
player1 = Player(100, WIN_H - 130)

enemy_group = pg.sprite.Group()
water_group = pg.sprite.Group()
lava_group = pg.sprite.Group()
door_group = pg.sprite.Group()
coin_group = pg.sprite.Group()
piper_group = pg.sprite.Group()

score_coin = Coin(TILE_SIZE // 2, TILE_SIZE // 2)
coin_group.add(score_coin)

if lvl == 1:
    world_data = lvl1
elif lvl == 2:
    world_data = lvl2
elif lvl == 3:
    world_data = lvl3
world = World(world_data)

restart_button = Button(restart_img, WIN_W // 2 - 90, WIN_H // 2 + 50)
start_button = Button(start_img, 213, WIN_H // 2 - 75)
exit_button = Button(exit_img, 607, WIN_H // 2 - 75)


#flag = 0
run = True
while run:
    clock.tick(fps)
    if main_menu == True:
        sc.blit(menu_bg, (0, 0))
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False

    else:
        if lvl == 1:
            bg.fill(pg.Color(BLUE))
            sc.blit(bg, (0, 0))
            cloud = pg.image.load('skins/blocks/cloud.png')
            cloud_img = pg.transform.scale(cloud, (150, 85))
            bush = pg.image.load('skins/blocks/bush.png')
            bush_img = pg.transform.scale(bush, (145, 45))
            sc.blit(cloud_img, (100, 100))
            sc.blit(cloud_img, (800, 300))
            sc.blit(cloud_img, (500, 10))
            sc.blit(bush_img, (2, 805))
            sc.blit(bush_img, (750, 55))
        elif lvl == 2:
            bg.fill(pg.Color(VIOLET))
            sc.blit(bg, (0, 0))
        elif lvl == 3:
            bg.fill(pg.Color(BLACK))
            sc.blit(bg, (0, 0))

        world.draw()

        if game_over == 0:
            enemy_group.update()
            if pg.sprite.spritecollide(player1, coin_group, True):
                score += 1
                coin_fx.play()
            draw_text('X ' + str(score), font_score, '#ffffff', TILE_SIZE - 10, 10)

        enemy_group.draw(sc)
        water_group.draw(sc)
        lava_group.draw(sc)
        coin_group.draw(sc)
        door_group.draw(sc)
        piper_group.draw(sc)

        game_over = player1.update(game_over)

        if game_over == -1:
            if restart_button.draw():
                world_data = []
                world = reset_lvl(lvl)
                game_over = 0
                score = 0

        if game_over == 1:
            lvl += 1
            if lvl <= 3:
                world_data = []
                world = reset_lvl(lvl)
                game_over = 0
            else:
                #game_won_fx.play()
                draw_text('YOU WIN!', font, '#ffffff', (WIN_W // 2) - 140, WIN_H // 2 - 100)
                if restart_button.draw():
                    lvl = 1
                    world_data = []
                    world = reset_lvl(lvl)
                    game_over = 0
                    score = 0

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False

    pg.display.update()
pg.quit()
