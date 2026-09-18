"""Main-thread composition, frame lifetime and orderly shutdown."""
import pygame

from client.application.controller import Controller
from client.network.worker import NetworkWorker
from client.ui.input import InputRouter
from client.ui.layout import build_layout
from client.ui.renderer import ScreenRenderer


def _sync_text_input(focus):
    if focus:
        pygame.key.start_text_input()
    else:
        pygame.key.stop_text_input()


def run(config):
    network = NetworkWorker(config)
    controller = Controller(network)
    pygame.display.init()
    pygame.font.init()
    pygame.display.set_caption("작은 마을 · Game-client")
    screen = pygame.display.set_mode((config["window_width"], config["window_height"]), pygame.RESIZABLE)
    renderer = ScreenRenderer(screen, config)
    input_router = InputRouter()
    clock = pygame.time.Clock()
    _sync_text_input(controller.app.login.focus)
    network.start()
    try:
        while True:
            for event in network.drain_events():
                controller.handle_network_event(event)
            layout = build_layout(screen.get_size())
            for event in pygame.event.get():
                if controller.app.closing:
                    continue
                intent = input_router.route(event, layout, controller.app, controller.queries)
                if intent is None:
                    continue
                if intent["kind"] == "resize":
                    screen = pygame.display.set_mode(intent["size"], pygame.RESIZABLE)
                    renderer.set_screen(screen)
                    layout = build_layout(screen.get_size())
                    continue
                old_focus = controller.app.login.focus
                controller.handle_intent(intent)
                if old_focus != controller.app.login.focus:
                    _sync_text_input(controller.app.login.focus)
            renderer.render(controller.screen_model(), layout, clock.get_fps())
            if not network.is_alive():
                break
            clock.tick(config["fps"])
    finally:
        controller.app.closing = True
        controller.app.login.clear()
        network.stop()
        while network.is_alive():
            pygame.event.pump()
            for event in network.drain_events():
                controller.handle_network_event(event)
            layout = build_layout(screen.get_size())
            renderer.render(controller.screen_model(), layout, clock.get_fps())
            clock.tick(config["fps"])
        network.stop(timeout=0)
        pygame.quit()
    return 0
