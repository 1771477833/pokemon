"""招式实例。"""

from dataclasses import dataclass

from .data import MOVES, MoveTemplate
from .enums import MoveCategory, Type


@dataclass
class Move:
    template: MoveTemplate
    current_pp: int

    @classmethod
    def from_id(cls, move_id: str) -> "Move":
        template = MOVES[move_id]
        return cls(template=template, current_pp=template.pp)

    @property
    def id(self) -> str:
        return self.template.id

    @property
    def name(self) -> str:
        return self.template.name

    @property
    def move_type(self) -> Type:
        return self.template.move_type

    @property
    def category(self) -> MoveCategory:
        return self.template.category

    @property
    def power(self) -> int:
        return self.template.power

    @property
    def accuracy(self) -> int:
        return self.template.accuracy

    def use(self) -> bool:
        """消耗 PP，成功返回 True。"""
        if self.current_pp <= 0:
            return False
        self.current_pp -= 1
        return True
