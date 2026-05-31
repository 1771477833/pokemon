"""训练家。"""

from dataclasses import dataclass, field

from .items import Bag
from .party import Party
from .pokemon import Pokemon


@dataclass
class Trainer:
    name: str
    party: Party
    is_player: bool = False
    money: int = 3000
    bag: Bag = field(default_factory=Bag)

    @classmethod
    def player(cls, name: str = "小智") -> "Trainer":
        party = Party()
        party.add(Pokemon.create("pikachu", 5))
        party.add(Pokemon.create("charmander", 5))
        trainer = cls(name=name, party=party, is_player=True, money=3000)
        trainer.bag.add("potion", 2)
        return trainer

    @classmethod
    def wild(cls, pokemon: Pokemon) -> "Trainer":
        party = Party()
        party.add(pokemon)
        return cls(name="野生宝可梦", party=party)

    @classmethod
    def npc(cls, name: str, species_ids: list[tuple[str, int]]) -> "Trainer":
        party = Party()
        for sid, level in species_ids:
            party.add(Pokemon.create(sid, level))
        return cls(name=name, party=party)

    def active_pokemon(self) -> Pokemon | None:
        return self.party.first_alive()
