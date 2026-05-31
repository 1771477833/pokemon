"""瓦片贴图、角色动画与战斗精灵。"""

from __future__ import annotations

from pathlib import Path

import pygame

from .data import SPECIES
from .map import (
    TILE_CENTER,
    TILE_FENCE,
    TILE_GRASS,
    TILE_HOUSE,
    TILE_PATH,
    TILE_SHOP,
    TILE_TREE,
    TILE_WALL,
    TILE_WATER,
)

TILE_SIZE = 16
BATTLE_SPRITE_SIZE = 48
ASSET_VERSION = 3

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
TILESET_PATH = ASSETS_DIR / "tileset.png"
SPRITES_PATH = ASSETS_DIR / "sprites.png"
BATTLE_SPRITES_PATH = ASSETS_DIR / "battle_sprites.png"
BATTLE_BG_PATH = ASSETS_DIR / "battle_bg.png"
VERSION_PATH = ASSETS_DIR / ".asset_version"

# 方向: 0=下 1=上 2=左 3=右
DIR_DOWN, DIR_UP, DIR_LEFT, DIR_RIGHT = 0, 1, 2, 3
WALK_FRAMES = 2

# tileset 横向排列顺序（W 占 3 帧动画）
TILE_SHEET_ORDER: list[str | tuple[str, int]] = [
    TILE_GRASS, TILE_PATH, TILE_WALL,
    (TILE_WATER, 3),
    TILE_TREE, TILE_HOUSE, TILE_FENCE,
    TILE_CENTER, TILE_SHOP,
]

# 物种 → 战斗精灵配色 (body, accent, highlight)
POKE_COLORS: dict[str, tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]]] = {
    "bulbasaur": ((72, 168, 72), (48, 120, 48), (136, 208, 96)),
    "charmander": ((240, 128, 48), (200, 64, 32), (255, 200, 80)),
    "squirtle": ((80, 144, 224), (48, 96, 176), (160, 200, 248)),
    "pikachu": ((240, 208, 48), (200, 160, 32), (255, 240, 120)),
    "rattata": ((168, 128, 96), (120, 88, 64), (200, 160, 128)),
    "pidgey": ((176, 144, 96), (120, 96, 64), (220, 200, 160)),
}


def _shade(color: tuple[int, int, int], delta: int) -> tuple[int, int, int]:
    return tuple(max(0, min(255, c + delta)) for c in color)


def _draw_grass_tile(surf: pygame.Surface) -> None:
    base = (88, 168, 72)
    surf.fill(base)
    for x in range(0, TILE_SIZE, 4):
        for y in range(0, TILE_SIZE, 4):
            c = (120, 200, 88) if (x + y) % 8 == 0 else (64, 136, 56)
            pygame.draw.rect(surf, c, (x + 1, y + 1, 2, 2))


def _draw_path_tile(surf: pygame.Surface) -> None:
    base = (196, 164, 108)
    surf.fill(base)
    for i in range(4):
        pygame.draw.circle(surf, _shade(base, -18), (3 + i * 4, 5 + i * 2), 1)


def _draw_wall_tile(surf: pygame.Surface) -> None:
    base = (96, 88, 72)
    surf.fill(base)
    pygame.draw.rect(surf, _shade(base, -24), (0, 0, TILE_SIZE, TILE_SIZE), 1)


def _draw_water_tile(surf: pygame.Surface, frame: int = 0) -> None:
    colors = [(64, 128, 216), (72, 140, 224), (56, 120, 208)]
    surf.fill(colors[frame % 3])
    for x in range(2, TILE_SIZE, 5):
        pygame.draw.arc(surf, (180, 220, 255), (x - 2, 4 + (frame + x) % 3, 6, 4), 0, 3.14, 1)


def _draw_tree_tile(surf: pygame.Surface) -> None:
    surf.fill((64, 136, 56))
    pygame.draw.rect(surf, (96, 64, 32), (7, 10, 2, 6))
    pygame.draw.circle(surf, (48, 120, 48), (8, 7), 6)
    pygame.draw.circle(surf, (64, 152, 64), (8, 6), 4)
    pygame.draw.circle(surf, (88, 184, 72), (6, 5), 2)


def _draw_house_tile(surf: pygame.Surface) -> None:
    surf.fill((64, 136, 56))
    pygame.draw.rect(surf, (200, 176, 128), (3, 8, 10, 7))
    pygame.draw.polygon(surf, (192, 64, 64), [(2, 8), (8, 2), (14, 8)])
    pygame.draw.rect(surf, (96, 64, 32), (7, 11, 3, 4))
    pygame.draw.rect(surf, (136, 200, 240), (4, 9, 2, 2))


def _draw_fence_tile(surf: pygame.Surface) -> None:
    surf.fill((64, 136, 56))
    for x in (2, 7, 12):
        pygame.draw.rect(surf, (200, 176, 128), (x, 4, 2, 10))
    for y in (6, 10):
        pygame.draw.rect(surf, (176, 144, 96), (1, y, 14, 2))


def _draw_center_tile(surf: pygame.Surface) -> None:
    surf.fill((64, 136, 56))
    pygame.draw.rect(surf, (240, 240, 248), (2, 3, 12, 11))
    pygame.draw.rect(surf, (240, 96, 112), (2, 3, 12, 3))
    pygame.draw.rect(surf, (248, 248, 248), (6, 7, 4, 4))
    pygame.draw.line(surf, (240, 96, 112), (8, 7), (8, 11), 1)


def _draw_shop_tile(surf: pygame.Surface) -> None:
    surf.fill((64, 136, 56))
    pygame.draw.rect(surf, (248, 208, 128), (2, 5, 12, 9))
    pygame.draw.rect(surf, (240, 128, 64), (2, 5, 12, 3))
    pygame.draw.rect(surf, (248, 248, 248), (4, 9, 3, 3))
    pygame.draw.rect(surf, (248, 248, 248), (9, 9, 3, 3))
    pygame.draw.rect(surf, (96, 64, 32), (7, 11, 2, 3))


def _draw_character(
    surf: pygame.Surface,
    *,
    body: tuple[int, int, int],
    pants: tuple[int, int, int],
    direction: int,
    frame: int,
) -> None:
    surf.fill((0, 0, 0, 0))
    bob = frame % WALK_FRAMES
    leg_offset = 1 if bob else 0

    if direction == DIR_DOWN:
        pygame.draw.rect(surf, (248, 208, 160), (6, 2, 4, 3))
        pygame.draw.rect(surf, body, (5, 5, 6, 5))
        pygame.draw.rect(surf, pants, (4 + leg_offset, 10, 3, 4))
        pygame.draw.rect(surf, pants, (9 - leg_offset, 10, 3, 4))
    elif direction == DIR_UP:
        pygame.draw.rect(surf, body, (5, 4, 6, 6))
        pygame.draw.rect(surf, pants, (4 + leg_offset, 10, 3, 4))
        pygame.draw.rect(surf, pants, (9 - leg_offset, 10, 3, 4))
        pygame.draw.rect(surf, (248, 208, 160), (6, 2, 4, 2))
    elif direction == DIR_LEFT:
        pygame.draw.rect(surf, (248, 208, 160), (4, 2, 3, 3))
        pygame.draw.rect(surf, body, (4, 5, 5, 5))
        pygame.draw.rect(surf, pants, (3 + leg_offset, 10, 3, 4))
        pygame.draw.rect(surf, pants, (7 - leg_offset, 10, 2, 4))
    else:
        pygame.draw.rect(surf, (248, 208, 160), (9, 2, 3, 3))
        pygame.draw.rect(surf, body, (7, 5, 5, 5))
        pygame.draw.rect(surf, pants, (7 + leg_offset, 10, 2, 4))
        pygame.draw.rect(surf, pants, (11 - leg_offset, 10, 3, 4))


def _draw_battle_pokemon(surf: pygame.Surface, species_id: str, *, back: bool = False) -> None:
    body, accent, highlight = POKE_COLORS.get(species_id, ((160, 160, 160), (120, 120, 120), (200, 200, 200)))
    surf.fill((0, 0, 0, 0))
    cx, cy = BATTLE_SPRITE_SIZE // 2, BATTLE_SPRITE_SIZE // 2 + 4

    if species_id == "pikachu":
        pygame.draw.ellipse(surf, body, (cx - 14, cy - 10, 28, 22))
        pygame.draw.polygon(surf, body, [(cx - 10, cy - 12), (cx - 14, cy - 22), (cx - 6, cy - 14)])
        pygame.draw.polygon(surf, body, [(cx + 10, cy - 12), (cx + 14, cy - 22), (cx + 6, cy - 14)])
        pygame.draw.circle(surf, highlight, (cx - 5, cy - 4), 2)
        pygame.draw.circle(surf, highlight, (cx + 5, cy - 4), 2)
        if not back:
            pygame.draw.circle(surf, (32, 32, 32), (cx - 5, cy - 4), 1)
            pygame.draw.circle(surf, (32, 32, 32), (cx + 5, cy - 4), 1)
    elif species_id == "charmander":
        pygame.draw.ellipse(surf, body, (cx - 12, cy - 8, 24, 20))
        pygame.draw.ellipse(surf, highlight, (cx + 8, cy - 2, 8, 8))
        pygame.draw.circle(surf, (32, 32, 32), (cx - 4, cy - 4), 1)
    elif species_id == "squirtle":
        pygame.draw.ellipse(surf, body, (cx - 13, cy - 8, 26, 20))
        pygame.draw.circle(surf, accent, (cx, cy - 6), 8)
        pygame.draw.circle(surf, (32, 32, 32), (cx - 4, cy - 4), 1)
    elif species_id == "bulbasaur":
        pygame.draw.ellipse(surf, body, (cx - 13, cy - 6, 26, 18))
        pygame.draw.circle(surf, accent, (cx, cy - 12), 9)
        pygame.draw.circle(surf, (32, 32, 32), (cx - 4, cy - 2), 1)
    elif species_id == "rattata":
        pygame.draw.ellipse(surf, body, (cx - 14, cy - 6, 28, 14))
        pygame.draw.line(surf, accent, (cx + 12, cy - 4), (cx + 18, cy - 8), 2)
        pygame.draw.circle(surf, (32, 32, 32), (cx - 6, cy - 4), 1)
    else:
        pygame.draw.ellipse(surf, body, (cx - 12, cy - 8, 24, 18))
        pygame.draw.ellipse(surf, accent, (cx - 8, cy - 12, 16, 10))
        pygame.draw.circle(surf, (32, 32, 32), (cx - 4, cy - 4), 1)

    if back:
        surf.fill((0, 0, 0, 0), special_flags=pygame.BLEND_RGBA_MULT)


def _draw_battle_bg(surf: pygame.Surface) -> None:
    w, h = surf.get_size()
    for y in range(h):
        t = y / h
        color = (
            int(120 + 40 * t),
            int(176 + 30 * t),
            int(88 + 20 * t),
        )
        pygame.draw.line(surf, color, (0, y), (w, y))
    pygame.draw.ellipse(surf, (96, 152, 72), (0, h // 2, w, h // 2))
    pygame.draw.rect(surf, (144, 192, 112), (0, h - 24, w, 24))


def _expected_tileset_width() -> int:
    count = 0
    for item in TILE_SHEET_ORDER:
        count += item[1] if isinstance(item, tuple) else 1
    return count * TILE_SIZE


class TileAtlas:
    """资源图集：自动检测版本，支持贴图替换。"""

    def __init__(self) -> None:
        self.tile_size = TILE_SIZE
        self.tiles: dict[str, list[pygame.Surface]] = {}
        self.characters: dict[str, list[list[pygame.Surface]]] = {}
        self.battle_sprites: dict[str, pygame.Surface] = {}
        self.battle_bg: pygame.Surface | None = None
        self._anim_frame = 0
        self._load()

    def _needs_regenerate(self) -> bool:
        if not VERSION_PATH.exists():
            return True
        try:
            return int(VERSION_PATH.read_text().strip()) < ASSET_VERSION
        except ValueError:
            return True

    def _mark_version(self) -> None:
        ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        VERSION_PATH.write_text(str(ASSET_VERSION))

    def _load(self) -> None:
        ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        regenerate = self._needs_regenerate()

        if not regenerate and TILESET_PATH.exists():
            sheet = pygame.image.load(str(TILESET_PATH)).convert_alpha()
            if sheet.get_width() >= _expected_tileset_width():
                self._load_tiles_from_sheet(sheet)
            else:
                regenerate = True

        if regenerate or not self.tiles:
            self._build_procedural_tiles()
            self.export_tileset(TILESET_PATH)

        if not regenerate and SPRITES_PATH.exists():
            sheet = pygame.image.load(str(SPRITES_PATH)).convert_alpha()
            expected_w = WALK_FRAMES * 4 * TILE_SIZE
            expected_h = 2 * TILE_SIZE
            if sheet.get_width() >= expected_w and sheet.get_height() >= expected_h:
                self._load_characters_from_sheet(sheet)
            else:
                regenerate = True

        if regenerate or not self.characters:
            self._build_procedural_characters()
            self.export_sprites(SPRITES_PATH)

        if not regenerate and BATTLE_SPRITES_PATH.exists():
            self._load_battle_sprites_from_sheet(BATTLE_SPRITES_PATH)
        else:
            self._build_procedural_battle_sprites()
            self.export_battle_sprites(BATTLE_SPRITES_PATH)

        if not regenerate and BATTLE_BG_PATH.exists():
            self.battle_bg = pygame.image.load(str(BATTLE_BG_PATH)).convert()
        else:
            self.battle_bg = pygame.Surface((240, 112))
            _draw_battle_bg(self.battle_bg)
            pygame.image.save(self.battle_bg, str(BATTLE_BG_PATH))

        self._mark_version()

    def _load_tiles_from_sheet(self, sheet: pygame.Surface) -> None:
        col = 0
        cols = sheet.get_width() // self.tile_size
        for item in TILE_SHEET_ORDER:
            if isinstance(item, tuple):
                key, frame_count = item
                frames = []
                for _ in range(frame_count):
                    c, r = col % cols, col // cols
                    rect = pygame.Rect(c * self.tile_size, r * self.tile_size, self.tile_size, self.tile_size)
                    frames.append(sheet.subsurface(rect).copy())
                    col += 1
                self.tiles[key] = frames
            else:
                c, r = col % cols, col // cols
                rect = pygame.Rect(c * self.tile_size, r * self.tile_size, self.tile_size, self.tile_size)
                self.tiles[item] = [sheet.subsurface(rect).copy()]
                col += 1

    def _build_procedural_tiles(self) -> None:
        builders = {
            TILE_GRASS: _draw_grass_tile,
            TILE_PATH: _draw_path_tile,
            TILE_WALL: _draw_wall_tile,
            TILE_TREE: _draw_tree_tile,
            TILE_HOUSE: _draw_house_tile,
            TILE_FENCE: _draw_fence_tile,
            TILE_CENTER: _draw_center_tile,
            TILE_SHOP: _draw_shop_tile,
        }
        self.tiles = {}
        for key, fn in builders.items():
            s = pygame.Surface((self.tile_size, self.tile_size))
            fn(s)
            self.tiles[key] = [s]
        water = []
        for f in range(3):
            s = pygame.Surface((self.tile_size, self.tile_size))
            _draw_water_tile(s, f)
            water.append(s)
        self.tiles[TILE_WATER] = water

    def _load_characters_from_sheet(self, sheet: pygame.Surface) -> None:
        for row, name in enumerate(["player", "npc"]):
            frames_by_dir: list[list[pygame.Surface]] = []
            for d in range(4):
                walk: list[pygame.Surface] = []
                for f in range(WALK_FRAMES):
                    x = (d * WALK_FRAMES + f) * self.tile_size
                    y = row * self.tile_size
                    rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                    walk.append(sheet.subsurface(rect).copy())
                frames_by_dir.append(walk)
            self.characters[name] = frames_by_dir

    def _build_procedural_characters(self) -> None:
        configs = {
            "player": ((240, 72, 72), (48, 72, 160)),
            "npc": ((64, 160, 240), (56, 56, 96)),
        }
        self.characters = {}
        for name, (body, pants) in configs.items():
            dirs: list[list[pygame.Surface]] = []
            for d in range(4):
                walk = []
                for f in range(WALK_FRAMES):
                    s = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
                    _draw_character(s, body=body, pants=pants, direction=d, frame=f)
                    walk.append(s)
                dirs.append(walk)
            self.characters[name] = dirs

    def _load_battle_sprites_from_sheet(self, path: Path) -> None:
        sheet = pygame.image.load(str(path)).convert_alpha()
        species_ids = list(SPECIES.keys())
        for i, sid in enumerate(species_ids):
            rect = pygame.Rect(i * BATTLE_SPRITE_SIZE, 0, BATTLE_SPRITE_SIZE, BATTLE_SPRITE_SIZE)
            self.battle_sprites[sid] = sheet.subsurface(rect).copy()

    def _build_procedural_battle_sprites(self) -> None:
        self.battle_sprites = {}
        for sid in SPECIES:
            s = pygame.Surface((BATTLE_SPRITE_SIZE, BATTLE_SPRITE_SIZE), pygame.SRCALPHA)
            _draw_battle_pokemon(s, sid)
            self.battle_sprites[sid] = s

    def export_tileset(self, path: Path) -> None:
        width = _expected_tileset_width()
        sheet = pygame.Surface((width, self.tile_size), pygame.SRCALPHA)
        x = 0
        for item in TILE_SHEET_ORDER:
            if isinstance(item, tuple):
                key, _ = item
                for frame in self.tiles[key]:
                    sheet.blit(frame, (x, 0))
                    x += self.tile_size
            else:
                sheet.blit(self.tiles[item][0], (x, 0))
                x += self.tile_size
        pygame.image.save(sheet, str(path))

    def export_sprites(self, path: Path) -> None:
        w = WALK_FRAMES * 4 * self.tile_size
        h = 2 * self.tile_size
        sheet = pygame.Surface((w, h), pygame.SRCALPHA)
        for row, name in enumerate(["player", "npc"]):
            for d in range(4):
                for f in range(WALK_FRAMES):
                    x = (d * WALK_FRAMES + f) * self.tile_size
                    sheet.blit(self.characters[name][d][f], (x, row * self.tile_size))
        pygame.image.save(sheet, str(path))

    def export_battle_sprites(self, path: Path) -> None:
        species_ids = list(SPECIES.keys())
        w = len(species_ids) * BATTLE_SPRITE_SIZE
        sheet = pygame.Surface((w, BATTLE_SPRITE_SIZE), pygame.SRCALPHA)
        for i, sid in enumerate(species_ids):
            sheet.blit(self.battle_sprites[sid], (i * BATTLE_SPRITE_SIZE, 0))
        pygame.image.save(sheet, str(path))

    def tick(self) -> None:
        self._anim_frame += 1

    def get_tile(self, tile_id: str) -> pygame.Surface:
        frames = self.tiles.get(tile_id, self.tiles[TILE_PATH])
        if tile_id == TILE_WATER and len(frames) > 1:
            return frames[(self._anim_frame // 20) % len(frames)]
        return frames[0]

    def get_character_sprite(
        self,
        name: str,
        direction: int = DIR_DOWN,
        walk_frame: int = 0,
    ) -> pygame.Surface:
        char = self.characters.get(name, self.characters["player"])
        d = max(0, min(3, direction))
        f = walk_frame % WALK_FRAMES
        return char[d][f]

    def get_battle_sprite(self, species_id: str) -> pygame.Surface:
        return self.battle_sprites.get(
            species_id,
            self.battle_sprites.get("pikachu", next(iter(self.battle_sprites.values()))),
        )

    def get_battle_background(self) -> pygame.Surface:
        return self.battle_bg or pygame.Surface((240, 112))
