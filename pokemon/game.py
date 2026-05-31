"""游戏主循环与状态机。"""

from dataclasses import dataclass, field

import pygame

from .battle import Battle, BattleAction
from .controls import (
    KEY_CANCEL,
    KEY_CONFIRM,
    KEY_MENU,
    MOVE_COOLDOWN_FRAMES,
    is_cancel,
    is_confirm,
    is_start,
    movement_from_key,
    read_movement,
)
from .dialogue import DialogueSession
from .enums import GameState
from .items import ITEMS, SHOP_STOCK
from .map import DEFAULT_MAP, MapEntity, WorldMap
from .render import Renderer
from .shop import buy_item
from .save import load_game, save_game
from .tileset import DIR_DOWN, DIR_LEFT, DIR_RIGHT, DIR_UP
from .trainer import Trainer


def _battle_menu_move(index: int, dy: int, dx: int) -> int:
    row, col = index // 2, index % 2
    row = max(0, min(1, row + dy))
    col = max(0, min(1, col + dx))
    return row * 2 + col


@dataclass
class Game:
    renderer: Renderer = field(default_factory=Renderer)
    state: GameState = GameState.TITLE
    player: Trainer = field(default_factory=Trainer.player)
    world: WorldMap = field(default_factory=lambda: Game._create_world())
    battle: Battle | None = None
    dialogue: DialogueSession | None = None
    title_blink: int = 0
    title_menu_index: int = 0
    battle_menu_index: int = 0
    battle_move_index: int = 0
    in_move_menu: bool = False
    in_party_menu: bool = False
    in_bag_menu: bool = False
    party_menu_index: int = 0
    bag_menu_index: int = 0
    shop_menu_index: int = 0
    pause_menu_index: int = 0
    save_menu_index: int = 0
    save_slot: int = 1
    player_direction: int = DIR_DOWN
    player_walk_frame: int = 0
    move_cooldown: int = 0
    defeated_trainers: set[tuple[int, int]] = field(default_factory=set)
    pending_trainer_pos: tuple[int, int] | None = None
    running: bool = True

    @staticmethod
    def _create_world() -> WorldMap:
        world = WorldMap.from_strings(DEFAULT_MAP)
        world.entities = [
            MapEntity(2, 1, "building", {"role": "center", "name": "精灵中心"}),
            MapEntity(16, 1, "building", {"role": "shop", "name": "友好商店"}),
            MapEntity(5, 3, "npc", {
                "name": "老人",
                "direction": DIR_DOWN,
                "dialogue": [
                    "前面的草丛里有野生精灵！",
                    "记得准备好你的队伍。",
                ],
            }),
            MapEntity(10, 5, "npc", {
                "name": "小茂",
                "direction": DIR_LEFT,
                "dialogue": [
                    "我是小茂，你的劲敌！",
                    "让我看看你的精灵训练得怎么样了！",
                    "来对战吧！",
                ],
                "team": [("squirtle", 6)],
                "battle_after_dialogue": True,
            }),
        ]
        world.player_x = 2
        world.player_y = 3
        return world

    def run(self) -> None:
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.renderer.tick()
        pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type != pygame.KEYDOWN:
                continue

            if self.state == GameState.TITLE:
                self._handle_title_key(event.key)
            elif self.state == GameState.OVERWORLD:
                self._handle_overworld_key(event.key)
            elif self.state == GameState.DIALOGUE:
                self._handle_dialogue_key(event.key)
            elif self.state == GameState.BATTLE:
                self._handle_battle_key(event.key)
            elif self.state == GameState.SHOP:
                self._handle_shop_key(event.key)
            elif self.state == GameState.MENU:
                self._handle_menu_key(event.key)
            elif self.state == GameState.SAVE_MENU:
                self._handle_save_menu_key(event.key)

    def _handle_title_key(self, key: int) -> None:
        from .save import has_save

        has_saves = has_save(1) or has_save(2) or has_save(3)
        move = movement_from_key(key)

        if move is not None:
            _, dy = move
            max_options = 1 if not has_saves else 2
            if dy == -1:
                self.title_menu_index = max(0, self.title_menu_index - 1)
            elif dy == 1:
                self.title_menu_index = min(max_options, self.title_menu_index + 1)
        elif is_confirm(key):
            if has_saves and self.title_menu_index == 0:
                self.state = GameState.SAVE_MENU
                self.pause_menu_index = 3
                self.save_menu_index = 0
                self.save_slot = 1
            else:
                self.state = GameState.OVERWORLD

    def _handle_overworld_key(self, key: int) -> None:
        if key == KEY_MENU:
            self.state = GameState.MENU
            self.pause_menu_index = 0
            return
        if is_confirm(key):
            self._try_interact()

    def _update_overworld_movement(self) -> None:
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return

        delta = read_movement(pygame.key.get_pressed())
        if delta is None:
            return

        dx, dy = delta
        if dy == -1:
            self.player_direction = DIR_UP
        elif dy == 1:
            self.player_direction = DIR_DOWN
        elif dx == -1:
            self.player_direction = DIR_LEFT
        elif dx == 1:
            self.player_direction = DIR_RIGHT

        moved, encounter = self.world.move_player(dx, dy)
        if moved:
            self.player_walk_frame = (self.player_walk_frame + 1) % 2
            self.move_cooldown = MOVE_COOLDOWN_FRAMES
        if encounter:
            self._start_wild_battle()
        elif moved:
            self._try_interact(auto_only=True)

    def _start_dialogue(self, session: DialogueSession) -> None:
        self.dialogue = session
        self.state = GameState.DIALOGUE

    def _end_dialogue(self) -> None:
        session = self.dialogue
        callback = session.consume_callback() if session else None
        self.dialogue = None
        self.state = GameState.OVERWORLD
        if callback:
            callback()

    def _handle_dialogue_key(self, key: int) -> None:
        if not self.dialogue:
            self.state = GameState.OVERWORLD
            return
        if is_confirm(key):
            if not self.dialogue.advance():
                self._end_dialogue()
        elif is_cancel(key):
            self.dialogue.skip_all()
            self._end_dialogue()

    def _try_interact(self, auto_only: bool = False) -> None:
        entity = self.world.interactable_at(self.world.player_x, self.world.player_y)
        if not entity:
            return
        if auto_only and not entity.data.get("auto_talk"):
            return

        role = entity.data.get("role")
        if entity.kind == "building":
            if role == "center":
                self._interact_pokemon_center()
            elif role == "shop":
                self._interact_shop_intro()
            return

        if entity.kind == "npc":
            self._interact_npc(entity)

    def _interact_pokemon_center(self) -> None:
        def heal() -> None:
            self.player.party.heal_all()
            self._start_dialogue(DialogueSession.from_npc("乔伊小姐", [
                "……好了！",
                "你的精灵已经恢复健康了！",
                "祝你好运！",
            ]))

        self._start_dialogue(DialogueSession.from_npc("乔伊小姐", [
            "欢迎来到精灵中心！",
            "我们可以恢复你的精灵。",
            "要恢复吗？",
        ], on_finish=heal))

    def _interact_shop_intro(self) -> None:
        def open_shop() -> None:
            self.state = GameState.SHOP
            self.shop_menu_index = 0

        self._start_dialogue(DialogueSession.from_npc("店员", [
            "欢迎光临友好商店！",
            "这里有伤药、好伤药和精灵球。",
            "需要什么？",
        ], on_finish=open_shop))

    def _interact_npc(self, entity: MapEntity) -> None:
        name = entity.data.get("name", "训练家")
        lines = entity.data.get("dialogue", [])
        team = entity.data.get("team", [])
        pos = (entity.x, entity.y)

        if team and pos in self.defeated_trainers:
            self._start_dialogue(DialogueSession.from_npc(name, [
                "你已经打败我了。",
                "继续去变强吧！",
            ]))
            return

        def on_battle() -> None:
            if team:
                self._start_trainer_battle(name, team, trainer_pos=pos)

        if lines and entity.data.get("battle_after_dialogue") and team:
            self._start_dialogue(DialogueSession.from_npc(name, lines, on_finish=on_battle))
        elif lines:
            self._start_dialogue(DialogueSession.from_npc(name, lines))
        elif team:
            self._start_trainer_battle(name, team, trainer_pos=pos)
        else:
            self._start_dialogue(DialogueSession.from_npc(name, ["你好，训练家！"]))

    def _start_wild_battle(self) -> None:
        wild = self.world.spawn_wild_pokemon()
        self.battle = Battle(player=self.player, enemy=Trainer.wild(wild), is_wild=True)
        self.battle.start()
        self.state = GameState.BATTLE
        self._reset_battle_ui()

    def _start_trainer_battle(
        self,
        name: str,
        team: list[tuple[str, int]],
        *,
        trainer_pos: tuple[int, int] | None = None,
    ) -> None:
        self.battle = Battle(player=self.player, enemy=Trainer.npc(name, team), is_wild=False)
        self.battle.start()
        self.state = GameState.BATTLE
        self._reset_battle_ui()
        self.pending_trainer_pos = trainer_pos

    def _reset_battle_ui(self) -> None:
        self.battle_menu_index = 0
        self.battle_move_index = 0
        self.in_move_menu = False
        self.in_party_menu = False
        self.in_bag_menu = False
        self.party_menu_index = 0
        self.bag_menu_index = 0
        self.pending_trainer_pos = None

    def _handle_battle_key(self, key: int) -> None:
        if not self.battle:
            return

        if self.battle.finished:
            if is_confirm(key):
                if self.battle.player_won and self.pending_trainer_pos:
                    self.defeated_trainers.add(self.pending_trainer_pos)
                    self.player.money += 500
                if not self.battle.player_won and self.player.party.all_fainted():
                    self.player.party.heal_all()
                    self._start_dialogue(DialogueSession.from_npc("系统", ["你的精灵倒下了……已紧急恢复。"]))
                self.battle = None
                self.pending_trainer_pos = None
                if self.state == GameState.BATTLE:
                    self.state = GameState.OVERWORLD
            return

        if self.in_move_menu:
            self._handle_move_menu_key(key)
            return
        if self.in_party_menu:
            self._handle_party_menu_key(key)
            return
        if self.in_bag_menu:
            self._handle_bag_menu_key(key)
            return

        move = movement_from_key(key)
        if move is not None:
            dx, dy = move
            if dy == -1:
                self.battle_menu_index = _battle_menu_move(self.battle_menu_index, -1, 0)
            elif dy == 1:
                self.battle_menu_index = _battle_menu_move(self.battle_menu_index, 1, 0)
            elif dx == -1:
                self.battle_menu_index = _battle_menu_move(self.battle_menu_index, 0, -1)
            elif dx == 1:
                self.battle_menu_index = _battle_menu_move(self.battle_menu_index, 0, 1)
        elif is_confirm(key):
            self._confirm_battle_menu()

    def _handle_move_menu_key(self, key: int) -> None:
        moves = self.battle.player_active.moves if self.battle and self.battle.player_active else []
        move = movement_from_key(key)
        if move is not None:
            _, dy = move
            if dy == -1:
                self.battle_move_index = max(0, self.battle_move_index - 1)
            elif dy == 1:
                self.battle_move_index = min(max(0, len(moves) - 1), self.battle_move_index + 1)
        elif is_confirm(key) and moves:
            self.battle.player_choose(BattleAction(kind="move", move_index=self.battle_move_index))
            self.in_move_menu = False
        elif is_cancel(key):
            self.in_move_menu = False

    def _handle_party_menu_key(self, key: int) -> None:
        members = self.player.party.members
        move = movement_from_key(key)
        if move is not None:
            _, dy = move
            if dy == -1:
                self.party_menu_index = max(0, self.party_menu_index - 1)
            elif dy == 1:
                self.party_menu_index = min(max(0, len(members) - 1), self.party_menu_index + 1)
        elif is_confirm(key):
            self.battle.player_choose(BattleAction(kind="switch", switch_index=self.party_menu_index))
            self.in_party_menu = False
        elif is_cancel(key):
            self.in_party_menu = False

    def _handle_bag_menu_key(self, key: int) -> None:
        items = self.player.bag.usable_in_battle()
        move = movement_from_key(key)
        if move is not None:
            _, dy = move
            if dy == -1:
                self.bag_menu_index = max(0, self.bag_menu_index - 1)
            elif dy == 1:
                self.bag_menu_index = min(max(0, len(items) - 1), self.bag_menu_index + 1)
        elif is_confirm(key) and items:
            item_id = items[self.bag_menu_index]
            self.battle.player_choose(BattleAction(kind="item", item_id=item_id))
            self.in_bag_menu = False
        elif is_cancel(key):
            self.in_bag_menu = False

    def _confirm_battle_menu(self) -> None:
        if not self.battle:
            return

        idx = self.battle_menu_index
        if idx == 0:
            self.in_move_menu = True
            self.battle_move_index = 0
        elif idx == 1:
            items = self.player.bag.usable_in_battle()
            if items:
                self.in_bag_menu = True
                self.bag_menu_index = 0
            else:
                self.battle.log.append("背包里没有道具！")
        elif idx == 2:
            self.in_party_menu = True
            self.party_menu_index = 0
        elif idx == 3:
            if self.battle.is_wild:
                self.battle.player_choose(BattleAction(kind="run"))
            else:
                self.battle.log.append("不能逃跑！")

    def _handle_shop_key(self, key: int) -> None:
        move = movement_from_key(key)
        if move is not None:
            _, dy = move
            if dy == -1:
                self.shop_menu_index = max(0, self.shop_menu_index - 1)
            elif dy == 1:
                self.shop_menu_index = min(len(SHOP_STOCK), self.shop_menu_index + 1)
        elif is_confirm(key):
            if self.shop_menu_index < len(SHOP_STOCK):
                item_id = SHOP_STOCK[self.shop_menu_index]
                msg = buy_item(self.player, item_id)
                self._start_dialogue(DialogueSession.from_npc("店员", [msg]))
            else:
                self.state = GameState.OVERWORLD
        elif is_cancel(key):
            self.state = GameState.OVERWORLD

    def _handle_menu_key(self, key: int) -> None:
        from .save import has_save
        move = movement_from_key(key)
        if move is not None:
            _, dy = move
            if dy == -1:
                self.pause_menu_index = max(0, self.pause_menu_index - 1)
            elif dy == 1:
                self.pause_menu_index = min(4, self.pause_menu_index + 1)
        elif is_confirm(key):
            if self.pause_menu_index == 0:
                self._start_dialogue(DialogueSession.from_npc("系统", ["队伍状态请查看下方列表。"]))
            elif self.pause_menu_index == 1:
                self.player.party.heal_all()
                self._start_dialogue(DialogueSession.from_npc("系统", ["宝可梦全部恢复了！"]))
            elif self.pause_menu_index == 2:
                self.state = GameState.SAVE_MENU
                self.save_menu_index = 0
                self.save_slot = 1
            elif self.pause_menu_index == 3:
                if has_save(1) or has_save(2) or has_save(3):
                    self.state = GameState.SAVE_MENU
                    self.save_menu_index = 0
                    self.save_slot = 1
                else:
                    self._start_dialogue(DialogueSession.from_npc("系统", ["没有找到存档文件。"]))
            else:
                self.state = GameState.OVERWORLD
        elif is_cancel(key):
            self.state = GameState.OVERWORLD

    def _handle_save_menu_key(self, key: int) -> None:
        from .save import has_save, load_game, save_game

        in_load_mode = self.pause_menu_index == 3
        move = movement_from_key(key)
        if move is not None:
            _, dy = move
            if dy == -1:
                self.save_menu_index = max(0, self.save_menu_index - 1)
            elif dy == 1:
                self.save_menu_index = min(2, self.save_menu_index + 1)
            self.save_slot = self.save_menu_index + 1
        elif is_confirm(key):
            slot = self.save_slot
            if in_load_mode:
                loaded = load_game(slot)
                if loaded:
                    self.player = loaded.player
                    self.world = loaded.world
                    self.defeated_trainers = loaded.defeated_trainers
                    self.state = GameState.OVERWORLD
                    self._start_dialogue(DialogueSession.from_npc("系统", [f"读取了存档 {slot}！"]))
                else:
                    self._start_dialogue(DialogueSession.from_npc("系统", [f"存档 {slot} 不存在。"]))
            else:
                if save_game(self, slot):
                    self._start_dialogue(DialogueSession.from_npc("系统", [f"保存到存档 {slot} 成功！"]))
                else:
                    self._start_dialogue(DialogueSession.from_npc("系统", [f"保存到存档 {slot} 失败。"]))
                self.state = GameState.MENU
        elif is_cancel(key):
            self.state = GameState.MENU

    def _update(self) -> None:
        if self.state == GameState.TITLE:
            self.title_blink = (self.title_blink + 1) % 60
        elif self.state == GameState.OVERWORLD:
            self._update_overworld_movement()

    def _draw(self) -> None:
        if self.state == GameState.TITLE:
            from .save import has_save
            has_saves = has_save(1) or has_save(2) or has_save(3)
            self.renderer.draw_title(self.title_blink < 30, has_saves, self.title_menu_index)
        elif self.state in (GameState.OVERWORLD, GameState.DIALOGUE):
            self.renderer.draw_overworld(
                self.world, self.player,
                player_direction=self.player_direction,
                player_walk_frame=self.player_walk_frame,
            )
            if self.state == GameState.DIALOGUE and self.dialogue:
                self.renderer.draw_dialogue(self.dialogue)
        elif self.state == GameState.BATTLE and self.battle:
            self.renderer.draw_battle(
                self.battle,
                self.battle_menu_index,
                self.battle_move_index,
                self.in_move_menu,
                self.in_party_menu,
                self.party_menu_index,
                self.in_bag_menu,
                self.bag_menu_index,
            )
        elif self.state == GameState.SHOP:
            self.renderer.draw_overworld(
                self.world, self.player,
                player_direction=self.player_direction,
                player_walk_frame=self.player_walk_frame,
            )
            self.renderer.draw_shop(self.player, self.shop_menu_index)
        elif self.state == GameState.MENU:
            self.renderer.draw_menu(self.player, self.pause_menu_index)
        elif self.state == GameState.SAVE_MENU:
            self.renderer.draw_save_menu(self.pause_menu_index, self.save_menu_index, self.save_slot)
