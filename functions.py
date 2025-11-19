import random
import classes
from abilities import AutomaticCrossbow, ThrowingAxes, WildFlail
from constants import SCREEN_HEIGHT, SCREEN_WIDTH, SPRITE_HEIGHT, SPRITE_WIDTH


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


def check_level(player):
    current_level = player.level
    next_level = current_level + 1
    score_needed = next_level**1.5
    if player.score >= score_needed:
        player.level += 1
        print(f"Player level up! Level is now: {player.level}")

        if player.level % 5 == 0:
            print("Time to pick a new ability!")
            new_ability(player)

        return True
    return False


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
        return classes.SpecialEnemy
    elif elapsed_sec < 180:
        return classes.EasyEnemy
    elif 180 <= elapsed_sec < 300:
        return random.choice([classes.EasyEnemy, classes.MediumEnemy])
    elif 300 <= elapsed_sec < 540:
        return classes.MediumEnemy
    elif 540 <= elapsed_sec < 600:
        return random.choice(
            [classes.EasyEnemy, classes.MediumEnemy, classes.HardEnemy]
        )
    else:
        return None
