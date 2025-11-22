import pygame
from constants import SCREEN_WIDTH


class Score:
    def __init__(self, player):
        self.player = player
        self.font = pygame.font.Font("./assets/fonts/PublicPixel-rv0pA.ttf", 36)
        self.text_color = (255, 255, 255)
        self.update()

    def update(self):
        score_text = f"Score: {self.player.score}"
        self.score_surface = self.font.render(score_text, True, self.text_color)
        self.score_rect = self.score_surface.get_rect()
        self.score_rect.topright = (SCREEN_WIDTH - 140, 20)

    def draw(self, screen):
        self.update()
        screen.blit(self.score_surface, self.score_rect)
        bg_rect = self.score_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
        screen.blit(self.score_surface, self.score_rect)


class Timer:
    def __init__(self):
        self.image = pygame.image.load(
            "./assets/images/user-interface/time.png"
        ).convert_alpha()
        self.image_rect = self.image.get_rect()
        self.font = pygame.font.Font("./assets/fonts/PublicPixel-rv0pA.ttf", 24)
        self.text_color = (255, 255, 255)

    def update(self, rem_seconds):
        minutes = rem_seconds // 60
        seconds = rem_seconds % 60
        timer_text = f"{minutes:02d}:{seconds:02d}"
        self.timer_surface = self.font.render(timer_text, True, self.text_color)
        self.timer_rect = self.timer_surface.get_rect()
        self.timer_rect.topright = (SCREEN_WIDTH - 25, 28)
        self.image_rect.midtop = (SCREEN_WIDTH - 20, -42)

    def draw(self, screen, seconds):
        self.update(seconds)
        screen.blit(self.image, self.image_rect)
        screen.blit(self.timer_surface, self.timer_rect)


class HealthBar:
    def __init__(self, player):
        self.player = player
        self.image = pygame.image.load(
            "./assets/images/user-interface/Heart_Bar_3.png"
        ).convert_alpha()
        self.image_rect = self.image.get_rect()
        self.health_bar_width = 282
        self.health_bar_height = 22
        self.pos = (78, 30)
        self.bg_color = (255, 0, 0)
        self.health_color = (0, 255, 0)
        self.update()

    def update(self):
        health_ratio = self.player.health / self.player.max_health
        current_health_width = self.health_bar_width * health_ratio
        self.health_rect = pygame.Rect(
            self.pos[0], self.pos[1], self.health_bar_width, self.health_bar_height
        )
        self.current_health_rect = pygame.Rect(
            self.pos[0], self.pos[1], current_health_width, self.health_bar_height
        )
        self.image_rect.midtop = (190, 0)

    def draw(self, screen):
        self.update()
        pygame.draw.rect(screen, self.bg_color, self.health_rect)
        pygame.draw.rect(screen, self.health_color, self.current_health_rect)
        screen.blit(self.image, self.image_rect)


class PlayerLevel:
    def __init__(self, player):
        self.player = player
        self.font = pygame.font.Font("./assets/fonts/PublicPixel-rv0pA.ttf", 24)
        self.text_color = (255, 255, 255)
        self.update()

    def update(self):
        self.text = str(self.player.level)
        if self.player.level >= 10:
            self.font = pygame.font.Font("./assets/fonts/PublicPixel-rv0pA.ttf", 16)
            self.level_surface = self.font.render(self.text, True, self.text_color)
            self.level_rect = self.level_surface.get_rect()
            self.level_rect.topright = (52, 26)
        else:
            self.level_surface = self.font.render(self.text, True, self.text_color)
            self.level_rect = self.level_surface.get_rect()
            self.level_rect.topright = (52, 22)

    def draw(self, screen):
        self.update()
        screen.blit(self.level_surface, self.level_rect)


class ExperienceBar:
    def __init__(self, player):
        self.player = player

        # Bar appearance
        self.bar_width = 280
        self.bar_height = 16
        self.bar_padding = 12  # space between level text and bar
        self.bg_color = (30, 30, 50, 180)
        self.fill_color = (0, 200, 255)
        self.border_color = (100, 200, 255)
        self.border_radius = 6

        self.update()

    def update(self):
        # XP bar
        self.bar_rect = pygame.Rect(78, 50, self.bar_width, self.bar_height)
        # self.bar_rect.midtop = self.level_rect.midbottom
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

        # 1. XP bar background
        pygame.draw.rect(
            screen, self.bg_color, self.bar_rect, border_radius=self.border_radius
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
        # screen.blit(self.level_surface, self.level_rect)
