import os

os.environ["SDL_AUDIODRIVER"] = "pulse"
import pygame

pygame.mixer.pre_init(44100, -16, 2, 16384)
pygame.init()
music = pygame.mixer.Sound("./music/pixelated_carnage_1.wav")
music.play(-1)
pygame.time.wait(120000)  # 2 min
pygame.quit()
