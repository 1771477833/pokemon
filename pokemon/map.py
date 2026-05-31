"""地图与遇敌。"""

import random
from dataclasses import dataclass, field

from .pokemon import Pokemon

# 基础地形
TILE_GRASS = "G"
TILE_PATH = "."
TILE_WALL = "#"
TILE_WATER = "W"
# 装饰/障碍
TILE_TREE = "T"
TILE_HOUSE = "H"
TILE_FENCE = "F"
TILE_CENTER = "C"
TILE_SHOP = "S"

# 不可行走的瓦片
BLOCKED_TILES = frozenset({
    TILE_WALL, TILE_WATER, TILE_TREE, TILE_HOUSE, TILE_FENCE,
    TILE_CENTER, TILE_SHOP,
})

DEFAULT_MAP = [
    "TTTTTTTTTTTTTTTTTTTT",
    "T.C....G.G.G....S.HT",
    "T..G..G...G..G..G..T",
    "T......G.G.G......FT",
    "T..FFFF....FFFF....T",
    "T..F..G.G.G..F..G..T",
    "T..F..G.G.G..F..G..T",
    "T..FFFF....FFFF....T",
    "T......G.G.G......WT",
    "T..G..G...G..G..G..T",
    "T......G.G.G......FT",
    "TTTTTTTTTTTTTTTTTTTT",
]


@dataclass
class MapEntity:
    x: int
    y: int
    kind: str
    data: dict = field(default_factory=dict)


@dataclass
class WorldMap:
    tiles: list[list[str]]
    width: int = 0
    height: int = 0
    player_x: int = 1
    player_y: int = 1
    entities: list[MapEntity] = field(default_factory=list)
    grass_encounters: list[tuple[str, int]] = field(default_factory=list)
    encounter_rate: float = 0.15

    def __post_init__(self) -> None:
        if isinstance(self.tiles[0], str):
            self.tiles = [list(row) for row in self.tiles]
        self.height = len(self.tiles)
        self.width = max(len(row) for row in self.tiles) if self.height else 0
        self.tiles = [
            row + [TILE_WALL] * (self.width - len(row))
            for row in self.tiles
        ]
        if not self.grass_encounters:
            self.grass_encounters = [("rattata", 5), ("pidgey", 5)]

    @classmethod
    def from_strings(cls, rows: list[str], **kwargs) -> "WorldMap":
        return cls(tiles=rows, **kwargs)

    def is_walkable(self, x: int, y: int) -> bool:
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return False
        return self.tiles[y][x] not in BLOCKED_TILES

    def tile_at(self, x: int, y: int) -> str:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return TILE_WALL

    def move_player(self, dx: int, dy: int) -> tuple[bool, bool]:
        nx, ny = self.player_x + dx, self.player_y + dy
        if not self.is_walkable(nx, ny):
            return False, False

        self.player_x, self.player_y = nx, ny
        triggered = self.tile_at(nx, ny) == TILE_GRASS and random.random() < self.encounter_rate
        return True, triggered

    def spawn_wild_pokemon(self) -> Pokemon:
        species_id, weight = random.choices(
            self.grass_encounters,
            weights=[w for _, w in self.grass_encounters],
        )[0]
        return Pokemon.wild(species_id, (3, 6))

    def npc_at(self, x: int, y: int) -> MapEntity | None:
        for entity in self.entities:
            if entity.kind in ("npc", "building") and entity.x == x and entity.y == y:
                return entity
        return None

    def interactable_at(self, px: int, py: int) -> MapEntity | None:
        """玩家面前或脚下的可交互对象。"""
        for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
            entity = self.npc_at(px + dx, py + dy)
            if entity:
                return entity
        return None
