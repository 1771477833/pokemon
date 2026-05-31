"""Pygame 渲染（GBA 240x160 分辨率）。"""

import pygame

from .battle import Battle
from .map import WorldMap
from .tileset import DIR_DOWN, TILE_SIZE, TileAtlas
from .trainer import Trainer

GBA_W, GBA_H = 240, 160
SCALE = 3
SCREEN_W, SCREEN_H = GBA_W * SCALE, GBA_H * SCALE

COLORS = {
    "bg": (48, 56, 96),
    "grass_dark": (56, 96, 40),
    "text": (248, 248, 248),
    "text_shadow": (32, 32, 48),
    "panel": (248, 248, 248),
    "panel_border": (32, 32, 48),
    "hp_green": (80, 192, 80),
    "hp_yellow": (240, 192, 48),
    "hp_red": (224, 64, 64),
    "highlight": (248, 192, 48),
}


class Renderer:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("孙鹏大帅逼")
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.surface = pygame.Surface((GBA_W, GBA_H))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("microsoftyahei,simsun,arial", 10)
        self.font_lg = pygame.font.SysFont("microsoftyahei,simsun,arial", 12, bold=True)
        self.atlas = TileAtlas()
        pygame.key.stop_text_input()

    def tick(self, fps: int = 60) -> None:
        scaled = pygame.transform.scale(self.surface, (SCREEN_W, SCREEN_H))
        self.screen.blit(scaled, (0, 0))
        pygame.display.flip()
        self.clock.tick(fps)

    def clear(self, color: tuple[int, int, int] = COLORS["bg"]) -> None:
        self.surface.fill(color)

    def draw_text(self, text: str, x: int, y: int, *, center: bool = False, large: bool = False) -> None:
        font = self.font_lg if large else self.font
        shadow = font.render(text, True, COLORS["text_shadow"])
        main = font.render(text, True, COLORS["text"])
        if center:
            rect = main.get_rect(center=(x, y))
            self.surface.blit(shadow, rect.move(1, 1))
            self.surface.blit(main, rect)
        else:
            self.surface.blit(shadow, (x + 1, y + 1))
            self.surface.blit(main, (x, y))

    def draw_panel(self, x: int, y: int, w: int, h: int) -> None:
        pygame.draw.rect(self.surface, COLORS["panel"], (x, y, w, h))
        pygame.draw.rect(self.surface, COLORS["panel_border"], (x, y, w, h), 2)

    def draw_hp_bar(self, x: int, y: int, w: int, ratio: float) -> None:
        color = COLORS["hp_green"] if ratio > 0.5 else COLORS["hp_yellow"] if ratio > 0.2 else COLORS["hp_red"]
        pygame.draw.rect(self.surface, COLORS["panel_border"], (x, y, w, 6))
        pygame.draw.rect(self.surface, color, (x + 1, y + 1, int((w - 2) * ratio), 4))

    def draw_title(self, blink: bool, has_saves: bool = False, selected: int = 0) -> None:
        self.clear()
        self.draw_text("POKEMON", GBA_W // 2, 40, center=True, large=True)
        self.draw_text("GBA Framework", GBA_W // 2, 58, center=True)
        if has_saves:
            options = ["继续游戏", "新的开始"]
            for i, opt in enumerate(options):
                prefix = ">" if i == selected else " "
                self.draw_text(f"{prefix}{opt}", GBA_W // 2, 90 + i * 16, center=True)
        elif blink:
            self.draw_text("按 Enter 开始", GBA_W // 2, 120, center=True)
            self.draw_text("W/S 选择  J 确认", GBA_W // 2, 140, center=True)

    def draw_dialogue(self, dialogue) -> None:
        self.draw_panel(4, GBA_H - 44, GBA_W - 8, 40)
        line = dialogue.current
        if len(line) > 34:
            self.draw_text(line[:34], 12, GBA_H - 38)
            self.draw_text(line[34:68], 12, GBA_H - 26)
        else:
            self.draw_text(line, 12, GBA_H - 34)
        hint = "J 下一句" if dialogue.has_more else "J 结束"
        self.draw_text(f"{hint}  K 跳过", GBA_W - 72, GBA_H - 14)

    def draw_overworld(
        self,
        world: WorldMap,
        player: Trainer,
        *,
        player_direction: int = DIR_DOWN,
        player_walk_frame: int = 0,
    ) -> None:
        self.atlas.tick()
        tile_size = TILE_SIZE
        self.clear(COLORS["grass_dark"])
        cam_x = max(0, min(world.player_x * tile_size - GBA_W // 2, world.width * tile_size - GBA_W))
        cam_y = max(0, min(world.player_y * tile_size - GBA_H // 2, world.height * tile_size - GBA_H))

        for y in range(world.height):
            for x in range(world.width):
                px, py = x * tile_size - cam_x, y * tile_size - cam_y
                self.surface.blit(self.atlas.get_tile(world.tiles[y][x]), (px, py))

        for entity in world.entities:
            if entity.kind == "npc":
                px = entity.x * tile_size - cam_x
                py = entity.y * tile_size - cam_y
                npc_dir = entity.data.get("direction", DIR_DOWN)
                sprite = self.atlas.get_character_sprite("npc", npc_dir, 0)
                self.surface.blit(sprite, (px, py))

        px = world.player_x * tile_size - cam_x
        py = world.player_y * tile_size - cam_y
        player_sprite = self.atlas.get_character_sprite("player", player_direction, player_walk_frame)
        self.surface.blit(player_sprite, (px, py))

        self.draw_panel(0, GBA_H - 32, GBA_W, 32)
        active = player.active_pokemon()
        if active:
            self.draw_text(
                f"{player.name}  Lv.{active.level} {active.name}  HP:{active.current_hp}/{active.max_hp}",
                8, GBA_H - 26,
            )
        self.draw_text(f"${player.money}", GBA_W - 36, GBA_H - 26)
        self.draw_text("WASD移动 | J互动 | Esc菜单", 8, GBA_H - 14)

    def draw_battle(
        self,
        battle: Battle,
        menu_index: int,
        move_index: int,
        in_move_menu: bool,
        in_party_menu: bool = False,
        party_index: int = 0,
        in_bag_menu: bool = False,
        bag_index: int = 0,
    ) -> None:
        self.atlas.tick()
        self.clear(COLORS["bg"])

        bg = self.atlas.get_battle_background()
        self.surface.blit(bg, (0, 0))

        player_poke = battle.player_active
        enemy_poke = battle.enemy_active

        if enemy_poke:
            sprite = self.atlas.get_battle_sprite(enemy_poke.species.id)
            enemy_sprite = pygame.transform.flip(sprite, True, False)
            self.surface.blit(enemy_sprite, (GBA_W - 72, 8))
            self.draw_panel(8, 8, 110, 28)
            label = f"野生的 {enemy_poke.name}" if battle.is_wild else battle.enemy.name
            self.draw_text(label, 12, 12)
            self.draw_text(f"Lv.{enemy_poke.level}", 12, 22)
            ratio = enemy_poke.current_hp / enemy_poke.max_hp
            self.draw_hp_bar(12, 28, 60, ratio)

        if player_poke:
            sprite = self.atlas.get_battle_sprite(player_poke.species.id)
            self.surface.blit(sprite, (16, 52))
            self.draw_panel(8, 88, 120, 22)
            self.draw_text(f"{player_poke.name}  Lv.{player_poke.level}", 12, 92)
            ratio = player_poke.current_hp / player_poke.max_hp
            self.draw_hp_bar(12, 102, 80, ratio)
            self.draw_text(f"HP {player_poke.current_hp}/{player_poke.max_hp}", 96, 92)

        log_lines = battle.log[-2:]
        self.draw_panel(0, 112, GBA_W, 48)
        for i, line in enumerate(log_lines):
            self.draw_text(line[:28], 8, 116 + i * 12)

        if battle.finished:
            self.draw_text("J 继续", GBA_W - 56, 140)
            return

        if in_bag_menu:
            from .items import ITEMS
            items = battle.player.bag.usable_in_battle()
            self.draw_panel(GBA_W - 100, 112, 96, 48)
            self.draw_text("选择道具", GBA_W - 94, 114)
            for i, iid in enumerate(items[:4]):
                prefix = ">" if i == bag_index else " "
                tpl = ITEMS[iid]
                cnt = battle.player.bag.count(iid)
                self.draw_text(f"{prefix}{tpl.name} x{cnt}", GBA_W - 94, 124 + i * 9)
            return

        if in_party_menu:
            self.draw_panel(GBA_W - 100, 112, 96, 48)
            self.draw_text("选择精灵", GBA_W - 94, 114)
            for i, poke in enumerate(battle.player.party.members[:4]):
                prefix = ">" if i == party_index else " "
                status = "倒下" if poke.is_fainted else f"HP{poke.current_hp}"
                self.draw_text(f"{prefix}{poke.name} Lv.{poke.level} {status}", GBA_W - 94, 124 + i * 9)
            return

        if in_move_menu and player_poke:
            self.draw_panel(GBA_W - 100, 112, 96, 48)
            for i, move in enumerate(player_poke.moves[:4]):
                prefix = ">" if i == move_index else " "
                self.draw_text(
                    f"{prefix}{move.name} {move.current_pp}/{move.template.pp}",
                    GBA_W - 94, 116 + i * 11,
                )
        else:
            options = ["战斗", "背包", "精灵", "逃跑"]
            self.draw_panel(GBA_W - 100, 112, 96, 48)
            for i, opt in enumerate(options):
                prefix = ">" if i == menu_index else " "
                col = 0 if i % 2 == 0 else 1
                row = i // 2
                x = GBA_W - 94 + col * 44
                y = 116 + row * 18
                self.draw_text(f"{prefix}{opt}", x, y)

    def draw_shop(self, player: Trainer, selected: int) -> None:
        from .items import ITEMS, SHOP_STOCK

        self.draw_panel(8, 24, GBA_W - 16, 112)
        self.draw_text("友好商店", GBA_W // 2, 32, center=True, large=True)
        self.draw_text(f"金钱: ${player.money}", 16, 46)
        for i, item_id in enumerate(SHOP_STOCK):
            tpl = ITEMS[item_id]
            prefix = ">" if i == selected else " "
            y = 58 + i * 18
            self.draw_text(f"{prefix}{tpl.name}  ${tpl.price}", 16, y)
            self.draw_text(f"   {tpl.description}", 20, y + 9)
        prefix = ">" if selected == len(SHOP_STOCK) else " "
        self.draw_text(f"{prefix}离开", 16, 58 + len(SHOP_STOCK) * 18)
        self.draw_text("W/S选择 J购买/离开 K取消", 16, 124)

    def draw_menu(self, player: Trainer, selected: int) -> None:
        self.clear(COLORS["bg"])
        self.draw_text("菜单", GBA_W // 2, 20, center=True, large=True)
        self.draw_text("W/S 选择  J 确认  K 取消", GBA_W // 2, 36, center=True)
        options = ["宝可梦", "治疗", "存档", "读档", "关闭"]
        for i, opt in enumerate(options):
            prefix = ">" if i == selected else " "
            self.draw_text(f"{prefix}{opt}", 80, 50 + i * 20)
        self.draw_panel(8, 110, GBA_W - 16, 44)
        for i, p in enumerate(player.party.members[:6]):
            status = "倒下" if p.is_fainted else f"HP {p.current_hp}/{p.max_hp}"
            self.draw_text(f"{p.name} Lv.{p.level} {status}", 14, 116 + i * 7)

    def draw_save_menu(self, menu_mode: int, selected: int, slot: int) -> None:
        from .save import get_save_info

        self.clear(COLORS["bg"])
        mode_name = "读取存档" if menu_mode == 3 else "保存存档"
        self.draw_text(mode_name, GBA_W // 2, 20, center=True, large=True)
        self.draw_text("W/S 选择  J 确认  K 取消", GBA_W // 2, 36, center=True)

        for i in range(3):
            info = get_save_info(i + 1)
            prefix = ">" if i == selected else " "
            if info:
                self.draw_text(f"{prefix}存档 {i + 1}: {info['player_name']} ${info['player_money']}", 40, 50 + i * 20)
            else:
                self.draw_text(f"{prefix}存档 {i + 1}: 空", 40, 50 + i * 20)
