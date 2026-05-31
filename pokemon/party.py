"""队伍管理。"""

from dataclasses import dataclass, field

from .pokemon import Pokemon


@dataclass
class Party:
    members: list[Pokemon] = field(default_factory=list)
    max_size: int = 6

    def add(self, pokemon: Pokemon) -> bool:
        if len(self.members) >= self.max_size:
            return False
        self.members.append(pokemon)
        return True

    def first_alive(self) -> Pokemon | None:
        for p in self.members:
            if not p.is_fainted:
                return p
        return None

    def all_fainted(self) -> bool:
        return all(p.is_fainted for p in self.members)

    def heal_all(self) -> None:
        for p in self.members:
            p.heal()
