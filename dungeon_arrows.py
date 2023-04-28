import pygame
import math
import random
import dungeon_settings
# imports


class Arrow:
    def __init__(self, startpos, target, damage, knockback, safe,
                 chain=False, chainstack=0, rot=None, growing=False):
        self.x, self.y = startpos  # set the x and y positions
        self.target = target  # keep track of where it is heading

        self.start = startpos

        self.ischain = chain  # need to reduce chain opness
        self.chainstack = chainstack

        self.tip_color = pygame.Color('light grey')  # arrow tip color
        self.shaft_color = pygame.Color('brown')  # arrow shaft color

        self.speed = 5

        self.damage = damage
        self.knockback = knockback  # knockback don't work at the moment

        self.safe = safe

        if rot is None:  # figure out the dx and dy needed (not my invention)
            r = math.dist(self.target, self.start)

            if r > 0:
                if r >= self.speed:
                    self.dx = ((self.target[0] - self.x) / r) * self.speed
                else:
                    self.dx = self.target[0] - self.x
            else:
                self.dx = 0

            if r > 0:
                if r >= self.speed:
                    self.dy = ((self.target[1] - self.y) / r) * self.speed
                else:
                    self.dy = self.target[1] - self.y
            else:
                self.dy = 0

        self.xrect = pygame.Rect(self.x, self.y, int(self.dx * 5),
                                 int(self.dy * 5))  # xrect is... something

        width = self.dx * 5
        height = self.dy * 5  # size of the arrow

        if width >= 0:
            self.d1 = -5
        elif width < 0:
            self.d1 = 5
        if height >= 0:
            self.d2 = -5
        elif height < 0:
            self.d2 = 5

        self.rect = pygame.Rect(self.x - self.d1, self.y - self.d2,
                                int(self.dx * 5) + (self.d1 * 2),
                                int(self.dy * 5) + (self.d2 * 2))

        self.x += self.dx * 2
        self.y += self.dy * 2

        self.growing = growing  # whether or not the arrow has growing power

        if r <= 0:
            # if something weird happened just destroy the evidence
            self.destroy(type('Game', (), {'arrows': []})())
            return

    # move the x, y, rect.x, rect.y, xrect.x, and xrect.y

    def move_xy(self, x, y):
        self.x += x
        self.y += y
        self.rect.x = int(self.x) - self.d1
        self.rect.y = int(self.y) - self.d2
        self.xrect.x = int(self.x)
        self.xrect.y = int(self.y)

    def render(self, game):
        self.move_xy(self.dx, self.dy)  # move towards its target

        self.draw(game)  # draw it

        for entity in game.enemies + game.helpfuls + \
                      game.spawners + [game.player]:
            rec = entity.rect
            entity.rect = pygame.Rect(rec.x - 8, rec.y - 8,
                                      rec.width + 16, rec.height + 16)

            if entity != self.safe and \
               pygame.sprite.collide_rect(entity, self):
                self.hit(entity, game)
                self.destroy(game)
                dungeon_settings.arrow_hit.play()

            entity.rect = rec

        if self.growing:
            self.damage += 0.04  # increase damage if arrow is growing

        if self.rect.x < -100 or \
           self.rect.x > game.screen.get_width() + 100 or \
           self.rect.y < -100 or self.rect.y > game.screen.get_height() + 100:
            self.destroy(game)  # kill arrow if it gets out of screen

    def draw(self, game):
        pygame.draw.line(game.screen, self.shaft_color,
                         (self.xrect.x, self.xrect.y),
                         (self.xrect.x + (self.dx * 5),
                          self.xrect.y + (self.dy * 5)), 3)
        pygame.draw.circle(game.screen, self.tip_color,
                          (int(self.xrect.x + (self.dx * 5)),
                           int(self.xrect.y + (self.dy * 5))), 3)  # tip

    def destroy(self, game):
        if self in game.arrows:
            game.arrows.remove(self)
        self.rect.x = 10000
        self.rect.y = 10000
        self.xrect.x = 10000
        self.xrect.y = 10000
        self.x = 10000
        self.y = 10000

    def hit(self, entity, game):  # hit something
        x = self.rect.x
        y = self.rect.y
        self.rect.x = self.xrect.x
        self.rect.y = self.xrect.y
        if self.growing:
            self.growing = round(self.growing)
        if type(entity) not in [dungeon_helpful.Golem, dungeon_helpful.Wolf,
                                dungeon_helpful.Bat]:
            entity.take_damage(self.damage)
        else:
            entity.take_damage(self, self.damage)
        entity.knockback(self.knockback, self)  # don't work! waah!
        if hasattr(entity, 'armor_use'):
            entity.armor_use(self, game)  # just for players
        if self.ischain and \
           random.randint(0, 10 - int(round(self.chainstack / 2))) == 0:
            # 5 different directions
            game.arrows.append(type(self)((self.rect.x + entity.rect.width,
                    self.rect.y + entity.rect.height),
                    (self.rect.x + (int(self.dx) * 10), self.rect.y),
                    self.damage, self.knockback, self.safe, self.ischain,
                    self.chainstack - 1))
            game.arrows.append(type(self)((self.rect.x + entity.rect.width,
                    self.rect.y + entity.rect.height),
                    (self.rect.x + (int(self.dx) * 10),
                     self.rect.y + (int(self.dy) * 10)),
                    self.damage, self.knockback, self.safe, self.ischain,
                    self.chainstack - 1))
            game.arrows.append(type(self)((self.rect.x + entity.rect.width,
                    self.rect.y + entity.rect.height),
                    (self.rect.x, self.rect.y + (int(self.dy) * 10)),
                    self.damage, self.knockback, self.safe, self.ischain,
                    self.chainstack - 1))
            game.arrows.append(type(self)((self.rect.x + entity.rect.width,
                    self.rect.y + entity.rect.height),
                    (self.rect.x + (int(self.dx) * 5),
                    self.rect.y + (int(self.dy) * 5)),
                    self.damage, self.knockback, self.safe, self.ischain,
                    self.chainstack - 1))
            game.arrows.append(type(self)((self.rect.x + entity.rect.width,
                    self.rect.y + entity.rect.height),
                    (self.rect.x + (int(self.dx) * -5),
                     self.rect.y + (int(self.dy) * -5)),
                    self.damage, self.knockback, self.safe, self.ischain,
                    self.chainstack - 1))
        self.rect.x = x
        self.rect.y = y


class SlowArrow(Arrow):
    def __init__(self, startpos, target, damage, knockback, safe,
                 chain=False, chainstack=0, growing=False):
        super().__init__(startpos, target, damage, knockback, safe,
                         chain, chainstack)
        self.tip_color = pygame.Color('dark grey')

    def hit(self, entity, game):
        super().hit(entity, game)
        if hasattr(entity, 'effects') and entity.effects['slowness'] < 15:
            entity.effects['slowness'] = 15
        elif not hasattr(entity, 'effects'):  # if it's a spawner
            entity.take_damage(1)


class PoisonArrow(Arrow):
    def __init__(self, startpos, target, damage, knockback, safe,
                 chain=False, chainstack=0, growing=False):
        super().__init__(startpos, target, damage, knockback, safe,
                         chain, chainstack)
        self.tip_color = pygame.Color('green')

    def hit(self, entity, game):
        super().hit(entity, game)
        if hasattr(entity, 'effects') and entity.effects['poison'] < 15:
            entity.effects['poison'] = 15  # poison it
        elif not hasattr(entity, 'effects'):
            entity.take_damage(1)


class FlamingArrow(Arrow):
    def __init__(self, startpos, target, damage, knockback, safe,
                 chain=False, chainstack=0, growing=False):
        super().__init__(startpos, target, damage, knockback, safe,
                         chain, chainstack)
        self.tip_color = self.shaft_color = pygame.Color('red')

    def hit(self, entity, game):
        super().hit(entity, game)
        if hasattr(entity, 'effects') and entity.effects['fire'] < 25:
            entity.effects['fire'] = 25  # light it up!
        elif not hasattr(entity, 'effects'):
            entity.take_damage(1)


class ExplodingArrow(Arrow):
    def __init__(self, startpos, target, damage, knockback, safe,
                 chain=False, chainstack=0, growing=False):
        super().__init__(startpos, target, damage, knockback, safe,
                         chain, chainstack)
        self.tip_color = pygame.Color('red')
        self.shaft_color = pygame.Color('white')
        self.explodebox = pygame.Rect(self.rect.x - (self.d1 * 10),
                self.rect.y - (self.d2 * 10),
                int(self.dx * 5) + (self.d1 * 2) + (self.d1 * 20),
                int(self.dy * 5) + (self.d2 * 2) + (self.d2 * 20))

    def hit(self, entity, game):
        super().hit(entity, game)
        x = self.rect.x
        y = self.rect.y
        self.rect.x = self.x
        self.rect.y = self.y
        self.explodebox = pygame.Rect(self.rect.x - (self.d1 * 10),
                                      self.rect.y - (self.d2 * 10),
                                      int(self.dx * 5) + (self.d1 * 2) +
                                      (self.d1 * 20), int(self.dy * 5) +
                                      (self.d2 * 2) + (self.d2 * 20))
        rec = self.rect
        self.rect = self.explodebox
        for entity in game.enemies + game.helpfuls + [game.player]:
            if pygame.sprite.collide_rect(self, entity):
                if type(entity) in [dungeon_helpful.Golem,
                                    dungeon_helpful.Wolf]:
                    entity.take_damage(self, 8)
                else:
                    entity.take_damage(8)
                entity.knockback(self.knockback, self)
        self.rect = rec
        self.rect.x = x
        self.rect.y = y

    def destroy(self, game):
        super().destroy(game)
        self.explodebox.x = 10000  # change the explodebox as well
        self.explodebox.y = 10000

    def move_xy(self, x, y):  # move the explodebox along with it
        super().move_xy(x, y)
        self.explodebox.x += x
        self.explodebox.y += y


class ImplodingArrow(ExplodingArrow):
    def __init__(self, startpos, target, damage, knockback, safe,
                 chain=False, chainstack=0, growing=False):
        super().__init__(startpos, target, damage, knockback, safe,
                         chain, chainstack)
        self.tip_color = pygame.Color('white')
        self.shaft_color = pygame.Color('red')
        self.knockback *= -1


class SpeedWhenHurtArrow(Arrow):
    def __init__(self, startpos, target, damage, knockback, safe,
                 chain=False, chainstack=0, growing=False):
        super().__init__(startpos, target, damage, knockback, safe,
                         chain, chainstack)

    def hit(self, entity, game):
        super().hit(entity, game)
        if entity.hp <= 0 and game.player.effects['speed'] < 10:
            game.player.effects['speed'] = 10  # speed on kill


class Bolt(Arrow):
    def __init__(self, startpos, target, safe):
        super().__init__(startpos, target, 5, 40, safe, False, 0)
        self.tip_color = pygame.Color('dark green')
        self.shaft_color = pygame.Color('blue')

    def render(self, game):
        self.move_xy(self.dx, self.dy)

        self.draw(game)

        for entity in [game.player] + game.helpfuls:
            rec = entity.rect
            entity.rect = pygame.Rect(rec.x - 8, rec.y - 8,
                                      rec.width + 16, rec.height + 16)

            if pygame.sprite.collide_rect(entity, self) and entity !=self.safe:
                self.hit(entity, game)
                self.destroy(game)
                dungeon_settings.arrow_hit.play()

            entity.rect = rec

        if (self.rect.x < -100 or self.rect.x >game.screen.get_width() + 100 or
           self.rect.y < -100 or self.rect.y > game.screen.get_height() + 100):
            self.destroy(game)


import dungeon_helpful  # so circular imports are avoided, it must be down here
