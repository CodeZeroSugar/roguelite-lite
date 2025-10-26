import pygame
import math
import random
from constants import *


class Player:
    def __init__(self, image, height, speed, health, max_health):
        self.speed = speed
        self.image = image
        self.pos = image.get_rect().move(0, height)
        self.health = health
        self.max_health = max_health

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


class Enemy:
    def __init__(self, image, speed):
        self.speed = speed
        self.image = image
        self.pos = image.get_rect()

    def move_toward(self, target):
        dx = target[0] - self.pos[0]
        dy = target[1] - self.pos[1]
        distance = math.hypot(dx, dy)
        if distance > 0:
            dx /= distance
            dy /= distance
            self.pos[0] += dx * self.speed
            self.pos[1] += dy * self.speed


def main():
    print("Starting Roguelite-lite!")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    player = pygame.image.load("player.png").convert()
    background = pygame.image.load("grass.jpg").convert()
    screen.blit(background, (0, 0))

    p = Player(player, 10, 3, 10, 10)
    health_bar_pos = (50, 50)
    health_bar_width = 200
    health_bar_height = 20
    background_color = (255, 0, 0)
    health_color = (0, 255, 0)

    running = True

    objects = []
    for x in range(5):
        o = Enemy(player, 2)
        o.pos[0] = random.randint(0, SCREEN_WIDTH - 20)
        o.pos[1] = random.randint(0, SCREEN_WIDTH - 20)
        objects.append(o)
        print("Enemy spawned")

    damage_tick = 0
    damaged = False
    while running:
        if damage_tick > 100:
            damaged = False
            damage_tick = 0

        target = p.pos
        screen.blit(background, p.pos, p.pos)

        health_ratio = p.health / p.max_health
        current_health_width = health_bar_width * health_ratio

        pygame.draw.rect(
            screen,
            background_color,
            (health_bar_pos[0], health_bar_pos[1], health_bar_width, health_bar_height),
        )
        pygame.draw.rect(
            screen,
            health_color,
            (
                health_bar_pos[0],
                health_bar_pos[1],
                current_health_width,
                health_bar_height,
            ),
        )

        for o in objects:
            screen.blit(background, o.pos, o.pos)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            p.move(up=True)
        if keys[pygame.K_s]:
            p.move(down=True)
        if keys[pygame.K_a]:
            p.move(left=True)
        if keys[pygame.K_d]:
            p.move(right=True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.blit(p.image, p.pos)

        for o in objects:
            o.move_toward(target)
            if o.pos.colliderect(p.pos) and damage_tick == 0:
                p.take_damage()
                damaged = True
            screen.blit(o.image, o.pos)

        pygame.display.update()

        clock.tick(60)
        if damaged:
            damage_tick += 1
    pygame.quit()


if __name__ == "__main__":
    main()
