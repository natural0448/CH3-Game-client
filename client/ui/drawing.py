"""Reusable Pygame drawing primitives."""
import pygame

INK = (33, 53, 49)
MUTED = (100, 116, 105)
GREEN = (29, 105, 83)
CREAM = (245, 244, 234)
WHITE = (255, 254, 247)
LINE = (219, 224, 208)


class Painter:
    def __init__(self, canvas, assets, layout):
        self.canvas = canvas
        self.fonts = assets.fonts
        self.images = assets.images
        self.layout = layout

    def text(self, text, position, size=17, color=INK):
        self.canvas.blit(self.fonts[size].render(str(text), True, color), position)

    def wrapped(self, text, rect, size=15, color=MUTED):
        font = self.fonts[size]
        line, y = "", rect.y
        for char in str(text):
            if char == "\n" or font.size(line + char)[0] > rect.width:
                self.text(line, (rect.x, y), size, color)
                y += font.get_linesize()
                line = "" if char == "\n" else char
                if y + font.get_linesize() > rect.bottom:
                    return
            else:
                line += char
        self.text(line, (rect.x, y), size, color)

    def card(self, rect, color=WHITE):
        pygame.draw.rect(self.canvas, color, rect, border_radius=12)
        pygame.draw.rect(self.canvas, LINE, rect, 1, border_radius=12)

    def button(self, name, label, enabled=True):
        rect = self.layout.controls[name]
        pygame.draw.rect(self.canvas, GREEN if enabled else (219, 225, 211), rect, border_radius=8)
        text = self.fonts[17].render(label, True, WHITE if enabled else MUTED)
        self.canvas.blit(text, text.get_rect(center=rect.center))
