import math
import pygame


def distance_between(x1, y1, x2, y2):
    # distance between (x1, y1) and (x2, y2)
    return math.sqrt(math.pow(x1-x2, 2) + math.pow(y1-y2, 2))


def get_nearest_target(game, me, hostile):  # get the nearest target
    if hostile:
        player = None  # nearest helpful/player
        distance = 10000000000
        for i in [game.player] + game.helpfuls:
            dis = distance_between(me.rect.x, me.rect.y, i.rect.x, i.rect.y)
            if dis < distance:
                distance = dis
                player = i
        return player
    else:
        enemy = None  # nearest enemy
        distance = 10000000000
        for i in game.enemies:
            dis = distance_between(me.rect.x, me.rect.y, i.rect.x, i.rect.y)
            if dis < distance:
                distance = dis
                enemy = i
        return enemy
