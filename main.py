import pygame
import math
import random
from constants import *


class Player:
    def __init__(self, image, height, speed, health, max_health):
        self.speed = speed
        self.image = image
        self.flip_image = pygame.transform.flip(image, True, False)
        self.pos = image.get_rect().move(0, height)
        self.health = health
        self.max_health = max_health
        self.arc_active = False
        self.arc_start_time = 0
        self.arc_duration = 500
        self.arc_color = (255, 255, 255)
        self.arc_rect = pygame.Rect(0, 0, self.pos[2], self.pos[3])
        self.facing = 1

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

        self.draw_arc(surface)

    def draw_arc(self, surface):
        offset = 25
        center = (self.pos.centerx + offset, self.pos.centery)
        radius = 50
        start_angle = -math.pi / 2
        end_angle = math.pi / 2
        pygame.draw.arc(
            surface,
            self.arc_color,
            (center[0] - radius, center[1] - radius, radius * 2, radius * 2),
            start_angle,
            end_angle,
            width=5,
        )

    def update(self):
        current_time = pygame.time.get_ticks()
        if self.arc_active and (current_time - self.arc_start_time > self.arc_duration):
            self.arc_active = False


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
    player = pygame.image.load("player.png").convert_alpha()
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

    attack_cooldown = 0
    on_cooldown = False

    while running:
        if damage_tick > 100:
            damaged = False
            damage_tick = 0

        if attack_cooldown > 100:
            on_cooldown = False
            attack_cooldown = 0

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
            p.image = p.flip_image
        if keys[pygame.K_d]:
            p.move(right=True)
            p.image = player

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    p.basic_attack(screen)
                    print("Player attacks")
                    on_cooldown = True

        p.update()

        screen.blit(background, (0, 0))
        screen.blit(p.image, p.pos)

        for o in objects:
            o.move_toward(target)
            if o.pos.colliderect(p.pos) and damage_tick == 0:
                p.take_damage()
                damaged = True
            screen.blit(o.image, o.pos)

        if damaged:
            damage_tick += 1

        if on_cooldown:
            attack_cooldown += 1

        if p.arc_active:
            p.draw_arc(screen)

        pygame.display.update()

        clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    main()
