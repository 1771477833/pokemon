"""道具与背包。"""

from dataclasses import dataclass, field

from .pokemon import Pokemon


@dataclass(frozen=True)
class ItemTemplate:
    id: str
    name: str
    price: int
    description: str
    kind: str  # heal | ball


ITEMS: dict[str, ItemTemplate] = {
    "potion": ItemTemplate("potion", "伤药", 200, "恢复 20 HP", "heal"),
    "super_potion": ItemTemplate("super_potion", "好伤药", 500, "恢复 50 HP", "heal"),
    "pokeball": ItemTemplate("pokeball", "精灵球", 200, "捕捉野生精灵", "ball"),
}

SHOP_STOCK: list[str] = ["potion", "super_potion", "pokeball"]

HEAL_VALUES: dict[str, int] = {
    "potion": 20,
    "super_potion": 50,
}


@dataclass
class Bag:
    items: dict[str, int] = field(default_factory=dict)

    def count(self, item_id: str) -> int:
        return self.items.get(item_id, 0)

    def add(self, item_id: str, amount: int = 1) -> None:
        self.items[item_id] = self.count(item_id) + amount

    def remove(self, item_id: str, amount: int = 1) -> bool:
        current = self.count(item_id)
        if current < amount:
            return False
        remaining = current - amount
        if remaining == 0:
            self.items.pop(item_id, None)
        else:
            self.items[item_id] = remaining
        return True

    def usable_in_battle(self) -> list[str]:
        return [iid for iid, cnt in self.items.items() if cnt > 0 and iid in ITEMS]

    def use_heal(self, item_id: str, pokemon: Pokemon) -> str:
        if item_id not in HEAL_VALUES:
            return "无法使用该道具。"
        if not self.remove(item_id):
            return "道具不足。"
        if pokemon.is_fainted:
            return f"{pokemon.name} 已经倒下了！"
        amount = HEAL_VALUES[item_id]
        before = pokemon.current_hp
        pokemon.current_hp = min(pokemon.max_hp, pokemon.current_hp + amount)
        healed = pokemon.current_hp - before
        name = ITEMS[item_id].name
        return f"使用了 {name}！{pokemon.name} 恢复了 {healed} HP！"
