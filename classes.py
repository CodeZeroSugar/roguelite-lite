import pygame
import math
import os
import random
import animation
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, SPRITE_HEIGHT, SPRITE_WIDTH


class Player:
    def __init__(self, image, speed, health, max_health):
        self.speed = speed
        self.image = image
        self.flip_image = pygame.transform.flip(image, True, False)
        self.pos = image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.hitbox = (image.get_rect()).scale_by(0.35, 0.55)
        self.health = health
        self.score = 0
        self.max_health = max_health
        self.arc_active = False
        self.arc_start_time = 0
        self.arc_duration = 300
        self.arc_color = (255, 255, 255)
        self.hit_enemies = []
        self.attack_hitbox = pygame.Rect(0, 0, 80, 60)
        # slash animation
        self.slash_sheet = pygame.image.load(
            "./assets/animations/slash/slash2_128x128.png"
        ).convert_alpha()
        self.slash_frames = 9
        self.slash_w = 128
        self.slash_h = 128
        self.slash_index = 0
        self.slash_active = False
        self.slash_start = 0
        self.slash_duration = 270
        # Load 128x128 sprite sheets
        self.idle_sheet = animation.SpriteSheet(
            "./assets/animations/player/Idle.png", frame_count=4
        )
        self.walk_sheet = animation.SpriteSheet(
            "./assets/animations/player/Walk.png", frame_count=8
        )
        self.attack_sheet = animation.SpriteSheet(
            "./assets/animations/player/Attack_1.png", frame_count=5
        )
        # Compute offsets for each sheet
        self.offsets = {
            "idle": animation.get_center_offset(self.idle_sheet),
            "walk": animation.get_center_offset(self.walk_sheet),
            "attack": animation.get_center_offset(self.attack_sheet),
        }
        # Create animations
        self.animations = {
            "idle": animation.Animation(self.idle_sheet, base_fps=8),
            "walk": animation.Animation(self.walk_sheet, base_fps=12),
            "attack": animation.Animation(self.attack_sheet, base_fps=15, loop=False),
        }
        # Current state
        self.state = "idle"
        self.facing = "right"
        self.current_anim = self.animations["idle"]
        self.is_attacking = False
        # Level tracking
        self.level = 0
        self.next_level = 1
        self.current_xp = 0
        self.max_xp = 0
        # Obtained abilities
        self.abilities = []
        self.bolts = []
        self.axes = []
        self.flails = []

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

    def take_damage(self, damage=1):
        if self.health > 0:
            self.health -= damage
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

    def update(self, enemies):
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        dx = dy = 0
        # WASD movement
        if keys[pygame.K_w]:
            dy -= self.speed
        if keys[pygame.K_s]:
            dy += self.speed
        if keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_d]:
            dx += self.speed

        moving = dx != 0 or dy != 0

        # Update position
        self.pos[0] += dx
        self.pos[1] += dy

        # Update facing direction
        if dx > 0:
            self.facing = "right"
        elif dx < 0:
            self.facing = "left"

        player_radius = 32
        self.pos.centerx = max(
            player_radius, min(self.pos.centerx, SCREEN_WIDTH - player_radius)
        )
        self.pos.centery = max(
            player_radius, min(self.pos.centery, SCREEN_HEIGHT - player_radius)
        )
        # Update xp
        if self.level == self.next_level:
            print("Current xp reset")
            self.current_xp = 0
            self.max_xp = (self.level + 1) ** 1.5 - self.score
            self.next_level += 1

        # Attack trigger
        if keys[pygame.K_SPACE] and not self.is_attacking:
            self.set_state("attack")
            self.is_attacking = True
        elif not keys[pygame.K_SPACE]:
            self.is_attacking = False

        # Switch after attack finishes
        if self.state == "attack" and self.current_anim.finished:
            self.set_state("walk" if moving else "idle")

        # Update state logic
        elif self.state != "attack":
            self.set_state("walk" if moving else "idle")

        # Update animation
        self.current_anim.update()

        # slash animation
        if self.slash_active:
            elapsed = current_time - self.slash_start
            frame = int(elapsed * self.slash_frames / self.slash_duration)
            frame = max(0, min(frame, self.slash_frames - 1))
            self.slash_index = frame

            if elapsed >= self.slash_duration:
                self.slash_active = False

        if self.facing == "right":
            self.attack_hitbox.midleft = (self.pos.right - 10, self.pos.centery)
        else:
            self.attack_hitbox.midright = (self.pos.left + 10, self.pos.centery)
        if self.arc_active:
            if self.facing == "right":
                self.attack_hitbox.midleft = (self.pos.right, self.pos.centery)
            else:
                self.attack_hitbox.midright = (self.pos.left, self.pos.centery)

            if current_time - self.arc_start_time > self.arc_duration:
                self.arc_active = False
                self.hit_enemies = []
        # Update all bolts
        self.bolts = [bolt for bolt in self.bolts if not bolt.update(enemies)]
        # Update all axes
        self.axes = [axe for axe in self.axes if not axe.update(enemies)]
        # Update flail
        self.flails = [
            flail for flail in self.flails if not flail.update(self, enemies)
        ]

    def set_state(self, new_state):
        if self.state != new_state:
            self.state = new_state
            self.current_anim = self.animations[new_state]
            self.current_anim.reset()

    def draw(self, surface):
        anim = self.current_anim
        frame = anim.sprite_sheet.frames[anim.current_frame]

        offset_x, offset_y = self.offsets[self.state]

        # Flip if facing left
        if self.facing == "left":
            frame = pygame.transform.flip(frame, True, False)
            offset_x = 128 - offset_x

        draw_x = int(self.pos.centerx - offset_x)
        draw_y = int(self.pos.centery - offset_y)

        # Draw centered
        surface.blit(frame, (draw_x, draw_y))

    def grant_ability(self, ability_class):
        new_ability = ability_class()
        if any(ab.name == new_ability.name for ab in self.abilities):
            return
        self.abilities.append(new_ability)
        print(f"Granted {new_ability.name!r}")


class Enemy:
    def __init__(self, image, speed, health):
        self.image = image
        self.speed = speed
        self.health = health
        self.pos = [0.0, 0.0]
        self.rect = self.image.get_rect()

    def get_random_sprite(self):
        raise NotImplementedError("Children contain implementations")

    def move_toward(self, target):
        dx = target[0] - self.pos[0]
        dy = target[1] - self.pos[1]
        distance = math.hypot(dx, dy)
        if distance > 0:
            self.pos[0] += (dx / distance) * self.speed
            self.pos[1] += (dy / distance) * self.speed
        self.rect.center = (round(self.pos[0]), round(self.pos[1]))

    def take_damage(self, damage=2):
        if self.health > 0:
            self.health -= damage
            print(f"Enemy health is {self.health}")
        else:
            print("Enemy health is 0!")


class EasyEnemy(Enemy):
    def __init__(self):
        self.health = 4
        self.speed = 2.0
        self.image = pygame.image.load(self.get_random_sprite()).convert_alpha()
        self.pos = [0.0, 0.0]
        self.rect = self.image.get_rect()
        self.hitbox = (self.image.get_rect()).scale_by(0.55, 0.75)

    def get_random_sprite(self):
        path_to_sprite = os.path.abspath("assets/images/enemies/easy/")
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
        self.pos = [0.0, 0.0]
        self.rect = self.image.get_rect()
        self.hitbox = (self.image.get_rect()).scale_by(0.55, 0.75)

    def get_random_sprite(self):
        path_to_sprite = os.path.abspath("assets/images/enemies/medium/")
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
        self.pos = [0.0, 0.0]
        self.rect = self.image.get_rect()
        self.hitbox = (self.image.get_rect()).scale_by(0.55, 0.75)

    def get_random_sprite(self):
        path_to_sprite = os.path.abspath("assets/images/enemies/hard/")
        sprites = []
        for entry in os.listdir(path_to_sprite):
            full_path = os.path.join(path_to_sprite, entry)
            sprites.append(full_path)
        return sprites[random.randrange(0, 2)]


class SpecialEnemy(Enemy):
    def __init__(self):
        self.health = 30
        self.speed = 2.5
        self.image = pygame.image.load(
            "./assets/images/enemies/special/orc_B8.png"
        ).convert_alpha()
        self.pos = [0.0, 0.0]
        self.rect = self.image.get_rect()
        self.hitbox = (self.image.get_rect()).scale_by(0.55, 0.75)
