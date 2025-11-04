import pygame


class Food:
    def __init__(self, image):
        self.image = pygame.Rect(0, 0, 20, 20)
        self.health_amount = 5

    def get_eaten(self, player):
        lost_health = player.max_health - player.health
        if self.health_amount > lost_health:
            player.health += lost_health

        else:
            player.health += self.health_amount
