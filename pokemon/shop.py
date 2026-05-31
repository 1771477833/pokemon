"""商店逻辑。"""

from .items import ITEMS, SHOP_STOCK
from .trainer import Trainer


def buy_item(player: Trainer, item_id: str) -> str:
    template = ITEMS.get(item_id)
    if not template:
        return "没有这个商品。"
    if player.money < template.price:
        return "金钱不足！"
    player.money -= template.price
    player.bag.add(item_id)
    return f"购买了 {template.name}！（剩余 ${player.money}）"
