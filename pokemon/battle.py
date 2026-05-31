"""回合制战斗系统。"""

import random
from dataclasses import dataclass, field

from .enums import BattlePhase, MoveCategory
from .formula import calc_damage, stat_for_category
from .move import Move
from .pokemon import Pokemon
from .trainer import Trainer


@dataclass
class BattleAction:
    kind: str  # "move" | "run" | "switch" | "item"
    move_index: int = 0
    switch_index: int = 0
    item_id: str = ""


@dataclass
class Battle:
    player: Trainer
    enemy: Trainer
    phase: BattlePhase = BattlePhase.INTRO
    is_wild: bool = False
    log: list[str] = field(default_factory=list)
    finished: bool = False
    player_won: bool = False
    pending_exp: int = 0

    def start(self) -> list[str]:
        self.log.clear()
        self.finished = False
        self.player_won = False
        self.pending_exp = 0
        self.phase = BattlePhase.PLAYER_TURN

        enemy = self.enemy.active_pokemon()
        if self.is_wild and enemy:
            self.log.append(f"野生的 {enemy.name} 出现了！")
        else:
            self.log.append(f"{self.enemy.name} 发起了挑战！")
        return list(self.log)

    @property
    def player_active(self) -> Pokemon | None:
        return self.player.active_pokemon()

    @property
    def enemy_active(self) -> Pokemon | None:
        return self.enemy.active_pokemon()

    def player_choose(self, action: BattleAction) -> list[str]:
        """玩家选择行动，返回本回合消息。"""
        if self.finished or self.phase != BattlePhase.PLAYER_TURN:
            return []

        messages: list[str] = []

        if action.kind == "run":
            if self.is_wild:
                self.log.append("成功逃跑了！")
                self.finished = True
                self.player_won = False
                return list(self.log)
            self.log.append("不能逃跑！")
            return list(self.log)

        if action.kind == "switch":
            return self._switch_player(action.switch_index)

        if action.kind == "item":
            return self._use_item(action.item_id)

        if action.kind == "move":
            return self._execute_turn(action.move_index)

        return messages

    def _use_item(self, item_id: str) -> list[str]:
        from .items import HEAL_VALUES, ITEMS

        template = ITEMS.get(item_id)
        player_poke = self.player_active
        enemy_poke = self.enemy_active
        if not template or not player_poke:
            self.log.append("无法使用该道具。")
            return list(self.log)

        if template.kind == "heal":
            if item_id not in HEAL_VALUES:
                self.log.append("无法使用该道具。")
                return list(self.log)
            msg = self.player.bag.use_heal(item_id, player_poke)
            self.log.append(msg)
            if self._check_end():
                return list(self.log)
            self.phase = BattlePhase.ENEMY_TURN
            self._enemy_turn()
            return list(self.log)

        if template.kind == "ball":
            if not self.is_wild or not enemy_poke:
                self.log.append("只能对野生精灵使用精灵球！")
                return list(self.log)
            if not self.player.bag.remove(item_id):
                self.log.append("没有精灵球了！")
                return list(self.log)
            self.log.append(f"扔出了 {template.name}！")
            hp_ratio = enemy_poke.current_hp / max(1, enemy_poke.max_hp)
            catch_rate = 0.2 + 0.55 * (1 - hp_ratio)
            if random.random() < catch_rate:
                self.log.append(f"太好了！抓住了 {enemy_poke.name}！")
                if len(self.player.party.members) < self.player.party.max_size:
                    caught = Pokemon.create(enemy_poke.species.id, enemy_poke.level)
                    self.player.party.add(caught)
                else:
                    self.log.append("队伍已满，无法加入新精灵。")
                self.finished = True
                self.player_won = True
                self.phase = BattlePhase.END
            else:
                self.log.append("可惜！精灵逃出来了……")
                self.phase = BattlePhase.ENEMY_TURN
                self._enemy_turn()
            return list(self.log)

        self.log.append("无法使用该道具。")
        return list(self.log)

    def _switch_player(self, index: int) -> list[str]:
        if index < 0 or index >= len(self.player.party.members):
            self.log.append("无效的切换目标。")
            return list(self.log)

        target = self.player.party.members[index]
        if target.is_fainted:
            self.log.append(f"{target.name} 已经倒下了！")
            return list(self.log)
        if target is self.player_active:
            self.log.append(f"{target.name} 已经在场上！")
            return list(self.log)

        self.player.party.members.remove(target)
        self.player.party.members.insert(0, target)
        self.log.append(f"去吧！{target.name}！")
        self.phase = BattlePhase.ENEMY_TURN
        self._enemy_turn()
        return list(self.log)

    def _execute_turn(self, move_index: int) -> list[str]:
        player_poke = self.player_active
        enemy_poke = self.enemy_active
        if not player_poke or not enemy_poke:
            return []

        if move_index < 0 or move_index >= len(player_poke.moves):
            self.log.append("无效的招式。")
            return list(self.log)

        player_move = player_poke.moves[move_index]
        enemy_move = self._pick_enemy_move(enemy_poke)

        # 按速度决定先后手（同速随机）
        player_first = player_poke.speed > enemy_poke.speed or (
            player_poke.speed == enemy_poke.speed and random.random() < 0.5
        )

        order = (
            [(player_poke, enemy_poke, player_move, True), (enemy_poke, player_poke, enemy_move, False)]
            if player_first
            else [(enemy_poke, player_poke, enemy_move, False), (player_poke, enemy_poke, player_move, True)]
        )

        for attacker, defender, move, is_player in order:
            if attacker.is_fainted or defender.is_fainted:
                continue
            self._use_move(attacker, defender, move, is_player_attacker=is_player)

        if self._check_end():
            return list(self.log)

        self.phase = BattlePhase.PLAYER_TURN
        return list(self.log)

    def _pick_enemy_move(self, pokemon: Pokemon) -> Move:
        usable = [m for m in pokemon.moves if m.current_pp > 0]
        return random.choice(usable) if usable else pokemon.moves[0]

    def _use_move(
        self,
        attacker: Pokemon,
        defender: Pokemon,
        move: Move,
        *,
        is_player_attacker: bool,
    ) -> None:
        side = "player" if is_player_attacker else "enemy"
        if not move.use():
            self.log.append(f"{attacker.name} 的 {move.name} 没有 PP 了！")
            return

        self.log.append(f"{attacker.name} 使用了 {move.name}！")

        if move.category == MoveCategory.STATUS:
            self.log.append("但是没有任何效果……")
            return

        if random.randint(1, 100) > move.accuracy:
            self.log.append("攻击未命中！")
            return

        atk, def_ = stat_for_category(attacker.stats, move.category)
        damage, effectiveness, _ = calc_damage(
            level=attacker.level,
            power=move.power,
            attack=atk,
            defense=def_,
            move_type=move.move_type,
            attacker_types=attacker.types,
            defender_types=defender.types,
            category=move.category,
        )

        if effectiveness == 0:
            self.log.append("对 {0} 似乎没有效果……".format(defender.name))
            return

        actual = defender.take_damage(damage)
        self.log.append(f"对 {defender.name} 造成了 {actual} 点伤害！")

        if effectiveness >= 2:
            self.log.append("效果拔群！")
        elif effectiveness <= 0.5:
            self.log.append("效果不佳……")

        if defender.is_fainted:
            self.log.append(f"{defender.name} 倒下了！")
            if side == "player":
                self.pending_exp += defender.exp_yield()

    def _enemy_turn(self) -> None:
        """强制敌人行动（切换后）。"""
        player_poke = self.player_active
        enemy_poke = self.enemy_active
        if not player_poke or not enemy_poke or enemy_poke.is_fainted:
            self._check_end()
            self.phase = BattlePhase.PLAYER_TURN if not self.finished else BattlePhase.END
            return

        move = self._pick_enemy_move(enemy_poke)
        self._use_move(enemy_poke, player_poke, move, is_player_attacker=False)
        self._check_end()
        if not self.finished:
            self.phase = BattlePhase.PLAYER_TURN
        else:
            self.phase = BattlePhase.END

    def _check_end(self) -> bool:
        if self.enemy.party.all_fainted():
            self.finished = True
            self.player_won = True
            self.phase = BattlePhase.END
            if self.is_wild:
                self.log.append("获得了胜利！")
            else:
                self.log.append(f"打败了 {self.enemy.name}！")
            winner = self.player_active
            if winner and self.pending_exp > 0:
                msgs = winner.gain_exp(self.pending_exp)
                self.log.extend(msgs)
                self.log.append(f"{winner.name} 获得了 {self.pending_exp} 经验！")
            return True

        if self.player.party.all_fainted():
            self.finished = True
            self.player_won = False
            self.phase = BattlePhase.END
            self.log.append("你被打败了……")
            return True

        return False
