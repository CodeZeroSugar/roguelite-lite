import pygame


class SpriteSheet:
    def __init__(self, filename, frame_count):
        """
        Loads 128x128 sprite sheet (1 row, left to right)
        - filename: path to sprite sheet
        - frame_count: Number of frames in the row
        """
        self.sheet = pygame.image.load(filename).convert_alpha()
        self.frame_count = frame_count
        self.frame_width = 128
        self.frame_height = 128

        # validate sheet dimensions
        expected_width = frame_count * self.frame_width
        actual_width = self.sheet.get_width()
        if actual_width < expected_width:
            raise ValueError(
                f"Sprite sheet too narrow! Expected {expected_width}px, got {actual_width}px."
            )
        if self.sheet.get_height() != self.frame_height:
            raise ValueError(
                f"Sprite sheet height must be 128x, got {self.sheet.get_height()}px."
            )

        self.frames = []
        for i in range(frame_count):
            x = i * self.frame_width
            rect = pygame.Rect(x, 0, self.frame_width, self.frame_height)
            frame = self.sheet.subsurface(rect)
            self.frames.append(frame)


class Animation:
    def __init__(self, sprite_sheet, base_fps=12, loop=True, speed_multiplier=1.0):
        self.sprite_sheet = sprite_sheet
        self.base_fps = base_fps
        self.speed_multiplier = speed_multiplier
        self.frame_delay = int(1000 / (base_fps * speed_multiplier))
        self.loop = loop
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.finished = False

    def update(self):
        if self.finished:
            return
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_delay:
            self.last_update = now
            self.current_frame += 1
            if self.current_frame >= self.sprite_sheet.frame_count:
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = self.sprite_sheet.frame_count - 1
                    self.finished = True

    def draw(self, surface, position):
        if not self.finished:
            surface.blit(self.sprite_sheet.frames[self.current_frame], position)

    def get_fps(self):
        """Returns current playback FPS for debugging)."""
        return 1000 / self.frame_delay

    def set_speed(self, multiplier):
        """Dynamically adjust speed"""
        self.speed_multiplier = multiplier
        self.frame_delay = int(1000 / (self.base_fps * multiplier))

    def reset(self):
        self.current_frame = 0
        self.finished = False
        self.last_update = pygame.time.get_ticks()


def get_center_offset(sheet: SpriteSheet, frame_index: int = 0) -> tuple[int, int]:
    frame = sheet.frames[frame_index]
    w, h = frame.get_size()

    # Find left-most non-transparent pixel
    left = 0
    for x in range(w):
        for y in range(h):
            if frame.get_at((x, y))[3] > 0:  # alpha > 0
                left = x
                break
        else:
            continue
        break

    # Find right-most
    right = w - 1
    for x in range(w - 1, -1, -1):
        for y in range(h):
            if frame.get_at((x, y))[3] > 0:
                right = x
                break
        else:
            continue
        break

    # Find top-most
    top = 0
    for y in range(h):
        for x in range(w):
            if frame.get_at((x, y))[3] > 0:
                top = y
                break
        else:
            continue
        break

    # Find bottom-most
    bottom = h - 1
    for y in range(h - 1, -1, -1):
        for x in range(w):
            if frame.get_at((x, y))[3] > 0:
                bottom = y
                break
        else:
            continue
        break

    # Visual center
    center_x = (left + right) // 2
    center_y = (top + bottom) // 2

    # Offset from top-left of the *frame*
    offset_x = center_x
    offset_y = center_y
    return offset_x, offset_y
