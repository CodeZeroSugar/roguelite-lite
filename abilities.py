import pygame
import math
from constants import SCREEN_HEIGHT, SCREEN_WIDTH


class Ability:
    """Base class for every passive ability."""

    def __init__(self, name, cooldown_frames):
        self.name = name
        self.cooldown_frames = cooldown_frames
        self._timer = 0

    def ready(self):
        """True when the ability may fire."""
        return self._timer <= 0

    def start_cooldown(self):
        """Called right after the ability fires."""
        self._timer = self.cooldown_frames

    def update(self):
        """Call every frame – counts down."""
        if self._timer > 0:
            self._timer -= 1

    def fire(self, player, enemies):
        """Override in subclasses – what the ability actually does."""
        raise NotImplementedError


class AutomaticCrossbow(Ability):
    def __init__(self):
        super().__init__("automatic crossbow", cooldown_frames=90)

    def fire(self, player, enemies):
        if not enemies:
            return
        closest = min(
            enemies,
            key=lambda e: math.hypot(
                e.rect.centerx - player.pos.centerx, e.rect.centery - player.pos.centery
            ),
        )
        MAX_RANGE = 350
        dist = math.hypot(
            closest.rect.centerx - player.pos.centerx,
            closest.rect.centery - player.pos.centery,
        )
        if dist > MAX_RANGE:
            return

        # Spawn bolt towards target
        start_x, start_y = player.pos.center
        target_x, target_y = closest.rect.center
        bolt = Bolt(start_x, start_y, target_x, target_y)

        # Add to bolt list
        player.bolts.append(bolt)

        print(f"Crossbow hit {closest.__class__.__name__} at {closest.rect.center}")


class ThrowingAxes(Ability):
    def __init__(self):
        super().__init__("throwing axes", cooldown_frames=90)

    def fire(self, player, enemies=None):
        start_x, start_y = player.pos.center
        axe_up = Axe(start_x, start_y, "up")
        axe_down = Axe(start_x, start_y, "down")

        player.axes.append(axe_up)
        player.axes.append(axe_down)


class WildFlail(Ability):
    def __init__(self):
        super().__init__("wild flail", cooldown_frames=0)

    def fire(self, player, enemies=None):
        if len(player.flails) < 1:
            flail = Flail()
            player.flails.append(flail)


class Flail:
    def __init__(self):
        self.pos = pygame.Rect(0, 0, 12, 12)

        self.image = pygame.image.load("./items/flail.png").convert_alpha()
        self.radius = 100.0
        self.angle = 0.0
        self.orbit_speed = 0.025

    def update(self, player, enemies):
        self.angle += self.orbit_speed
        self.pos.centerx = player.hitbox.centerx + self.radius * math.cos(self.angle)
        self.pos.centery = player.hitbox.centery + self.radius * math.sin(self.angle)

        for enemy in enemies:
            if self.pos.colliderect(enemy.hitbox):
                enemy.take_damage(2)
                return True

        return False

    def draw(self, surface):
        surface.blit(self.image, self.pos)


class Axe:
    def __init__(self, start_x, start_y, direction, speed=5):
        self.pos = pygame.Rect(0, 0, 65, 70)
        self.pos.center = (start_x, start_y)

        self.image = pygame.image.load("./items/axe.png").convert_alpha()

        self.direction = direction
        self.speed = speed

        self.max_age = 180
        self.age = 0

    def update(self, enemies):
        if self.direction == "up":
            self.pos.y += self.speed
        else:
            self.pos.y -= self.speed

        for enemy in enemies:
            if self.pos.colliderect(enemy.hitbox):
                enemy.take_damage(4)
                return True

        # Remove if too old or off-screen
        if (
            self.pos.right < 0
            or self.pos.left > SCREEN_WIDTH
            or self.pos.bottom < 0
            or self.pos.top > SCREEN_HEIGHT
            or self.age > self.max_age
        ):
            return True
        return False

    def draw(self, surface):
        surface.blit(self.image, self.pos)


class Bolt:
    def __init__(self, start_x, start_y, target_x, target_y, target=None, speed=4):
        self.pos = pygame.Rect(0, 0, 12, 6)
        self.pos.center = (start_x, start_y)
        self.target = target

        dx = target_x - start_x
        dy = target_y - start_y
        distance = math.hypot(dx, dy)
        if distance > 0:
            self.vel_x = (dx / distance) * speed
            self.vel_y = (dy / distance) * speed
        else:
            self.vel_x = self.vel_y = 0

        # Load image of Bolt
        self.image = pygame.image.load("./items/bolt.png").convert_alpha()

        # face in correct direction
        angle = math.degrees(math.atan2(self.vel_y, self.vel_x))
        self.image = pygame.transform.rotate(self.image, -angle)
        self.image = pygame.transform.scale(self.image, (50, 15))
        self.pos = self.image.get_rect(center=(start_x, start_y))

        # Bolt disappears after 3 seconds
        self.max_age = 180
        self.age = 0

    def update(self, enemies):
        self.pos.x += self.vel_x
        self.pos.y += self.vel_y
        self.age += 1

        for enemy in enemies:
            if self.pos.colliderect(enemy.hitbox):
                enemy.take_damage(1)
                return True

        # Remove if too old or off-screen
        if (
            self.pos.right < 0
            or self.pos.left > SCREEN_WIDTH
            or self.pos.bottom < 0
            or self.pos.top > SCREEN_HEIGHT
            or self.age > self.max_age
        ):
            return True
        return False

    def draw(self, surface):
        surface.blit(self.image, self.pos)
