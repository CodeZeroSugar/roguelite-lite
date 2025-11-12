import pygame
import math

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
        super().__init__("automatic crossbow", cooldown_frames=60)   

    def fire(self, player, enemies):
        if not enemies:
            return
        closest = min(
            enemies,
            key=lambda e: math.hypot(e.rect.centerx - player.pos.centerx,
                                    e.rect.centery - player.pos.centery)
        )
        MAX_RANGE = 350
        dist = math.hypot(closest.rect.centerx - player.pos.centerx,
                          closest.rect.centery - player.pos.centery)
        if dist > MAX_RANGE:
            return

        closest.health -= 1
        print(f"Crossbow hit {closest.__class__.__name__} at {closest.rect.center}")
