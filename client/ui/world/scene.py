"""World draw order only."""
from client.ui.world.actors import draw_actors
from client.ui.world.markers import draw_markers
from client.ui.world.nameplates import draw_nameplates
from client.ui.world.projection import project_players
from client.ui.world.terrain import draw_decorations, draw_terrain


def draw_world(painter, game, layout):
    painter.card(layout.world_rect)
    draw_terrain(painter)
    draw_decorations(painter)
    draw_markers(painter)
    if game.own is not None and game.has_ws_state:
        actors, nameplates = project_players(game.players, game.own["player_id"])
        draw_actors(painter, actors)
        draw_nameplates(painter, nameplates)
