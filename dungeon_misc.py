import pygame
import random
import time
import math
import dungeon_arrows
from threading import Thread
import dungeon_util #has a function to choose the nearest enemy/helpful from the list

#particle mappings, type -> particle color
_types = {'strength': pygame.Color('purple'), 'slowness': pygame.Color('dark grey'), 'speed': pygame.Color('light blue'), 'weakness': pygame.Color('grey'), 'poison': pygame.Color('green'), 'resistance': pygame.Color('dark red'), 'regeneration': pygame.Color('pink')}

class _particle: #one particle
    def __init__(self, _type):
        self.x = 0
        self.y = 0
        self._type = _type
        self.color = _types[_type]

    def render(self, game, x, y):
        self.x = x
        self.y = y
        self.draw(game)

    def draw(self, game):
        pygame.draw.circle(game.screen, self.color, (self.x, self.y), 1)

class _particlehandler: #draws 3 particles of a certain type
    def __init__(self, _type):
        self.particle1 = _particle(_type)
        self.particle2 = _particle(_type)
        self.particle3 = _particle(_type)

    def drawparts(self, xmin, xmax, ymin, ymax, game):
        self.particle1.render(game, random.randint(min(xmin, xmax), max(xmin, xmax)), random.randint(min(ymin, ymax), max(ymin, ymax)))
        self.particle2.render(game, random.randint(min(xmin, xmax), max(xmin, xmax)), random.randint(min(ymin, ymax), max(ymin, ymax)))
        self.particle3.render(game, random.randint(min(xmin, xmax), max(xmin, xmax)), random.randint(min(ymin, ymax), max(ymin, ymax)))


class Particles: #has a _particlehandler for each type and mappings to them
    def __init__(self):
        self.strength = _particlehandler('strength')
        self.slowness = _particlehandler('slowness')
        self.speed = _particlehandler('speed')
        self.weakness = _particlehandler('weakness')
        self.poison = _particlehandler('poison')
        self.regeneration = _particlehandler('regeneration')
        self.resistance = _particlehandler('resistance')
        self.particles = {'strength': self.strength, 'slowness': self.slowness, 'speed': self.speed, 'weakness': self.weakness, 'poison': self.poison, 'regeneration': self.regeneration, 'resistance': self.resistance}

    def particle(self, p, xmin, xmax, ymin, ymax, game):
        if p not in self.particles.keys():
            print(f'Particle for effect {p} does not exist') #TODO: replace with logger.critical
            return
        self.particles[p].drawparts(xmin, xmax, ymin, ymax, game)

particle = Particles()

"""class ThrowingPotion:
    def __init__(self, x, y, xvel, yvel, type):
        self.x = x
        self.y = y
        self.xvel = xvel
        self.yvel = yvel
        self.type = type
        self.isfalling = True
        self.xdone = False
        self.ydone = False

    def render(self, game):
        self.draw(game)
        if self.xdone and self.ydone:
            pass
        else:
            self.x += self.xvel
            self.y += self.yvel
            if self.xvel > 0: self.xvel -= 0.1
            elif self.xvel < 0: self.xvel += 0.1
            elif not self.xdone: self.xdone = True
            if self.yvel > 0: self.yvel -= 0.1
            elif self.yvel < 0: self.yvel += 0.1
            elif not self.ydone: self.ydone = True

    def draw(self, game):
        if not self.isfalling:
            particle.particle(self.type, round(self.x) - 20, round(self.y) - 20, round(self.x) + 20, round(self.y) + 20, game)
        else:
            pygame.draw.circle(game.screen, pygame.Color('white'), (round(self.x), round(self.y)), 4)
            pygame.draw.circle(game.screen, _types[self.type], (round(self.x), round(self.y)), 3""" #original idea, abandoned halfway through

class EmeraldPot: #lol
    def __init__(self, x, y, data={}):
        self.x = x
        self.y = y
        self._die = False
        if '_die' in data:
            self._die = data['_die']
        
    def render(self, game):
        if self._die:
            game.other.remove(self)
            return
        self.draw(game)

    def hit(self, player):
        self.x = 1000000
        self.y = 1000000
        self._die = True
        player.emeralds += random.randint(15, 25) #die and give emeralds

    def draw(self, game):
        pygame.draw.rect(game.screen, pygame.Color('turquoise'), pygame.Rect(self.x, self.y + 15, 15, 5))
        pygame.draw.rect(game.screen, pygame.Color('turquoise'), pygame.Rect(self.x + 2, self.y + 9, 11, 6))
        pygame.draw.rect(game.screen, pygame.Color('turquoise'), pygame.Rect(self.x + 5, self.y, 5, 9)) #wow... turquoise is an actual pygame.Color?

    def get_save_data(self):
        return {'_die': self._die, 'x': self.x, 'y': self.y} #needs to know whether or not it should die, and its position

class ThrowingPotion(dungeon_arrows.Arrow):
    def __init__(self, startpos, target, safe, effect):
        super().__init__(startpos, target, 0, 0, safe)
        self.effect = effect
        self.col = _types[self.effect]
        self.xm = 0
        self.ym = 0
        self._x_ = 0
        self._y_ = 0

    def move_xy(self, x, y): #needs to know how far it has gone
        super().move_xy(x, y)
        self.xm += 1
        self.ym += 1
        if self.xm > 100 and self.ym > 100:
            self._x_ = self.rect.x
            self._y_ = self.rect.y
            self.rect.x = 1000000
            self.rect.y = 1000000

    def destroy(self, game):
        super().destroy(game)
        game.other.append(ThrownPotion((self._x_ if self._x_ else self.rect.x), (self._y_ if self._y_ else self.rect.y), self.effect)) #make a potion cloud when it breaks

    def draw(self, game):
        pygame.draw.circle(game.screen, pygame.Color('white'), (self.x, self.y), 4)
        pygame.draw.circle(game.screen, self.col, (self.x, self.y), 3)

class ConjuredProjectile(dungeon_arrows.Arrow): #arrow-type projectile made by Conjured Slimes (homing missile)
    def __init__(self, x, y):
        super().__init__((x, y), (0, 0), 3, 10, None)
        self.d1 = 0
        self.d2 = 0

    def render(self, game):
        #self.move_xy(self.dx, self.dy)
        target = dungeon_util.get_nearest_target(game, self, True)

        if target.rect.x < self.x: #home in!
            self.move_xy(-3, 0)
        elif target.rect.x > self.x:
            self.move_xy(3, 0)
        if target.rect.y < self.y:
            self.move_xy(0, -3)
        elif target.rect.y > self.y:
            self.move_xy(0, 3)

        self.draw(game)
        
        for entity in game.helpfuls + game.enemies + game.spawners + [game.player]: #see if it hit anything
            #if target.rect.y in range(self.rect.y - 20, self.rect.y + 20) and target.rect.x in range(self.rect.x - 20, self.rect.x + 20):
            if target.rect.y - 20 < self.y < target.rect.y + 20 and target.rect.x - 20 < self.x < target.rect.x + 20:
                self.hit(entity, game)
                self.destroy(game)

        if self.growing:
            self.damage += 0.04 #wait, they shouldn't be able to grow..?

        if self.rect.x < -100 or self.rect.x > game.screen.get_width() + 100 or self.rect.y < -100 or self.rect.y > game.screen.get_height() + 100:
            self.destroy(game)

    def draw(self, game):
        pygame.draw.circle(game.screen, pygame.Color('purple'), (self.x, self.y), 5) #just a purple lump

class ThrownPotion: #potion cloud
    def __init__(self, x, y, effect):
        self.x = x
        self.y = y
        if type(effect) == dict:
            self.effect = effect['effect']
            self.t = time.time() - effect['howlong']
        else:
            self.effect = effect
            self.t = time.time()

    def render(self, game):
        self.draw(game)
        for i in game.helpfuls + game.enemies + [game.player]:
            if i.rect.colliderect(pygame.Rect(self.x - 10, self.y - 10, 20, 20)):
                if i.effects[self.effect] < 10:
                    i.effects[self.effect] = 10 #give effect for 10 seconds if an entity gets in it
        if time.time() - self.t >= 10: #die after 10 seconds
            self.x = 1000000
            self.y = 1000000
            game.other.remove(self)

    def draw(self, game):
        particle.particle(self.effect, self.x - 10, self.y - 10, self.x + 10, self.y + 10, game) #3 times as many particles as normal
        particle.particle(self.effect, self.x - 10, self.y - 10, self.x + 10, self.y + 10, game)
        particle.particle(self.effect, self.x - 10, self.y - 10, self.x + 10, self.y + 10, game)

    def get_save_data(self):
        return {'x': self.x, 'y': self.y, 'effect': self.effect, 'howlong': time.time() - self.t}

class PoisonCloud(ThrownPotion): #special thrown potion that has a safe object and is automatically poison
    def __init__(self, x, y, safe):
        super().__init__(x, y, 'poison')
        if type(safe) == dict:
            self.safe = None #you stop being safe when you quit!
        else:
            self.safe = safe

    def render(self, game):
        self.draw(game)
        for i in game.helpfuls + game.enemies + [game.player]:
            if i != self.safe and i.rect.colliderect(pygame.Rect(self.x - 10, self.y - 10, 20, 20)):
                if i.effects[self.effect] < 10:
                    i.effects[self.effect] = 10
        if time.time() - self.t >= 10:
            self.x = 1000000
            self.y = 1000000
            game.other.remove(self)

class TNT:
    def __init__(self, x, y, data={}): #TNT!
        self.x = x
        self.y = y
        self.fuse = 5
        self.red = True
        self.decreasefuselast = time.time()
        if 'fuse' in data: self.fuse = data['fuse']
        if 'red' in data: self.red = data['red']
        if 'howlong' in data: self.decreasefuselast - data['howlong']

    def render(self, game):
        self.draw(game)
        if time.time() - self.decreasefuselast >= 1: #decrease the fuse
            self.fuse -= 1
            self.red = not self.red
            self.decreasefuselast = time.time()
        if self.fuse <= 0:
            Thread(target=self.explode, args=(game,)).start() #TODO: improve this (it is weird)
            if self in game.other:
                game.other.remove(self)

    def draw(self, game):
        pygame.draw.rect(game.screen, pygame.Color('red' if self.red else 'white'), pygame.Rect(self.x - 5, self.y - 5, 15, 15))
        if self.red:
            pygame.draw.rect(game.screen, pygame.Color('white'), pygame.Rect(self.x - 5, self.y, 15, 5))

    def explode(*args): #blow up da tnt, man
        self, game = args
        collision_rect = pygame.Rect(self.x - 45*2, self.y - 45*2, 95*2, 95*2)
        pygame.draw.rect(game.screen, pygame.Color('yellow'), collision_rect)
        pygame.draw.rect(game.screen, pygame.Color('orange'), pygame.Rect(self.x - 25*2, self.y - 25*2, 55*2, 55*2))
        pygame.draw.rect(game.screen, pygame.Color('red'), pygame.Rect(self.x - 5*2, self.y - 5*2, 15*2, 15*2))
        pygame.display.update()
        time.sleep(2)
        self.rect = pygame.Rect(self.x, self.y, 1, 1)
        for entity in game.enemies + game.helpfuls + game.spawners + [game.player]:
            if collision_rect.colliderect(entity.rect):
                if type(entity) in [dungeon_helpful.Golem, dungeon_helpful.Wolf, dungeon_helpful.Bat]: entity.take_damage(self, 15)
                else: entity.take_damage(15)
                entity.knockback(20, self)

    def get_save_data(self):
        return {'x': self.x, 'y': self.y, 'fuse': self.fuse, 'red': self.red, 'howlong': time.time() - self.decreasefuselast} #save the fuse, howlong since fuse was decrease, and color

class EvokerSpikes:
    def __init__(self, x, y, data={}):
        self.x = x
        self.y = y
        self.rect = type('rect', (), {'x': self.x, 'y': self.y, 'move': self.move}) #needs a rect
        self.getridof = time.time()
        self.delayd = 0
        self.delayD = 20
        if 'howlong' in data:
            self.getridof -= data['howlong']
            self.delayd = data['delayd']

    def render(self, game):
        self.draw(game)
        if time.time() - self.getridof > 2:
            if self in game.other:
                game.other.remove(self) #die after 2 seconds
        self.delayd += 1
        if self.delayd >= self.delayD: #do 1 damage to player and helpfuls
            if game.player.rect.colliderect(pygame.Rect(self.x - 5, self.y, 20, 15)):
                game.player.hp -= 1
            for entity in game.helpfuls:
                if entity.rect.colliderect(pygame.Rect(self.x - 5, self.y, 20, 15)):
                    entity.hp -= 1

    def draw(self, game):
        pygame.draw.lines(game.screen, pygame.Color('black'), True, [(self.x - 5, self.y + 15), (self.x - 5, self.y), (self.x, self.y + 5), (self.x + 5, self.y), (self.x + 10, self.y + 5), (self.x + 15, self.y), (self.x + 15, self.y + 15)])

    def move(self, x=0, y=0): #move it
        self.x += x
        self.y += y

    def get_save_data(self):
        return {'x': self.x, 'y': self.y, 'howlong': time.time() - self.getridof, 'delayd': self.delayd} #save howlong it has been and what its damage delay is

class WraithFlames: #fire made by a wraith
    def __init__(self, x, y, data={}):
        self.x = x
        self.y = y
        self.rect = type('rect', (), {'x': self.x, 'y': self.y, 'move': self.move})
        self.getridof = time.time()
        self.col = pygame.Color('blue')
        self.delayd = 0
        self.delayD = 20
        if 'howlong' in data:
            self.getridof -= data['howlong']
            self.delayd = data['delayd']

    def render(self, game):
        self.draw(game)
        if time.time() - self.getridof > 8:
            if self in game.other:
                game.other.remove(self) #die after 8 seconds
        self.delayd += 1
        if self.delayd >= self.delayD:
            self.delayd = 0
            for entity in game.enemies:
                if entity.rect.colliderect(pygame.Rect(self.x, self.y, 20, 20)):
                    if entity.maintype == 'wraith': #wraiths avoid their fires
                        entity.teleport_away()
                    else:
                        entity.hp -= 1 #hurt them, light them on fire
                        if entity.effects['fire'] < 10:
                            entity.effects['fire'] = 10
            for entity in game.helpfuls: #same thing for helpfuls and the player
                if entity.rect.colliderect(pygame.Rect(self.x, self.y, 20, 20)):
                    entity.hp -= 1
                    if entity.effects['fire'] < 10:
                        entity.effects['fire'] = 10
            if game.player.rect.colliderect(pygame.Rect(self.x, self.y, 20, 20)):
                game.player.hp -= 1
                if game.player.effects['fire'] < 10:
                    game.player.effects['fire'] = 10

    def draw(self, game): #draw flames
        pygame.draw.line(game.screen, self.col, (self.x, self.y), (self.x + 5, self.y + 19), 3)
        pygame.draw.line(game.screen, self.col, (self.x + 6, self.y + 1), (self.x + 9, self.y + 18), 3)
        pygame.draw.line(game.screen, self.col, (self.x + 14, self.y + 3), (self.x + 13, self.y + 20), 3)
        pygame.draw.line(game.screen, self.col, (self.x + 19, self.y + 2), (self.x + 18, self.y + 19), 3)

    def move(self, x=0, y=0):
        self.x += x
        self.y += y

    def move_xy(self, x, y):
        self.move(x, y)

    def get_save_data(self):
        return {'x': self.x, 'y': self.y, 'howlong': time.time() - self.getridof, 'delayd': self.delayd} #save howlong it has been and the delay between its damage

class GeomancerColumn: #geomancer column
    def __init__(self, x, y, data={}, *, explode=False):
        self.x = x
        self.y = y
        self.doesexplode = explode #whether or not it is exploding
        self.rect = pygame.Rect(self.x, self.y, 100, 100)
        self.left = pygame.Rect(self.x, self.y, 10, 100)
        self.right = pygame.Rect(self.x + 90, self.y, 10, 100)
        self.top = pygame.Rect(self.x, self.y, 100, 10)
        self.bottom = pygame.Rect(self.x + 90, self.y, 100, 10)
        self.xrect = True
        self.getridof = time.time()
        if 'howlong' in data: self.getridof -= data['howlong']
        if 'doesexplode' in data: self.doesexplode = data['doesexplode']
        if 'x' in data:
            self.x = x
            self.rect.x = x
            self.left.x = x
            self.right.x = x + 90
            self.top.x = x
            self.bottom.x = x + 90
        if 'y' in data:
            self.y = y
            self.rect.y = y
            self.left.y = y
            self.right.y = y
            self.top.y = y
            self.bottom.y = y

    def get_save_data(self):
        return {'x': self.x, 'y': self.y, 'howlong': time.time() - self.getridof, 'doesexplode': self.doesexplode} #howlong it has been, and whether or not it explodes

    def render(self, game):
        self.draw(game)
        if time.time() - self.getridof > 10:
            if self in game.other:
                game.other.remove(self)
        if game.player.rect.colliderect(self.left): #don't let things pass it
            game.player.rect.x -= 10
        elif game.player.rect.colliderect(self.right):
            game.player.rect.x += 10
        elif game.player.rect.colliderect(self.bottom):
            game.player.rect.y += 10
        elif game.player.rect.colliderect(self.top):
            game.player.rect.y -= 10
        for enemy in game.enemies:
            if enemy.rect.colliderect(self.left):
                enemy.rect.x -= 10
            elif enemy.rect.colliderect(self.right):
                enemy.rect.x += 10
            elif enemy.rect.colliderect(self.top):
                enemy.rect.y -= 10
            elif enemy.rect.colliderect(self.bottom):
                enemy.rect.y += 10
        for helpful in game.helpfuls:
            if helpful.rect.colliderect(self.left):
                helpful.rect.x -= 10
            elif helpful.rect.colliderect(self.right):
                helpful.rect.x += 10
            elif helpful.rect.colliderect(self.top):
                helpful.rect.y -= 10
            elif helpful.rect.colliderect(self.bottom):
                helpful.rect.y += 10
        rem = []
        for arrow in game.arrows: #destroy arrows that hit it
            if not issubclass(type(arrow), dungeon_arrows.Arrow): continue
            if arrow.rect.colliderect(self.rect) or arrow.xrect.colliderect(self.rect):
                rem.append(arrow)
        if rem:
            for arrow in rem:
                game.arrows.remove(arrow)
        if self.doesexplode and time.time() - self.getridof > 3:
            if self in game.other:
                game.other.remove(self)
            Thread(target=self.explode, args=(game,)).start() #TODO: tidy up (like tnt)

    def draw(self, game):
        pygame.draw.rect(game.screen, pygame.Color('dark grey' if not self.doesexplode else 'light grey'), self.rect) #draw dark grey if it does not explode, otherwise light grey

    def explode(*args): #blow up
        self, game = args
        collision_rect = pygame.Rect(self.x - 45*2, self.y - 45*2, 95*2, 95*2)
        pygame.draw.rect(game.screen, pygame.Color('yellow'), collision_rect)
        pygame.draw.rect(game.screen, pygame.Color('orange'), pygame.Rect(self.x - 25*2, self.y - 25*2, 55*2, 55*2))
        pygame.draw.rect(game.screen, pygame.Color('red'), pygame.Rect(self.x - 5*2, self.y - 5*2, 15*2, 15*2))
        pygame.display.update()
        time.sleep(1)
        self.rect = pygame.Rect(self.x, self.y, 1, 1)
        for entity in game.enemies + game.helpfuls + game.spawners + [game.player]: #blow it up
            if collision_rect.colliderect(entity.rect):
                if type(entity) in [dungeon_helpful.Golem, dungeon_helpful.Wolf, dungeon_helpful.Bat]: entity.take_damage(self, 15) #since helpfuls need source of damage
                else: entity.take_damage(15)
                entity.knockback(20, self)

    def move_xy(self, x=0, y=0): #move the column
        self.rect.x += x
        self.rect.y += y
        self.top.x += x
        self.top.y += y
        self.bottom.x += x
        self.bottom.y += y
        self.right.x += x
        self.right.y += y
        self.left.x += x
        self.left.y += y

import dungeon_helpful #gotta be at end to prevent circular import
