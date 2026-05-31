"""纯文本模式演示（无需图形界面）。"""

from pokemon.battle import Battle, BattleAction
from pokemon.pokemon import Pokemon
from pokemon.trainer import Trainer


def demo_battle() -> None:
    player = Trainer.player()
    wild = Trainer.wild(Pokemon.wild("rattata", (4, 4)))
    battle = Battle(player=player, enemy=wild, is_wild=True)
    battle.start()

    print("=== 文本战斗演示 ===")
    for line in battle.log:
        print(line)

    while not battle.finished:
        poke = battle.player_active
        if not poke:
            break
        print(f"\n{poke.name} HP: {poke.current_hp}/{poke.max_hp}")
        for i, move in enumerate(poke.moves):
            print(f"  [{i}] {move.name} (PP {move.current_pp}/{move.template.pp})")

        choice = 0
        battle.player_choose(BattleAction(kind="move", move_index=choice))

        for line in battle.log[-6:]:
            print(line)

    print("\n战斗结束！")


if __name__ == "__main__":
    demo_battle()
