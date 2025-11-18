import pygame
import random
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from classes import Player, EasyEnemy, MediumEnemy, HardEnemy
from items import Food
from functions import check_level, choose_enemy_type, place_enemy
from game_state import GameState


def main():
    print("Starting Roguelite-lite!")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")

    pygame.mixer.pre_init(frequency=48000, size=-16, channels=2, buffer=65536)
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # initialize music
    music = pygame.mixer.Sound("./assets/music/pixelated_carnage_1.wav")
    music.play(-1)

    running = True
    play_game = False

    title_background = pygame.image.load(
        "./assets/images/backgrounds/menu_screen.png"
    ).convert()
    death_screen = pygame.image.load(
        "./assets/images/backgrounds/death_screen.png"
    ).convert()

    player = pygame.image.load("./assets/images/player.png").convert_alpha()

    background = pygame.image.load(
        "./assets/images/backgrounds/dungeon_brick_wall_blue.png"
    ).convert()

    screen.blit(background, (0, 0))

    # Player init
    p = Player(player, 2.0, 10, 10)
    health_bar_pos = (50, 35)
    health_bar_width = 200
    health_bar_height = 20
    background_color = (255, 0, 0)
    health_color = (0, 255, 0)

    # Initialize in game items
    food_objects = []

    # Font for timer
    font = pygame.font.SysFont("Arial", 36, bold=True)
    remaining_sec = 0
    remaining_ms = 0

    # Where enemies live
    objects = []

    score_counter = 0

    spawn_interval = random.randint(0, 2000)
    timer_started = False
    start_time = 0
    last_spawn_time = 0
    ROUND_DURATION_MS = 600_000
    # 600_000

    # Cooldown initialization
    damage_tick = 0
    damaged = False

    create_food = False

    attack_cooldown = 0
    on_cooldown = False

    state_input = GameState.MENU

    while running:
        match state_input:
            case GameState.MENU:
                # Title Screen
                while True:
                    for event in pygame.event.get():
                        if (
                            event.type == pygame.KEYDOWN
                            and not pygame.key.get_pressed()[pygame.K_q]
                            and not pygame.key.get_pressed()[pygame.K_ESCAPE]
                        ):
                            state_input = GameState.PLAY
                            play_game = True
                        if (
                            pygame.key.get_pressed()[pygame.K_q]
                            or pygame.key.get_pressed()[pygame.K_ESCAPE]
                        ):
                            pygame.quit()
                    screen.blit(title_background, (0, 0))
                    pygame.display.flip()
                    clock.tick(60)
                    if play_game:
                        break

            case GameState.PLAY:
                while True:
                    # Start Timer
                    if not timer_started:
                        start_time = pygame.time.get_ticks()
                        last_spawn_time = start_time
                        timer_started = True

                    # check if player leveled up
                    check_level(score_counter, p)

                    current_time = pygame.time.get_ticks()

                    elapsed_ms = current_time - start_time
                    remaining_ms = max(0, ROUND_DURATION_MS - elapsed_ms)
                    elapsed_sec = elapsed_ms // 1000
                    remaining_sec = remaining_ms // 1000
                    # Round lasts 10 minutes
                    if remaining_ms <= 0:
                        print("Round over!")
                        state_input = GameState.WIN
                        break
                    # Spawn logic
                    if current_time - last_spawn_time >= spawn_interval:
                        enemy_class = choose_enemy_type(elapsed_sec)
                        if enemy_class:
                            o = enemy_class()
                            place_enemy(o)
                            objects.append(o)
                        last_spawn_time = current_time
                        spawn_interval = random.randint(1000, 3000)

                    # Player input
                    p.update(objects)

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE and not on_cooldown:
                                p.basic_attack(screen)
                                p.start_slash()
                                on_cooldown = True

                    # Update logic
                    target = p.pos.center
                    p.update(objects)

                    # Update bolts
                    p.bolts = [bolt for bolt in p.bolts if not bolt.update(objects)]

                    # Update axes
                    p.axes = [axe for axe in p.axes if not axe.update(objects)]

                    # Update flail
                    p.flails = [
                        flail for flail in p.flails if not flail.update(p, objects)
                    ]

                    # Move enemies
                    for o in objects:
                        o.move_toward(target)

                    # Player damaged
                    for o in objects:
                        if o.hitbox.colliderect(p.hitbox) and damage_tick == 0:
                            p.take_damage()
                            damaged = True
                            damage_tick = 1

                    # Enemy damage
                    if p.arc_active:
                        p.draw_arc(screen)
                        for o in objects:
                            if o.hitbox.colliderect(p.attack_hitbox):
                                if o not in p.hit_enemies:
                                    o.take_damage()
                                    p.hit_enemies.append(o)

                    # Player ability block
                    for ab in p.abilities:
                        ab.update()

                    for ab in p.abilities:
                        if ab.ready():
                            ab.fire(p, objects)
                            ab.start_cooldown()

                    # Increment score
                    for o in objects:
                        if o.health <= 0:
                            if type(o) is EasyEnemy:
                                score_counter += 1
                            if type(o) is MediumEnemy:
                                score_counter += 3
                            if type(o) is HardEnemy:
                                score_counter += 5
                            create_food = True

                    # Food chance
                    if create_food is True:
                        print("Attempting to spawn food")
                        if random.randrange(0, 101) <= 10:
                            print("creating food!")
                            food_objects.append(Food())
                            print(f"Number of food on screen: {len(food_objects)}")
                            create_food = False

                    # Player eats food
                    for food in food_objects:
                        if food.food_rect.colliderect(p.hitbox):
                            print("Food Eaten")
                            food.get_eaten(p)

                    food_objects = [
                        food
                        for food in food_objects
                        if not food.food_rect.colliderect(p.hitbox)
                    ]

                    # Remove dead enemies
                    objects = [o for o in objects if o.health > 0]

                    # Check if dead
                    if p.health <= 0:
                        print("You died!")
                        state_input = GameState.LOSE

                        break

                    # Draw
                    screen.blit(background, (0, 0))
                    p.hitbox.center = p.pos.center
                    for o in objects:
                        o.hitbox.center = o.rect.center

                    # health bar
                    health_ratio = p.health / p.max_health
                    current_health_width = health_bar_width * health_ratio

                    pygame.draw.rect(
                        screen,
                        background_color,
                        (
                            health_bar_pos[0],
                            health_bar_pos[1],
                            health_bar_width,
                            health_bar_height,
                        ),
                    )
                    pygame.draw.rect(
                        screen,
                        health_color,
                        (
                            health_bar_pos[0],
                            health_bar_pos[1],
                            current_health_width,
                            health_bar_height,
                        ),
                    )
                    pygame.draw.rect(
                        screen,
                        (255, 255, 255),
                        (
                            health_bar_pos[0],
                            health_bar_pos[1],
                            health_bar_width,
                            health_bar_height,
                        ),
                        2,
                    )

                    p.draw(screen)

                    # slash
                    if p.slash_active:
                        src_rect = pygame.Rect(
                            p.slash_index * p.slash_w, 0, p.slash_w, p.slash_h
                        )
                        frame = p.slash_sheet.subsurface(src_rect)
                        if p.facing == "left":
                            frame = pygame.transform.flip(frame, True, False)
                        dst_rect = frame.get_rect()
                        offset = 18
                        if p.facing == "right":
                            dst_rect.midleft = (p.pos.right - offset, p.pos.centery)
                        else:
                            dst_rect.midright = (p.pos.left + offset, p.pos.centery)

                        screen.blit(frame, dst_rect)

                    for food in food_objects:
                        screen.blit(food.image, food.food_rect)

                    for o in objects:
                        screen.blit(o.image, o.rect)

                    # draw bolts
                    for bolt in p.bolts:
                        bolt.draw(screen)

                    # draw axes
                    for axe in p.axes:
                        axe.draw(screen)

                    # draw flail
                    for flail in p.flails:
                        flail.draw(screen)

                    # Draw Timer
                    minutes = remaining_sec // 60
                    seconds = remaining_sec % 60
                    timer_text = f"{minutes:02d}:{seconds:02d}"
                    timer_surface = font.render(timer_text, True, (255, 255, 255))
                    timer_rect = timer_surface.get_rect()
                    timer_rect.topright = (SCREEN_WIDTH - 20, 20)
                    screen.blit(timer_surface, timer_rect)
                    bg_rect = timer_rect.inflate(20, 10)
                    pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
                    screen.blit(timer_surface, timer_rect)

                    # Draw Score score_counter
                    score_text = f"Score: {score_counter}"
                    score_surface = font.render(score_text, True, (255, 255, 255))
                    score_rect = score_surface.get_rect()
                    score_rect.topright = (SCREEN_WIDTH - 140, 20)
                    screen.blit(score_surface, score_rect)
                    bg_score = score_rect.inflate(20, 10)
                    pygame.draw.rect(screen, (0, 0, 0, 180), bg_score)
                    screen.blit(score_surface, score_rect)

                    # Cooldowns
                    create_food = False

                    if damaged:
                        damage_tick += 1
                        if damage_tick > 30:
                            damage_tick = 0
                            damaged = False

                    if on_cooldown:
                        attack_cooldown += 1
                        if attack_cooldown > 20:
                            attack_cooldown = 0
                            on_cooldown = False

                    pygame.display.update()

                    clock.tick(60)

                    # Check to break
                    if not running:
                        break

            case GameState.LOSE:
                play_game = False
                while True:
                    for event in pygame.event.get():
                        if (
                            event.type == pygame.KEYDOWN
                            and not pygame.key.get_pressed()[pygame.K_q]
                            and not pygame.key.get_pressed()[pygame.K_ESCAPE]
                        ):
                            state_input = GameState.PLAY
                            play_game = True
                        if (
                            pygame.key.get_pressed()[pygame.K_q]
                            or pygame.key.get_pressed()[pygame.K_ESCAPE]
                        ):
                            pygame.quit()

                    screen.blit(death_screen, (0, 0))
                    # Draw Timer
                    minutes = remaining_sec // 60
                    seconds = remaining_sec % 60
                    timer_text = f"{minutes:02d}:{seconds:02d}"
                    timer_surface = font.render(timer_text, True, (255, 255, 255))
                    timer_rect = timer_surface.get_rect()
                    timer_rect.topright = (SCREEN_WIDTH - 20, 20)
                    screen.blit(timer_surface, timer_rect)
                    bg_rect = timer_rect.inflate(20, 10)
                    pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
                    screen.blit(timer_surface, timer_rect)

                    # Draw Score score_counter
                    score_text = f"Score: {score_counter}"
                    score_surface = font.render(score_text, True, (255, 255, 255))
                    score_rect = score_surface.get_rect()
                    score_rect.topright = (SCREEN_WIDTH - 140, 20)
                    screen.blit(score_surface, score_rect)
                    bg_score = score_rect.inflate(20, 10)
                    pygame.draw.rect(screen, (0, 0, 0, 180), bg_score)
                    screen.blit(score_surface, score_rect)

                    pygame.display.flip()
                    clock.tick(60)
                    if play_game:
                        main()

            case GameState.WIN:
                play_game = False
                while True:
                    for event in pygame.event.get():
                        if (
                            event.type == pygame.KEYDOWN
                            and not pygame.key.get_pressed()[pygame.K_q]
                            and not pygame.key.get_pressed()[pygame.K_ESCAPE]
                        ):
                            state_input = GameState.PLAY
                            play_game = True
                        if (
                            pygame.key.get_pressed()[pygame.K_q]
                            or pygame.key.get_pressed()[pygame.K_ESCAPE]
                        ):
                            pygame.quit()

                    screen.blit(title_background, (0, 0))

                    # Draw Timer
                    minutes = remaining_sec // 60
                    seconds = remaining_sec % 60
                    timer_text = f"{minutes:02d}:{seconds:02d}"
                    timer_surface = font.render(timer_text, True, (255, 255, 255))
                    timer_rect = timer_surface.get_rect()
                    timer_rect.topright = (SCREEN_WIDTH - 20, 20)
                    screen.blit(timer_surface, timer_rect)
                    bg_rect = timer_rect.inflate(20, 10)
                    pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
                    screen.blit(timer_surface, timer_rect)

                    # Draw Score score_counter
                    score_text = f"Score: {score_counter}"
                    score_surface = font.render(score_text, True, (255, 255, 255))
                    score_rect = score_surface.get_rect()
                    score_rect.topright = (SCREEN_WIDTH - 140, 20)
                    screen.blit(score_surface, score_rect)
                    bg_score = score_rect.inflate(20, 10)
                    pygame.draw.rect(screen, (0, 0, 0, 180), bg_score)
                    screen.blit(score_surface, score_rect)

                    pygame.display.flip()
                    clock.tick(60)
                    if play_game:
                        main()

    pygame.quit()


if __name__ == "__main__":
    main()
