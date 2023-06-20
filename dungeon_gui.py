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
        if self.font == 'default':
            self.fonttype = pygame.font.SysFont
        else:
            self.fonttype = pygame.font.Font

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
            pygame.draw.rect(game.screen, pygame.Color('white'), pygame.Rect(
                self.rect.x - 2, self.rect.y - 2, self.rect.width + 4, self.rect.height + 4))
        pygame.draw.rect(game.screen, self.color, self.rect)
        text = self.fonttype(self.font, self.size).render(
            self.text, 1, pygame.Color('black'))
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


def get_enchant(weapon, game):
    a = {1: 0, 2: 0, 3: 0}
    def _1(): a[1] = 1
    def _2(): a[2] = 1
    def _3(): a[3] = 1
    s = game.screen
    w = s.get_width()
    h = s.get_height()
    b1 = Button(pygame.Rect((w // 2) - 200, 50, 400, 80), pygame.Color('light grey'), weapon.slots[1] + ' ' + str(weapon.slotlevel[1]+1), _1, 70, 'default')
    b2 = Button(pygame.Rect((w // 2) - 200, 200, 400, 80), pygame.Color('light grey'), weapon.slots[2] + ' ' + str(weapon.slotlevel[2]+1), _2, 70, 'default')
    b3 = Button(pygame.Rect((w // 2) - 200, 350, 400, 80), pygame.Color('light grey'), weapon.slots[3] + ' ' + str(weapon.slotlevel[3]+1), _3, 70, 'default')
    null = type('', (), {'update': lambda x: ..., 'update_': lambda a, b, c, d, e: ...})
    if weapon.slotlevel[1] == 3:
        b1 = null
    if weapon.slotlevel[2] == 3:
        b2 = null
    if weapon.slotlevel[3] == 3:
        b3 = null
    s.fill(pygame.Color('dark green'))
    while 1:
        events = pygame.event.get()
        b1.update(events)
        b2.update(events)
        b3.update(events)
        for event in events:
            if event.type == pygame.VIDEORESIZE:
                b1.update_((w // 2) - 200, 50, 400, 80, 70)
                b2.update_((w // 2) - 200, 200, 400, 80, 70)
                b3.update_((w // 2) - 200, 350, 400, 80, 70)
        if a[1]: return 1
        if a[2]: return 2
        if a[3]: return 3
        pygame.display.update()


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
        self.isactive = False

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
                self.sliderect = pygame.Rect(
                    self.sliderect.x, pygame.mouse.get_pos()[1], 10, 10)
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
        self.isactive = True
