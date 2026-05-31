"""游戏枚举定义。"""

from enum import Enum, auto


class Type(Enum):
    NORMAL = "一般"
    FIRE = "火"
    WATER = "水"
    GRASS = "草"
    ELECTRIC = "电"
    POISON = "毒"
    GROUND = "地面"
    FLYING = "飞行"
    PSYCHIC = "超能"
    BUG = "虫"
    ROCK = "岩石"
    GHOST = "幽灵"
    DRAGON = "龙"
    DARK = "恶"
    STEEL = "钢"
    ICE = "冰"
    FIGHTING = "格斗"


class Stat(Enum):
    HP = "hp"
    ATK = "attack"
    DEF = "defense"
    SPATK = "sp_attack"
    SPDEF = "sp_defense"
    SPD = "speed"


class MoveCategory(Enum):
    PHYSICAL = auto()
    SPECIAL = auto()
    STATUS = auto()


class GameState(Enum):
    TITLE = auto()
    OVERWORLD = auto()
    DIALOGUE = auto()
    BATTLE = auto()
    SHOP = auto()
    MENU = auto()
    SAVE_MENU = auto()


class BattlePhase(Enum):
    INTRO = auto()
    PLAYER_TURN = auto()
    ENEMY_TURN = auto()
    RESOLVE = auto()
    END = auto()
