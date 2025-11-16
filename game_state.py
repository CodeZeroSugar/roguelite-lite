from enum import Enum


class GameState(Enum):
    MENU = 1
    PLAY = 2
    LOSE = 3
    WIN = 4
    QUIT = 5
