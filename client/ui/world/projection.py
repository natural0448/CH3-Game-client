"""Pure conversion from confirmed player state to display DTOs."""
from dataclasses import dataclass

from client.contracts.game import TILE


@dataclass(frozen=True)
class ActorView:
    player_id: int
    x: int
    y: int
    pixel_x: int
    pixel_y: int
    mine: bool


@dataclass(frozen=True)
class NameplateView:
    tile_x: int
    tile_y: int
    label: str


def project_players(players, own_player_id):
    actors = []
    occupants = {}
    ordered = sorted(players, key=lambda item: (
        item["y"], item["player_id"] == own_player_id, item["player_id"]
    ))
    for player in ordered:
        tile = (player["x"], player["y"])
        occupants.setdefault(tile, []).append(player)
        actors.append(ActorView(
            player_id=player["player_id"], x=player["x"], y=player["y"],
            pixel_x=24 + player["x"] * TILE, pixel_y=152 + player["y"] * TILE,
            mine=player["player_id"] == own_player_id,
        ))
    nameplates = []
    for (tile_x, tile_y), group in occupants.items():
        label = ", ".join(item.get("username") or f"#{item['player_id']}" for item in group[:3])
        if len(group) > 3:
            label += f" +{len(group) - 3}"
        if len(group) > 1:
            label += f" ({len(group)}명)"
        nameplates.append(NameplateView(tile_x, tile_y, label))
    return actors, nameplates
