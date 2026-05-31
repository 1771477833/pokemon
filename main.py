#!/usr/bin/env python3
"""GBA 风格口袋妖怪游戏框架 - 入口。"""

import os

# 避免中文输入法拦截 WASD
os.environ.setdefault("SDL_IM_MODULE", "none")

from pokemon.game import Game


def main() -> None:
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
