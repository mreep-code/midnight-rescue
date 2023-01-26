import os
import random
from random import randint, choice
import math
import pygame
from os import listdir
from os.path import isfile, join

pygame.init()

pygame.display.set_caption('Game')

screen_width = 960
screen_height = 540
FPS = 24
PLAYER_VEL = 12

starting_ypos = randint(90, 100)

screen = pygame.display.set_mode((screen_width, screen_height))

def flip(sprites):
    return [pygame.transform.flip(sprite, False, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height):
    path = join("images", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

# implementing heart images
full_heart = pygame.image.load('images/health/full_heart.png').convert_alpha()
full_heart = pygame.transform.rotozoom(full_heart, 0, 3)

empty_heart = pygame.image.load('images/health/empty_heart.png').convert_alpha()
empty_heart = pygame.transform.rotozoom(empty_heart, 0, 3)

class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 2.5
    SPRITES = load_sprite_sheets("player",  "blue_hair", 64, 64)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.immune = 0
        self.health = 3
        self.max_health = 3

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0
        
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True

    def move_left(self, vel):
        self.x_vel = -vel

    def move_right(self, vel):
        self.x_vel = vel

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()
    
    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def get_damage(self):
        if self.immune == 0 and self.health > 0:
            self.health -= 1
            self.immune = int(3 * FPS)

    def empty_hearts(self):
        for heart in range(self.max_health):
            if heart < self.health:
                screen.blit(full_heart, (heart * 60 - 20, -50))
            else:
                screen.blit(empty_heart, (heart * 60 - 20, -50))
 
    def stay_screen(self):
        if self.rect.bottom > 468:
            self.rect.bottom = 468

        if self.rect.left < -30:
            self.rect.left = -30
        
        if self.rect.right > 980:
            self.rect.right = 980

        if self.rect.top < -10:
            self.rect.top = -10

    def update_sprite(self):
        sprite_sheet = "run"
        if self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "run"
        if self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)
        self.stay_screen()
        self.empty_hearts()
        if self.immune > 0:
                self.immune -= 1

    def draw(self, screen):
        screen.blit(self.sprite, (self.rect.x, self.rect.y))

class Ghost(pygame.sprite.Sprite):
    SPRITES = load_sprite_sheets("enemies",  "ghost", 64, 64)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.mask = None
        self.animation_count = 0
        self.x = x
        self.y = y

    def move(self):
        # sine wave
        t = pygame.time.get_ticks()/3 % 1000

        self.rect.x -= 5
        self.rect.y = starting_ypos - math.sin(t/75) * 30

    def loop(self):
        self.move()
        self.update()

    def reset(self):
        self.rect.y = random.randrange(80, 200)
        self.rect.x = random.randrange(1000, 1200)

    def update(self):
        self.update_sprite()
        if self.rect.right < 0:
            self.reset()
        self.vanish()

    def update_sprite(self):
        sprite_sheet = "move"

        sprite_sheet_name = sprite_sheet
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def vanish(self):
        if self.rect.right <= 0:
            pygame.sprite.Sprite.kill(self)

    def draw(self, screen):
        screen.blit(self.sprite, (self.rect.x, self.rect.y))

class Skeleton(pygame.sprite.Sprite):
    SPRITES = load_sprite_sheets("enemies",  "skeleton", 64, 64)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.mask = None
        self.animation_count = 0
        self.x = x
        self.y = y

    def move(self):
        self.rect.x -= 10

    def loop(self):
        self.move()
        self.update()

    def reset(self):
        self.rect.y = 342
        self.rect.x = random.randrange(1000, 1200)

    def update(self):
        self.update_sprite()
        if self.rect.right < 0:
            self.reset()
        self.vanish()

    def update_sprite(self):
        sprite_sheet = "move"

        sprite_sheet_name = sprite_sheet
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def vanish(self):
        if self.rect.right <= 0:
            pygame.sprite.Sprite.kill(self)

    def draw(self, screen):
        screen.blit(self.sprite, (self.rect.x, self.rect.y))

def draw(screen, player, ghost, skeleton):
    player.draw(screen)
    ghost.draw(screen)
    skeleton.draw(screen)
    pygame.display.update()

def handle_move(player):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    if keys[pygame.K_LEFT]:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT]:
        player.move_right(PLAYER_VEL)

player = pygame.sprite.GroupSingle()

enemies = []
enemies = pygame.sprite.Group()

for i in range(50):
    ghost = Ghost(randint(1000, 1200), starting_ypos, 50, 50)
 
    # Add the block to the list of objects
    enemies.add(ghost)

for i in range(50):
    skeleton = Skeleton(randint(1000, 1200), 342, 50, 50)

    enemies.add(skeleton)

scroll = 0

ground = pygame.image.load('images/background/ground.png').convert_alpha()
ground_width = ground.get_width()
ground_rect = ground.get_rect()

tiles = math.ceil(screen_width / ground_width) + 1

for i in range(0, tiles):
    screen.blit(ground, (i * ground_width + scroll, 0))

scroll -= 10
if abs(scroll) > ground_width:
    scroll = 0

bg = pygame.image.load('images/background/full_bg1.png').convert()
bg_width = bg.get_width()
bg_rect = bg.get_rect()

tiles = math.ceil(screen_width / bg_width) + 1

for i in range(0, tiles):
    screen.blit(bg, (i * bg_width + scroll, 0))

scroll -= 10
if abs(scroll) > bg_width:
    scroll = 0

def main(screen):
    clock = pygame.time.Clock()

    player = Player(200, 342, 50, 50)

    global scroll

    run = True
    while run:
        clock.tick(FPS)

        for i in range(0, tiles):
            screen.blit(bg, (i * bg_width + scroll, 0))

        scroll -= 10
        if abs(scroll) > bg_width:
            scroll = 0

        for i in range(0, tiles):
            screen.blit(ground, (i * ground_width + scroll, 0))

        scroll -= 10
        if abs(scroll) > ground_width:
            scroll = 0

        #collision
        if player.rect.colliderect(ghost.rect) or player.rect.colliderect(skeleton.rect):
            player.make_hit()
            player.get_damage()
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if player.rect.bottom == 468:
                        player.jump()

        player.loop(FPS)
        ghost.loop()
        skeleton.loop()
        handle_move(player)
        draw(screen, player, ghost, skeleton)
        player.update()
        ghost.update()
        skeleton.update()
    
    pygame.quit()
    quit()

if __name__ == "__main__":
    main(screen)