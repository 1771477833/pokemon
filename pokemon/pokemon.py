"""宝可梦实例。"""

import random
from dataclasses import dataclass, field

from .data import SPECIES, SpeciesTemplate
from .enums import Stat, Type
from .formula import calc_hp, calc_stat
from .move import Move


@dataclass
class Pokemon:
    species: SpeciesTemplate
    level: int
    current_hp: int = 0
    moves: list[Move] = field(default_factory=list)
    nickname: str | None = None
    experience: int = 0

    def __post_init__(self) -> None:
        if not self.moves:
            self.moves = [Move.from_id(mid) for mid in self.species.learnset]
        if self.current_hp <= 0:
            self.current_hp = self.max_hp

    @classmethod
    def create(cls, species_id: str, level: int) -> "Pokemon":
        return cls(species=SPECIES[species_id], level=level)

    @classmethod
    def wild(cls, species_id: str, level_range: tuple[int, int] = (3, 5)) -> "Pokemon":
        level = random.randint(*level_range)
        return cls.create(species_id, level)

    @property
    def name(self) -> str:
        return self.nickname or self.species.name

    @property
    def types(self) -> tuple[Type, ...]:
        return self.species.types

    @property
    def stats(self) -> dict[str, int]:
        s = self.species
        return {
            Stat.HP.value: calc_hp(s.base_hp, self.level),
            Stat.ATK.value: calc_stat(s.base_atk, self.level),
            Stat.DEF.value: calc_stat(s.base_def, self.level),
            Stat.SPATK.value: calc_stat(s.base_spatk, self.level),
            Stat.SPDEF.value: calc_stat(s.base_spdef, self.level),
            Stat.SPD.value: calc_stat(s.base_spd, self.level),
        }

    @property
    def max_hp(self) -> int:
        return self.stats[Stat.HP.value]

    @property
    def speed(self) -> int:
        return self.stats[Stat.SPD.value]

    @property
    def is_fainted(self) -> bool:
        return self.current_hp <= 0

    def heal(self) -> None:
        self.current_hp = self.max_hp
        for move in self.moves:
            move.current_pp = move.template.pp

    def take_damage(self, amount: int) -> int:
        actual = min(self.current_hp, max(0, amount))
        self.current_hp -= actual
        return actual

    def gain_exp(self, amount: int) -> list[str]:
        """获得经验，升级时返回消息列表。"""
        messages: list[str] = []
        self.experience += amount
        while self.level < 100 and self.experience >= self.exp_to_next_level():
            self.experience -= self.exp_to_next_level()
            self.level += 1
            old_max = self.max_hp
            self.current_hp += self.max_hp - old_max
            messages.append(f"{self.name} 升到了 Lv.{self.level}！")
        return messages

    def exp_to_next_level(self) -> int:
        """中等慢速成长曲线（Gen3 常见）。"""
        return self.level ** 3

    def exp_yield(self) -> int:
        """被击败时给予的经验值（简化）。"""
        return self.level * 10
