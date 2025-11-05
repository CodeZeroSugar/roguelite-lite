import pygame
import random
from constants import SCREEN_HEIGHT, SCREEN_WIDTH


class Food:
    def __init__(self):
        self.image = pygame.image.load("./items/81_pizza.png").convert_alpha()
        self.food_rect = self.image.get_rect().move(
            random.randint(0, SCREEN_WIDTH - 20), random.randint(0, SCREEN_HEIGHT - 20)
        )
        self.health_amount = 5

    def get_eaten(self, player):
        lost_health = player.max_health - player.health
        if self.health_amount > lost_health:
            player.health += lost_health
            print("Player healed to full")

        else:
            player.health += self.health_amount
            print("Player healed 5 points")
