import pygame
from constants import SCREEN_HEIGHT, SCREEN_WIDTH


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

        # Current fill amount
        if self.player.max_xp > 0:
            self.fill_amount = self.player.current_xp / self.player.max_xp
        else:
            self.fill_amount = 0.0

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
