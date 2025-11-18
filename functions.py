import random
from abilities import AutomaticCrossbow, ThrowingAxes, WildFlail
from constants import SCREEN_HEIGHT, SCREEN_WIDTH, SPRITE_HEIGHT, SPRITE_WIDTH
from classes import EasyEnemy, MediumEnemy, HardEnemy, SpecialEnemy


def new_ability(player):
    options = [AutomaticCrossbow, ThrowingAxes, WildFlail]
    available = [
        cls
        for cls in options
        if not any(ab.name == cls().name for ab in player.abilities)
    ]
    if not available:
        print("No new abilities available")
        return

    chosen = random.choice(options)
    player.grant_ability(chosen)


def check_level(score_counter, player):
    current_level = player.level
    next_level = current_level + 1
    score_needed = next_level**1.5
    if score_counter >= score_needed:
        player.level += 1
        print(f"Player level up! Level is now: {player.level}")

        if player.level % 5 == 0:
            print("Time to pick a new ability!")
            new_ability(player)


def place_enemy(enemy):
    edge = random.choice(["top", "bottom", "left", "right"])

    if edge == "top":
        enemy.pos[0] = random.uniform(0, SCREEN_WIDTH)
        enemy.pos[1] = 0.0
    elif edge == "bottom":
        enemy.pos[0] = random.uniform(0, SCREEN_WIDTH)
        enemy.pos[1] = SCREEN_HEIGHT - SPRITE_HEIGHT
    elif edge == "left":
        enemy.pos[0] = 0.0
        enemy.pos[1] = random.uniform(0, SCREEN_HEIGHT)
    else:
        enemy.pos[0] = SCREEN_WIDTH - SPRITE_WIDTH
        enemy.pos[1] = random.uniform(0, SCREEN_HEIGHT)

    enemy.rect.center = (int(enemy.pos[0]), int(enemy.pos[1]))


def choose_enemy_type(elapsed_sec):
    if random.randrange(0, 101) == 1:
        return SpecialEnemy
    if elapsed_sec < 180:
        return EasyEnemy
    elif 180 <= elapsed_sec < 300:
        return random.choice([EasyEnemy, MediumEnemy])
    elif 300 <= elapsed_sec < 540:
        return MediumEnemy
    elif 540 <= elapsed_sec < 600:
        return random.choice([EasyEnemy, MediumEnemy, HardEnemy])
    else:
        return None
