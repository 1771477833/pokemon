"""统一按键定义。"""

import pygame

# 开始游戏（标题画面）
KEY_START = pygame.K_RETURN

# 确认 / 取消（游戏中）
KEY_CONFIRM = pygame.K_j
KEY_CANCEL = pygame.K_k

# 移动：WASD + 方向键
KEY_UP = pygame.K_w
KEY_DOWN = pygame.K_s
KEY_LEFT = pygame.K_a
KEY_RIGHT = pygame.K_d

KEY_UP_ALT = pygame.K_UP
KEY_DOWN_ALT = pygame.K_DOWN
KEY_LEFT_ALT = pygame.K_LEFT
KEY_RIGHT_ALT = pygame.K_RIGHT

# 系统
KEY_MENU = pygame.K_ESCAPE

MOVE_COOLDOWN_FRAMES = 10


def is_confirm(key: int) -> bool:
    return key == KEY_CONFIRM


def is_cancel(key: int) -> bool:
    return key == KEY_CANCEL


def is_start(key: int) -> bool:
    return key in (KEY_START, pygame.K_SPACE)


def read_movement(keys) -> tuple[int, int] | None:
    """
    读取移动输入，返回 (dx, dy)。
    同时支持 WASD 与方向键。
    """
    if keys[KEY_UP] or keys[KEY_UP_ALT]:
        return 0, -1
    if keys[KEY_DOWN] or keys[KEY_DOWN_ALT]:
        return 0, 1
    if keys[KEY_LEFT] or keys[KEY_LEFT_ALT]:
        return -1, 0
    if keys[KEY_RIGHT] or keys[KEY_RIGHT_ALT]:
        return 1, 0
    return None


def movement_from_key(key: int) -> tuple[int, int] | None:
    """单次按键（KEYDOWN）的移动/方向输入。"""
    if key == KEY_UP or key == KEY_UP_ALT:
        return 0, -1
    if key == KEY_DOWN or key == KEY_DOWN_ALT:
        return 0, 1
    if key == KEY_LEFT or key == KEY_LEFT_ALT:
        return -1, 0
    if key == KEY_RIGHT or key == KEY_RIGHT_ALT:
        return 1, 0
    return None
