import pygame
import math
import os
import random
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, SPRITE_HEIGHT, SPRITE_WIDTH


class Player:
    def __init__(self, image, speed, health, max_health):
        self.speed = speed
        self.image = image
        self.flip_image = pygame.transform.flip(image, True, False)
        self.pos = image.get_rect().move((SCREEN_WIDTH // 2), SCREEN_HEIGHT // 2)
        self.hitbox = (image.get_rect()).scale_by(0.55, 0.75)
        self.health = health
        self.max_health = max_health
        self.arc_active = False
        self.arc_start_time = 0
        self.arc_duration = 300
        self.arc_color = (255, 255, 255)
        self.facing = 1
        self.hit_enemies = []
        self.attack_hitbox = pygame.Rect(0, 0, 80, 60)
        # slash animation
        self.slash_sheet = pygame.image.load(
            "./animations/slash/slash2_128x128.png"
        ).convert_alpha()
        self.slash_frames = 9
        self.slash_w = 128
        self.slash_h = 128
        self.slash_index = 0
        self.slash_active = False
        self.slash_start = 0
        self.slash_duration = 270

    def move(self, up=False, down=False, left=False, right=False):
        if right:
            self.pos.right += self.speed
        if left:
            self.pos.right -= self.speed
        if down:
            self.pos.top += self.speed
        if up:
            self.pos.top -= self.speed
        if self.pos.right > SCREEN_WIDTH:
            self.pos.left = 0
        if self.pos.top > SCREEN_HEIGHT - SPRITE_HEIGHT:
            self.pos.top = 0
        if self.pos.right < SPRITE_WIDTH:
            self.pos.right = SCREEN_WIDTH
        if self.pos.top < 0:
            self.pos.top = SCREEN_HEIGHT - SPRITE_HEIGHT

    def take_damage(self):
        if self.health > 0:
            self.health -= 1
            print(f"Player health is {self.health}")
        else:
            print("Player health is 0!")

    def basic_attack(self, surface):
        if not self.arc_active:
            self.arc_active = True
            self.arc_start_time = pygame.time.get_ticks()
            self.hit_enemies = []

        self.draw_arc(surface)

    def draw_arc(self, surface):
        offset = 0
        radius = 50
        if self.image == self.flip_image:
            center = (self.pos.centerx - offset, self.pos.centery)
            start_angle = math.pi / 2
            end_angle = -math.pi / 2
        else:
            center = (self.pos.centerx + offset, self.pos.centery)
            start_angle = -math.pi / 2
            end_angle = math.pi / 2
        return pygame.draw.arc(
            surface,
            self.arc_color,
            (center[0] - radius, center[1] - radius, radius * 2, radius * 2),
            start_angle,
            end_angle,
            width=5,
        )

    def start_slash(self):
        """Call this when the player presses Space."""
        if not self.slash_active:
            self.slash_active = True
            self.slash_start = pygame.time.get_ticks()
            self.slash_index = 0
            self.hit_enemies = []

    def update(self):
        current_time = pygame.time.get_ticks()
        # slash animation
        if self.slash_active:
            elapsed = current_time - self.slash_start
            frame = int(elapsed * self.slash_frames / self.slash_duration)
            frame = max(0, min(frame, self.slash_frames - 1))
            self.slash_index = frame

            if elapsed >= self.slash_duration:
                self.slash_active = False

        if self.facing == 1:
            self.attack_hitbox.midleft = (self.pos.right - 10, self.pos.centery)
        else:
            self.attack_hitbox.midright = (self.pos.left + 10, self.pos.centery)
        if self.arc_active:
            if self.facing == 1:
                self.attack_hitbox.midleft = (self.pos.right, self.pos.centery)
            else:
                self.attack_hitbox.midright = (self.pos.left, self.pos.centery)

            if current_time - self.arc_start_time > self.arc_duration:
                self.arc_active = False
                self.hit_enemies = []


class Enemy:
    def __init__(self, image, speed, health):
        self.image = image
        self.speed = speed
        self.health = health
        self.pos = image.get_rect()

    def get_random_sprite(self):
        raise NotImplementedError("Children contain implementations")

    def move_toward(self, target):
        dx = target[0] - self.pos[0]
        dy = target[1] - self.pos[1]
        distance = math.hypot(dx, dy)
        if distance > 0:
            dx /= distance
            dy /= distance
            self.pos[0] += dx * self.speed
            self.pos[1] += dy * self.speed

    def take_damage(self):
        if self.health > 0:
            self.health -= 2
            print(f"Enemy health is {self.health}")
        else:
            print("Enemy health is 0!")


class EasyEnemy(Enemy):
    def __init__(self):
        self.health = 4
        self.speed = 2.0
        self.image = pygame.image.load(self.get_random_sprite()).convert_alpha()
        self.pos = self.image.get_rect()

    def get_random_sprite(self):
        path_to_sprite = os.path.abspath("enemies/easy/")
        sprites = []
        for entry in os.listdir(path_to_sprite):
            full_path = os.path.join(path_to_sprite, entry)
            sprites.append(full_path)
        return sprites[random.randrange(0, 2)]


class MediumEnemy(Enemy):
    def __init__(self):
        self.health = 8
        self.speed = 1.0
        self.image = pygame.image.load(self.get_random_sprite()).convert_alpha()
        self.pos = self.image.get_rect()

    def get_random_sprite(self):
        path_to_sprite = os.path.abspath("enemies/medium/")
        sprites = []
        for entry in os.listdir(path_to_sprite):
            full_path = os.path.join(path_to_sprite, entry)
            sprites.append(full_path)
        return sprites[random.randrange(0, 2)]


class HardEnemy(Enemy):
    def __init__(self):
        self.health = 20
        self.speed = 0.5
        self.image = pygame.image.load(self.get_random_sprite()).convert_alpha()
        self.pos = self.image.get_rect()

    def get_random_sprite(self):
        path_to_sprite = os.path.abspath("enemies/hard/")
        sprites = []
        for entry in os.listdir(path_to_sprite):
            full_path = os.path.join(path_to_sprite, entry)
            sprites.append(full_path)
        return sprites[random.randrange(0, 2)]
