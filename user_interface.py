import pygame
from constants import SCREEN_HEIGHT, SCREEN_WIDTH


class HealthBar:
    def __init__(self, player):
        self.player = player
        self.health_bar_width = 200
        self.health_bar_height = 20
        self.bg_color = (255, 0, 0)
        self.health_color = (0, 255, 0)
        self.update()

    def update(self):
        health_ratio = self.player.health / self.player.max_health
        current_health_width = self.health_bar_width * health_ratio
        self.health_rect = pygame.Rect(
            50, 35, self.health_bar_width, self.health_bar_height
        )
        self.current_health_rect = pygame.Rect(
            50, 35, current_health_width, self.health_bar_height
        )

    def draw(self, screen):
        self.update()
        pygame.draw.rect(screen, self.bg_color, self.health_rect)
        pygame.draw.rect(screen, self.health_color, self.current_health_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.health_rect, 2)


class ExperienceBar:
    def __init__(self, player):
        self.player = player
        self.font = pygame.font.SysFont("Arial", 36, bold=True)
        self.text_color = (255, 255, 255)

        # Bar appearance
        self.bar_width = 300
        self.bar_height = 26
        self.bar_padding = 12  # space between level text and bar
        self.bg_color = (30, 30, 50, 180)
        self.fill_color = (0, 200, 255)
        self.border_color = (100, 200, 255)
        self.border_radius = 13

        self.level_surface = None
        self.level_rect = None
        self.update()

    def update(self):
        # Level text
        text = str(self.player.level)
        self.level_surface = self.font.render(text, True, self.text_color)
        self.level_rect = self.level_surface.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 65)
        )

        # XP bar
        self.bar_rect = pygame.Rect(0, 0, self.bar_width, self.bar_height)
        self.bar_rect.midtop = self.level_rect.midbottom
        self.bar_rect.y += self.bar_padding  # gap between text and bar

        # XP calculation
        current_xp = self.player.current_xp
        xp_needed = self.player.get_xp_needed()

        # Current fill amount
        self.fill_amount = max(0.0, min(1.0, current_xp / xp_needed))

        self.fill_rect = self.bar_rect.copy()
        self.fill_rect.width = int(self.bar_rect.width * self.fill_amount)

    def draw(self, screen):
        self.update()

        # 1. XP bar background + border
        pygame.draw.rect(
            screen, self.bg_color, self.bar_rect, border_radius=self.border_radius
        )
        pygame.draw.rect(
            screen,
            self.border_color,
            self.bar_rect,
            width=3,
            border_radius=self.border_radius,
        )

        # 2. XP fill
        if self.fill_amount > 0:
            pygame.draw.rect(
                screen,
                self.fill_color,
                self.fill_rect,
                border_radius=self.border_radius,
            )

        # 3. Level number on top
        screen.blit(self.level_surface, self.level_rect)
