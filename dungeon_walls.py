import pygame

WIDTH, HEIGHT = 20, 20


class Wall:
    def __repr__(self): return f'Wall({self.rect.x}, {self.rect.y})'

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, WIDTH, HEIGHT)
        self.color = pygame.Color('dark gray')

    def render(self, game):
        self.draw(game)

    def draw(self, game):
        pygame.draw.rect(game.screen, self.color, self.rect)


def genwalls(width=2000, height=1000):
    walls = []
    for w in [0, width]:
        for h in range(0, height, HEIGHT):
            walls.append(Wall(w, h))
    for w in range(0, width, WIDTH):
        for h in [0, height]:
            walls.append(Wall(w, h))
    return walls


def genfromlist(poses):
    walls = []
    for pos in poses:
        walls.append(Wall(pos['x'], pos['y']))
    return walls
