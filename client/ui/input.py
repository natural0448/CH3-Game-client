"""Translate Pygame events into application intents."""
import pygame


class InputRouter:
    GAME_KEYS = {
        pygame.K_UP: "up", pygame.K_DOWN: "down",
        pygame.K_LEFT: "left", pygame.K_RIGHT: "right",
        pygame.K_SPACE: "gather", pygame.K_x: "train",
    }

    def route(self, event, layout, app, queries):
        if event.type == pygame.QUIT:
            return {"kind": "quit"}
        if event.type == pygame.VIDEORESIZE:
            return {"kind": "resize", "size": (max(320, event.w), max(240, event.h))}
        if event.type == pygame.TEXTINPUT and app.login.focus and app.phase == "signed_out":
            return {"kind": "text", "text": event.text}
        if event.type == pygame.KEYDOWN:
            if app.login.focus:
                if event.key == pygame.K_TAB:
                    field = "password" if app.login.focus == "username" else "username"
                    return {"kind": "focus", "field": field}
                if event.key == pygame.K_ESCAPE:
                    return {"kind": "focus", "field": None}
                if event.key == pygame.K_BACKSPACE:
                    return {"kind": "backspace"}
                if event.key == pygame.K_RETURN:
                    return {"kind": "login"}
                return None
            if event.key in self.GAME_KEYS:
                return {"kind": "command", "action": self.GAME_KEYS[event.key]}
            if event.key == pygame.K_TAB and app.phase == "signed_out":
                return {"kind": "focus", "field": "username"}
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            open_panels = {kind for kind, slot in queries.slots.items() if slot.opened}
            hit = layout.hit_test(event.pos, open_panels)
            if hit in ("username", "password"):
                return {"kind": "focus", "field": hit}
            if hit == "login":
                return {"kind": "login"}
            if hit == "logout":
                return {"kind": "logout"}
            if hit in ("delivery", "analytics", "actions", "ingest", "history"):
                return {"kind": "query", "query": hit}
            if hit == "actions_refresh":
                return {"kind": "query", "query": "actions"}
            if hit == "ingest_refresh":
                return {"kind": "query", "query": "ingest"}
            if hit and hit.endswith("_close"):
                return {"kind": "panel_close", "query": hit.removesuffix("_close")}
            if hit and hit.endswith(("_previous", "_next")):
                query, operation = hit.rsplit("_", 1)
                return {"kind": "panel_page", "query": query,
                        "step": -1 if operation == "previous" else 1}
            if hit == "delivery_api":
                return {"kind": "toggle_api"}
            if hit == "api_source" and app.show_api:
                return {"kind": "api_source"}
            if hit in ("api_up", "api_down") and app.show_api:
                return {"kind": "api_scroll", "step": -3 if hit == "api_up" else 3}
            if hit in ("up", "down", "left", "right", "gather", "train"):
                return {"kind": "command", "action": hit}
            return {"kind": "focus", "field": None}
        return None
