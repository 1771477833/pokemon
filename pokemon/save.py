"""存档与读档。"""

import json
import os
from dataclasses import dataclass

from .data import MOVES, SPECIES
from .enums import GameState
from .items import Bag
from .move import Move
from .party import Party
from .pokemon import Pokemon
from .trainer import Trainer


SAVE_DIR = "saves"
MAX_SAVE_SLOTS = 3


@dataclass
class SaveData:
    player_name: str
    player_money: int
    player_bag: dict[str, int]
    party_data: list[dict]
    player_x: int
    player_y: int
    defeated_trainers: list[tuple[int, int]]
    game_state: str


def _serialize_pokemon(pokemon: Pokemon) -> dict:
    return {
        "species_id": pokemon.species.id,
        "level": pokemon.level,
        "current_hp": pokemon.current_hp,
        "moves": [move.id for move in pokemon.moves],
        "nickname": pokemon.nickname,
        "experience": pokemon.experience,
    }


def _deserialize_pokemon(data: dict) -> Pokemon:
    species = SPECIES[data["species_id"]]
    moves = [Move.from_id(mid) for mid in data["moves"]]
    pokemon = Pokemon(
        species=species,
        level=data["level"],
        current_hp=data["current_hp"],
        moves=moves,
        nickname=data.get("nickname"),
        experience=data.get("experience", 0),
    )
    return pokemon


def _serialize_party(party: Party) -> list[dict]:
    return [_serialize_pokemon(p) for p in party.members]


def _deserialize_party(data: list[dict]) -> Party:
    party = Party()
    for pdata in data:
        party.members.append(_deserialize_pokemon(pdata))
    return party


def _serialize_bag(bag: Bag) -> dict[str, int]:
    return dict(bag.items)


def _deserialize_bag(data: dict[str, int]) -> Bag:
    return Bag(items=dict(data))


def serialize_game(game) -> SaveData:
    return SaveData(
        player_name=game.player.name,
        player_money=game.player.money,
        player_bag=_serialize_bag(game.player.bag),
        party_data=_serialize_party(game.player.party),
        player_x=game.world.player_x,
        player_y=game.world.player_y,
        defeated_trainers=list(game.defeated_trainers),
        game_state=game.state.name,
    )


def deserialize_game(data: SaveData, world_creator) -> "Game":
    from .game import Game

    party = _deserialize_party(data.party_data)
    bag = _deserialize_bag(data.player_bag)
    player = Trainer(
        name=data.player_name,
        party=party,
        is_player=True,
        money=data.player_money,
        bag=bag,
    )

    game = Game()
    game.player = player
    game.world.player_x = data.player_x
    game.world.player_y = data.player_y
    game.defeated_trainers = set(data.defeated_trainers)
    game.state = GameState[data.game_state]

    return game


def _get_save_path(slot: int) -> str:
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
    return os.path.join(SAVE_DIR, f"save_{slot}.json")


def save_game(game, slot: int = 1) -> bool:
    if slot < 1 or slot > MAX_SAVE_SLOTS:
        return False

    data = serialize_game(game)
    save_dict = {
        "version": 1,
        "slot": slot,
        "data": {
            "player_name": data.player_name,
            "player_money": data.player_money,
            "player_bag": data.player_bag,
            "party_data": data.party_data,
            "player_x": data.player_x,
            "player_y": data.player_y,
            "defeated_trainers": data.defeated_trainers,
            "game_state": data.game_state,
        },
    }

    try:
        with open(_get_save_path(slot), "w", encoding="utf-8") as f:
            json.dump(save_dict, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def load_game(slot: int = 1):
    if slot < 1 or slot > MAX_SAVE_SLOTS:
        return None

    path = _get_save_path(slot)
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            save_dict = json.load(f)

        if save_dict.get("version") != 1:
            return None

        data = SaveData(
            player_name=save_dict["data"]["player_name"],
            player_money=save_dict["data"]["player_money"],
            player_bag=save_dict["data"]["player_bag"],
            party_data=save_dict["data"]["party_data"],
            player_x=save_dict["data"]["player_x"],
            player_y=save_dict["data"]["player_y"],
            defeated_trainers=save_dict["data"]["defeated_trainers"],
            game_state=save_dict["data"]["game_state"],
        )

        return deserialize_game(data, None)
    except Exception:
        return None


def has_save(slot: int = 1) -> bool:
    if slot < 1 or slot > MAX_SAVE_SLOTS:
        return False
    return os.path.exists(_get_save_path(slot))


def get_save_info(slot: int) -> dict | None:
    if slot < 1 or slot > MAX_SAVE_SLOTS:
        return None

    path = _get_save_path(slot)
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            save_dict = json.load(f)

        return {
            "slot": slot,
            "player_name": save_dict["data"]["player_name"],
            "player_money": save_dict["data"]["player_money"],
            "party_count": len(save_dict["data"]["party_data"]),
        }
    except Exception:
        return None
