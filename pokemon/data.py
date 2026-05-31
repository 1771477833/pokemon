"""物种、招式等静态数据。"""

from dataclasses import dataclass

from .enums import MoveCategory, Type


@dataclass(frozen=True)
class MoveTemplate:
    id: str
    name: str
    move_type: Type
    category: MoveCategory
    power: int
    accuracy: int
    pp: int


@dataclass(frozen=True)
class SpeciesTemplate:
    id: str
    name: str
    types: tuple[Type, ...]
    base_hp: int
    base_atk: int
    base_def: int
    base_spatk: int
    base_spdef: int
    base_spd: int
    learnset: tuple[str, ...]


MOVES: dict[str, MoveTemplate] = {
    "tackle": MoveTemplate("tackle", "撞击", Type.NORMAL, MoveCategory.PHYSICAL, 40, 100, 35),
    "scratch": MoveTemplate("scratch", "抓", Type.NORMAL, MoveCategory.PHYSICAL, 40, 100, 35),
    "ember": MoveTemplate("ember", "火花", Type.FIRE, MoveCategory.SPECIAL, 40, 100, 25),
    "water_gun": MoveTemplate("water_gun", "水枪", Type.WATER, MoveCategory.SPECIAL, 40, 100, 25),
    "vine_whip": MoveTemplate("vine_whip", "藤鞭", Type.GRASS, MoveCategory.PHYSICAL, 45, 100, 25),
    "thunder_shock": MoveTemplate("thunder_shock", "电击", Type.ELECTRIC, MoveCategory.SPECIAL, 40, 100, 30),
    "quick_attack": MoveTemplate("quick_attack", "电光一闪", Type.NORMAL, MoveCategory.PHYSICAL, 40, 100, 30),
    "bite": MoveTemplate("bite", "咬住", Type.DARK, MoveCategory.PHYSICAL, 60, 100, 25),
    "growl": MoveTemplate("growl", "叫声", Type.NORMAL, MoveCategory.STATUS, 0, 100, 40),
}

SPECIES: dict[str, SpeciesTemplate] = {
    "bulbasaur": SpeciesTemplate(
        "bulbasaur", "妙蛙种子", (Type.GRASS, Type.POISON),
        45, 49, 49, 65, 65, 45,
        ("tackle", "vine_whip", "growl"),
    ),
    "charmander": SpeciesTemplate(
        "charmander", "小火龙", (Type.FIRE,),
        39, 52, 43, 60, 50, 65,
        ("scratch", "ember", "growl"),
    ),
    "squirtle": SpeciesTemplate(
        "squirtle", "杰尼龟", (Type.WATER,),
        44, 48, 65, 50, 64, 43,
        ("tackle", "water_gun", "growl"),
    ),
    "pikachu": SpeciesTemplate(
        "pikachu", "皮卡丘", (Type.ELECTRIC,),
        35, 55, 40, 50, 50, 90,
        ("quick_attack", "thunder_shock", "growl"),
    ),
    "rattata": SpeciesTemplate(
        "rattata", "小拉达", (Type.NORMAL,),
        30, 56, 35, 25, 35, 72,
        ("tackle", "quick_attack", "bite"),
    ),
    "pidgey": SpeciesTemplate(
        "pidgey", "波波", (Type.NORMAL, Type.FLYING),
        40, 45, 40, 35, 35, 56,
        ("tackle", "quick_attack", "growl"),
    ),
}

# 属性克制表: attacker -> defender -> 倍率
TYPE_CHART: dict[Type, dict[Type, float]] = {
    Type.NORMAL: {Type.ROCK: 0.5, Type.GHOST: 0.0, Type.STEEL: 0.5},
    Type.FIRE: {
        Type.FIRE: 0.5, Type.WATER: 0.5, Type.GRASS: 2.0, Type.ICE: 2.0,
        Type.BUG: 2.0, Type.ROCK: 0.5, Type.DRAGON: 0.5, Type.STEEL: 2.0,
    },
    Type.WATER: {
        Type.FIRE: 2.0, Type.WATER: 0.5, Type.GRASS: 0.5, Type.GROUND: 2.0,
        Type.ROCK: 2.0, Type.DRAGON: 0.5,
    },
    Type.GRASS: {
        Type.FIRE: 0.5, Type.WATER: 2.0, Type.GRASS: 0.5, Type.POISON: 0.5,
        Type.GROUND: 2.0, Type.FLYING: 0.5, Type.BUG: 0.5, Type.ROCK: 2.0,
        Type.DRAGON: 0.5, Type.STEEL: 0.5,
    },
    Type.ELECTRIC: {
        Type.WATER: 2.0, Type.GRASS: 0.5, Type.ELECTRIC: 0.5, Type.GROUND: 0.0,
        Type.FLYING: 2.0, Type.DRAGON: 0.5,
    },
    Type.POISON: {
        Type.GRASS: 2.0, Type.POISON: 0.5, Type.GROUND: 0.5, Type.ROCK: 0.5,
        Type.GHOST: 0.5, Type.STEEL: 0.0,
    },
    Type.GROUND: {
        Type.FIRE: 2.0, Type.ELECTRIC: 2.0, Type.GRASS: 0.5, Type.POISON: 2.0,
        Type.FLYING: 0.0, Type.BUG: 0.5, Type.ROCK: 2.0, Type.STEEL: 2.0,
    },
    Type.FLYING: {
        Type.GRASS: 2.0, Type.ELECTRIC: 0.5, Type.FIGHTING: 2.0, Type.BUG: 2.0,
        Type.ROCK: 0.5, Type.STEEL: 0.5,
    },
    Type.PSYCHIC: {Type.FIGHTING: 2.0, Type.POISON: 2.0, Type.PSYCHIC: 0.5, Type.DARK: 0.0, Type.STEEL: 0.5},
    Type.BUG: {
        Type.FIRE: 0.5, Type.GRASS: 2.0, Type.FIGHTING: 0.5, Type.POISON: 0.5,
        Type.FLYING: 0.5, Type.PSYCHIC: 2.0, Type.GHOST: 0.5, Type.DARK: 2.0,
        Type.STEEL: 0.5,
    },
    Type.ROCK: {
        Type.FIRE: 2.0, Type.ICE: 2.0, Type.FIGHTING: 0.5, Type.GROUND: 0.5,
        Type.FLYING: 2.0, Type.BUG: 2.0, Type.STEEL: 0.5,
    },
    Type.GHOST: {Type.NORMAL: 0.0, Type.PSYCHIC: 2.0, Type.GHOST: 2.0, Type.DARK: 0.5},
    Type.DRAGON: {Type.DRAGON: 2.0, Type.STEEL: 0.5},
    Type.DARK: {Type.FIGHTING: 0.5, Type.PSYCHIC: 2.0, Type.GHOST: 2.0, Type.DARK: 0.5, Type.STEEL: 0.5},
    Type.STEEL: {
        Type.FIRE: 0.5, Type.WATER: 0.5, Type.ELECTRIC: 0.5, Type.ICE: 2.0,
        Type.ROCK: 2.0, Type.STEEL: 0.5,
    },
    Type.ICE: {
        Type.FIRE: 0.5, Type.WATER: 0.5, Type.GRASS: 2.0, Type.ICE: 0.5,
        Type.GROUND: 2.0, Type.FLYING: 2.0, Type.DRAGON: 2.0, Type.STEEL: 0.5,
    },
    Type.FIGHTING: {
        Type.NORMAL: 2.0, Type.ICE: 2.0, Type.POISON: 0.5, Type.FLYING: 0.5,
        Type.PSYCHIC: 0.5, Type.BUG: 0.5, Type.ROCK: 2.0, Type.GHOST: 0.0,
        Type.DARK: 2.0, Type.STEEL: 2.0,
    },
}


def get_type_effectiveness(move_type: Type, defender_types: tuple[Type, ...]) -> float:
    """计算招式对防御方属性的总倍率。"""
    multiplier = 1.0
    for def_type in defender_types:
        multiplier *= TYPE_CHART.get(move_type, {}).get(def_type, 1.0)
    return multiplier
