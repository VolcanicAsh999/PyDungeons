import dungeon_settings

import pygame
import time

pygame.init()

_handler = None


class ScreenHandler:
    def __init__(self, screen):
        global _handler
        self.screen = screen
        _handler = self

class Button:
    def __init__(self, rect, color, text, press, font_size, font=dungeon_settings.FONT_PATH, args=()):
        self.args = args
        self.rect = rect
        self.color = pygame.Color(color)
        self.text = text
        self.func = press
        self.size = font_size
        self.font = font
        if self.font == 'default': self.fonttype = pygame.font.SysFont
        else: self.fonttype = pygame.font.Font

    def update(self, events):
        global _handler
        available = False
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                available = True
        if available:
            if pygame.mouse.get_pressed()[0] and pygame.mouse.get_pos()[0] in range(self.rect.x, self.rect.x + self.rect.width) and pygame.mouse.get_pos()[1] in range(self.rect.y, self.rect.y + self.rect.height):
                self.func(*self.args)
                time.sleep(0.1)
                return

        self.draw(_handler)

    def draw(self, game):
        if pygame.mouse.get_pos()[0] in range(self.rect.x, self.rect.x + self.rect.width) and pygame.mouse.get_pos()[1] in range(self.rect.y, self.rect.y + self.rect.height):
            pygame.draw.rect(game.screen, pygame.Color('white'), pygame.Rect(self.rect.x - 2, self.rect.y - 2, self.rect.width + 4, self.rect.height + 4))
        pygame.draw.rect(game.screen, self.color, self.rect)
        text = self.fonttype(self.font, self.size).render(self.text, 1, pygame.Color('black'))
        xsize, ysize = text.get_width(), text.get_height()
        xrect_size, yrect_size = self.rect.width, self.rect.height
        xoffset, yoffset = (xrect_size - xsize) // 2, (yrect_size - ysize) // 2
        game.screen.blit(text, (self.rect.x + xoffset, self.rect.y + yoffset))

    def set_text(self, text):
        self.text = text

    def destroy(self):
        self.rect.x = self.rect.y = 10000000
        def q(*args):
            ...
        self.update = q

    def update_(self, x, y, width, height, font_size):
        self.rect = pygame.Rect(x, y, width, height)
        self.size = font_size

class ScrollBar:
    def __init__(self, pos, height, press, color, do_update_every_motion=False):
        self.sliderect = pygame.Rect(pos[0], pos[1] - 3, 10, 10)
        self.rect = pygame.Rect(*pos, 10, height)
        self.press = press
        self.hit = False
        self.color = color
        self.cango = range(self.rect.y - 3, self.rect.y + height - 3)
        self.y = self.rect.y
        self.prevpos = pygame.mouse.get_pos()[1]
        self.doupdateevery = do_update_every_motion

    def update(self, events):
        self.draw(_handler)
        if not self.hit:
            pos = pygame.mouse.get_pos()
            if pos[0] in range(self.sliderect.x, self.sliderect.x + self.sliderect.width) and pos[1] in range(self.sliderect.y, self.sliderect.y + self.sliderect.height):
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
                        self.click(True)

        else:
            if pygame.mouse.get_pos()[1] in self.cango:
                self.sliderect = pygame.Rect(self.sliderect.x, pygame.mouse.get_pos()[1], 10, 10)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP and not pygame.mouse.get_pressed()[0]:
                    self.click(False)

    def draw(self, game):
        if self.isactive:
            color = pygame.Color('dark grey')
        elif pygame.mouse.get_pos()[0] in range(self.rect.x, self.rect.x + self.rect.width) and pygame.mouse.get_pos()[1] in range(self.rect.y, self.rect.y + self.rect.height):
            color = pygame.Color('grey')
        else:
            color = pygame.Color('light grey')
        pygame.draw.rect(game.screen, self.color, self.rect)
        pygame.draw.rect(game.screen, color, self.rect)

    def click(self, hit):
        self.hit = hit
        self.prevpos = pygame.mouse.get_pos()[1]
