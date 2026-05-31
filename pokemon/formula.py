"""第三世代（GBA）数值公式。"""

import random

from .data import get_type_effectiveness
from .enums import MoveCategory, Stat, Type


def calc_stat(base: int, level: int, iv: int = 15, ev: int = 0) -> int:
    """计算非 HP 能力值。"""
    return (2 * base + iv + ev // 4) * level // 100 + 5


def calc_hp(base: int, level: int, iv: int = 15, ev: int = 0) -> int:
    """计算 HP。"""
    return (2 * base + iv + ev // 4) * level // 100 + level + 10


def calc_damage(
    *,
    level: int,
    power: int,
    attack: int,
    defense: int,
    move_type: Type,
    attacker_types: tuple[Type, ...],
    defender_types: tuple[Type, ...],
    category: MoveCategory,
    randomize: bool = True,
) -> tuple[int, float, bool]:
    """
    第三世代伤害公式（简化版）。
    返回 (伤害, 属性倍率, 是否 STAB)。
    """
    if category == MoveCategory.STATUS or power == 0:
        return 0, 1.0, False

    base = (2 * level // 5 + 2) * power * attack // defense // 50 + 2

    stab = 1.5 if move_type in attacker_types else 1.0
    effectiveness = get_type_effectiveness(move_type, defender_types)
    modifier = stab * effectiveness

    if randomize:
        modifier *= random.uniform(0.85, 1.0)

    damage = max(1, int(base * modifier)) if effectiveness > 0 else 0
    return damage, effectiveness, stab > 1.0


def stat_for_category(stats: dict[str, int], category: MoveCategory) -> tuple[int, int]:
    """根据招式类别返回 (攻击, 防御) 数值。"""
    if category == MoveCategory.SPECIAL:
        return stats[Stat.SPATK.value], stats[Stat.SPDEF.value]
    return stats[Stat.ATK.value], stats[Stat.DEF.value]
