"""Main-thread screen composition and final display update."""
import threading

import pygame

from client.ui.assets import AssetStore
from client.ui.drawing import CREAM, Painter
from client.ui.layout import CANVAS
from client.ui.overlays import draw_connection_overlay, draw_status
from client.ui.panels import draw_query_panels
from client.ui.sections.account import draw_account
from client.ui.sections.activity import draw_activity
from client.ui.sections.commands import draw_commands
from client.ui.sections.header import draw_header
from client.ui.sections.lobby import draw_lobby
from client.ui.world.scene import draw_world
from client.ui.ads import AdsRenderer


class ScreenRenderer:
    def __init__(self, screen, config):
        assert threading.current_thread() is threading.main_thread()
        self.screen = screen
        self.canvas = pygame.Surface(CANVAS)
        self.assets = AssetStore(config)
        self.ads = AdsRenderer()

    def set_screen(self, screen):
        self.screen = screen

    def render(self, model, layout, fps):
        assert threading.current_thread() is threading.main_thread()
        app, game, queries = model.app, model.game, model.queries
        painter = Painter(self.canvas, self.assets, layout)
        self.canvas.fill(CREAM)
        draw_header(painter, app, game, fps)
        draw_account(painter, app)
        painter.button("logout", "로그아웃",
                       game.own is not None and app.phase != "logging_out" and not app.closing)
        draw_world(painter, game, layout)
        draw_commands(painter, app, game)
        draw_activity(painter, app, game, queries)
        draw_lobby(painter, app, game, queries)
        receipts = self.ads.draw(painter, model.ads, game.own is not None and app.phase != "logging_out")
        draw_connection_overlay(painter, game)
        draw_query_panels(painter, queries)
        draw_status(painter, app, self.assets.notice)
        size, offset = layout.viewport()
        self.screen.fill((223, 228, 211))
        frame = self.canvas if size == CANVAS else pygame.transform.smoothscale(self.canvas, size)
        self.screen.blit(frame, offset)
        pygame.display.flip()
        visible = (pygame.display.get_active() and not app.show_api
                   and not any(slot.opened for slot in queries.values()))
        return receipts if visible else {}
