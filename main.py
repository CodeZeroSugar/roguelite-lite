import pygame
import math
import random
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, SPRITE_HEIGHT, SPRITE_WIDTH


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
        self.arc_duration = 300
        self.arc_color = (255, 255, 255)
        self.arc_rect = pygame.Rect(0, 0, self.pos[2], self.pos[3])
        self.facing = 1
        self.hit_enemies = []
        self.attack_hitbox = pygame.Rect(0, 0, 80, 60)
        # slash animation
        self.slash_sheet = pygame.image.load(
            "./animations/slash/sprite-sheet.png"
        ).convert_alpha()
        self.slash_frames = 9
        self.slash_w = 64
        self.slash_h = 64
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
        offset = 25
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
            offset = 35
            if self.facing == 1:
                self.attack_hitbox.midleft = (self.pos.right, self.pos.centery)
            else:
                self.attack_hitbox.midright = (self.pos.left, self.pos.centery)

            if current_time - self.arc_start_time > self.arc_duration:
                self.arc_active = False
                self.hit_enemies = []


class Enemy:
    def __init__(self, image, speed, health):
        self.speed = speed
        self.image = image
        self.health = health
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

    def take_damage(self):
        if self.health > 0:
            self.health -= 2
            print(f"Enemy health is {self.health}")
        else:
            print("Enemy health is 0!")


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
        o = Enemy(player, 2, 5)
        o.pos[0] = random.randint(0, SCREEN_WIDTH - 20)
        o.pos[1] = random.randint(0, SCREEN_HEIGHT - 20)
        objects.append(o)
        print("Enemy spawned")

    damage_tick = 0
    damaged = False

    attack_cooldown = 0
    on_cooldown = False

    while running:
        # Player input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            p.move(up=True)
        if keys[pygame.K_s]:
            p.move(down=True)
        if keys[pygame.K_a]:
            p.move(left=True)
            p.image = p.flip_image
            p.facing = -1
        if keys[pygame.K_d]:
            p.move(right=True)
            p.image = player
            p.facing = 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not on_cooldown:
                    p.basic_attack(screen)
                    p.start_slash()
                    print("Player attacks")
                    on_cooldown = True

        # Update logic
        target = p.pos.center
        p.update()

        # Move enemies
        for o in objects:
            o.move_toward(target)

        # Player damaged
        for o in objects:
            if o.pos.colliderect(p.pos) and damage_tick == 0:
                p.take_damage()
                damaged = True
                damage_tick = 1

        # Enemy damage
        if p.arc_active:
            p.draw_arc(screen)
            for o in objects:
                if o.pos.colliderect(p.attack_hitbox):
                    if o not in p.hit_enemies:
                        o.take_damage()
                        p.hit_enemies.append(o)

        # Draw
        screen.blit(background, (0, 0))

        # health bar
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
        pygame.draw.rect(
            screen,
            (255, 255, 255),
            (health_bar_pos[0], health_bar_pos[1], health_bar_width, health_bar_height),
            2,
        )

        screen.blit(p.image, p.pos)

        # slash
        if p.slash_active:
            src_rect = pygame.Rect(p.slash_index * p.slash_w, 0, p.slash_w, p.slash_h)
            frame = p.slash_sheet.subsurface(src_rect)
            if p.facing == -1:
                frame = pygame.transform.flip(frame, True, False)
            dst_rect = frame.get_rect()
            offset = 18
            if p.facing == 1:
                dst_rect.midleft = (p.pos.right - offset, p.pos.centery)
            else:
                dst_rect.midright = (p.pos.left + offset, p.pos.centery)

            screen.blit(frame, dst_rect)

        for o in objects:
            screen.blit(o.image, o.pos)

        # Cooldowns

        if damaged:
            damage_tick += 1
            if damage_tick > 30:
                damage_tick = 0
                damaged = False

        if on_cooldown:
            attack_cooldown += 1
            if attack_cooldown > 30:
                attack_cooldown = 0
                on_cooldown = False

        pygame.display.update()

        clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    main()
