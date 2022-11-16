import pygame
import math
import dungeon_util
import time
import random

class Helpful:
    def __init__(self, x, y):
        self.drect = pygame.Rect(x, y, 1, 1) #drect
        self.rect = pygame.Rect(x, y, 3, 3) #rect
        self.woff = 1 #width and height offsets
        self.hoff = 1
        self.going = None #which enemy to target
        self.speed = 1
        self.delaymove = 0
        self.delay_move = 20
        self.damage = 1
        self.knockbackd = 10
        self.delaydamage = 0
        self.delay_damage = 20
        self.hpmax = 20
        self.hp = self.hpmax
        self.armor = 0
        self.knockback_resistance = 0
        self.name = ''
        self.text = pygame.font.SysFont(self.name, 20).render(self.name, 1, pygame.Color('black'))
        self.color = pygame.Color('black')
        self.effects = {'speed': 0, 'slowness': 0, 'strength': 0, 'weakness': 0, 'resistance': 0, 'poison': 0, 'regeneration': 0, 'fire': 0}
        self.decreaseeffectslast = time.time() #all the normal entity attributes

    def render(self, game):
        self.draw(game)

        if time.time() - self.decreaseeffectslast >= 1: #decrease effect lengths
            self.decreaseeffectslast = time.time()
            for effect in self.effects.keys():
                if self.effects[effect] > 0:
                    self.effects[effect] -= 1
            if self.effects['poison'] > 0 and random.randint(0, 2) == 0 and self.hp > 1:
                self.hp -= 1
            if self.effects['regeneration'] > 0 and random.randint(0, 2) == 0:
                self.hp += 1
            if self.effects['fire'] > 0 and random.randint(0, 1) == 0:
                self.hp -= 1
                
        for effect in self.effects.keys(): #particles
            if self.effects[effect] > 0 and effect != 'fire':
                particle.particle(effect, self.rect.x, self.rect.x + self.rect.width, self.rect.y, self.rect.y + self.rect.height, game)
                
        if (not self.going) or (self.going and self.going.dead): #figure out the enemy to go after
            self.going = dungeon_util.get_nearest_target(game, self, False)
            if self.going == None:
                xdiff = random.choice([self.speed, 0, 0, -self.speed])
                self.rect.x += xdiff
                ydiff = random.choice([self.speed, 0, 0, -self.speed])
                self.rect.y += ydiff
                if self.hp <= 0:
                    self.rect.x = 1000000
                    self.rect.y = 1000000
                    game.helpfuls.remove(self)
                if self.hp > self.hpmax:
                    self.hp = self.hpmax
                self.updatepos()
                return

        self.delaymove += 1 #move
        if self.delaymove >= self.delay_move:
            self.delaymove = 0
            if self.going.rect.x < self.rect.x:
                self.rect.x -= self.speed
                if self.effects['slowness'] > 0: self.rect.x += 1
            else:
                self.rect.x += self.speed
                if self.effects['slowness'] > 0: self.rect.x -= 1
            if self.going.rect.y < self.rect.y:
                self.rect.y -= self.speed
                if self.effects['slowness'] > 0: self.rect.y += 1
            else:
                self.rect.y += self.speed
                if self.effects['slowness'] > 0: self.rect.y -= 1

            #self.hitbox.update(self.rect.x, self.rect.y, self.reach)

        self.delaydamage += 1 #hit the enemy
        if self.delaydamage >= self.delay_damage:
            self.delaydamage = 0
            if self.rect.colliderect(self.going.hitbox):
                self.attack(game)

        if self.hp <= 0: #die if low hp, or don't go over the max
            self.rect.x = 1000000
            self.rect.y = 1000000
            game.helpfuls.remove(self)
        if self.hp > self.hpmax:
            self.hp = self.hpmax
        self.updatepos() #update the position

    def attack(self, game):
        self.going.take_damage(self.damage) #attack the enemy
        self.going.knockback(self.knockbackd, self)

    def take_damage(self, src, damage): #take damage
        damage -= self.armor
        damage += random.randint(-1, 1)
        self.hp -= damage
        if hasattr(src, 'take_damage'): #hit back! helpfuls can really do this
            src.take_damage(self.damage)
        if hasattr(src, 'knockback') and type(src.knockback) not in [int, float]:
            src.knockback(self.knockbackd, self)
        if hasattr(src, 'hp'): #change the target to whatever hit them
            self.going = src

    def knockback(self, knockback, player): #take knockback
        if knockback > 0:
            knockback -= self.knockback_resistance
            knockback += random.randint(-5, 5)
            if knockback < 0: return
            for knock in range(int(knockback)):
                if player.rect.x > self.rect.x: self.rect.x -= 1
                if player.rect.x < self.rect.x: self.rect.x += 1
                if player.rect.y < self.rect.y: self.rect.y += 1
                if player.rect.y > self.rect.y: self.rect.y -= 1

        elif knockback < 0:
            knockback += self.knockback_resistance
            knockback += random.randint(-5, 5)
            if knockback > 0: return
            for knock in range(int(abs(knockback))):
                if player.rect.x > self.rect.x: self.rect.x += 1
                if player.rect.x < self.rect.x: self.rect.x -= 1
                if player.rect.y < self.rect.y: self.rect.y -= 1
                if player.rect.y > self.rect.y: self.rect.y += 1
        self.updatepos()

    def updatepos(self): #update the position
        self.drect.x = self.rect.x + self.woff
        self.drect.y = self.rect.y + self.hoff

    def draw(self, game):
        # use super().draw(game) and then the real thing draws
        health_rect = pygame.Rect(self.drect.x - (self.hpmax // 2), self.drect.y - 5, int(self.hp * 2), 8)
        pygame.draw.rect(game.screen, pygame.Color('red'), health_rect) #hp bar
        game.screen.blit(self.text, (self.drect.x - 5, self.drect.y - 20)) #enemy name

        if self.effects['fire'] > 0: #draw flames
            pygame.draw.line(game.screen, pygame.Color('red'), (self.drect.x + 10, self.drect.y + 24), (self.drect.x + 7, self.drect.y + 5), 4)
            pygame.draw.line(game.screen, pygame.Color('red'), (self.drect.x + 20, self.drect.y + 27), (self.drect.x + 23, self.drect.y + 3), 4)
            pygame.draw.line(game.screen, pygame.Color('red'), (self.drect.x + 14, self.drect.y + 26), (self.drect.x + 16, self.drect.y + 7), 4)

        if self.speed == 0: #ice block
            pygame.draw.rect(game.screen, pygame.Color('light blue'), pygame.Rect(self.drect.x + 2, self.drect.y + 2, self.drect.width - 4, self.drect.height - 4))

class Golem(Helpful): #iron golem
    def __init__(self, x, y):
        super().__init__(x, y)
        self.drect = pygame.Rect(x, y, 50, 70)
        self.rect = pygame.Rect(x - 20, y - 20, 90, 90)
        self.woff = 20
        self.hoff = 20
        self.name = 'Iron Golem'
        self.text = pygame.font.SysFont(self.name, 20).render(self.name, 1, pygame.Color('black'))
        self.damage = 18
        self.hpmax = 100
        self.hp = self.hpmax
        self.knockback_resistance = 20
        self.knockbackd = 80
        self.delay_move = 15
        self.delay_damage = 25
        self.speed = 3
        self.color = pygame.Color(250, 250, 250, 255)

    def draw(self, game):
        super().draw(game)
        pygame.draw.rect(game.screen, self.color, self.drect)
        pygame.draw.circle(game.screen, self.color, (self.drect.x + 25, self.drect.y - 10), 10)
        pygame.draw.line(game.screen, self.color, (self.drect.x - 20, self.drect.y + 60), (self.drect.x, self.drect.y + 10), 10)
        pygame.draw.line(game.screen, self.color, (self.drect.x + 70, self.drect.y + 60), (self.drect.x + 50, self.drect.y + 10), 10)

class Wolf(Helpful): #wolf
    def __init__(self, x, y):
        super().__init__(x, y)
        self.drect = pygame.Rect(x, y, 20, 10)
        self.rect = pygame.Rect(x - 10, y - 5, 40, 20)
        self.woff = 10
        self.hoff = 5
        self.name = 'Wolf'
        self.text = pygame.font.SysFont(self.name, 20).render(self.name, 1, pygame.Color('black'))
        self.damage = 2
        self.hpmax = 10
        self.hp = self.hpmax
        self.knockbackd = 20
        self.delay_move = 5
        self.delay_damage = 10
        self.speed = 4
        self.color = pygame.Color(250, 250, 250, 255)

    def draw(self, game):
        super().draw(game)
        pygame.draw.rect(game.screen, self.color, self.drect)
        pygame.draw.circle(game.screen, self.color, (self.drect.x - 5, self.drect.y), 5)
        pygame.draw.line(game.screen, self.color, (self.drect.x + 20, self.drect.y + 2), (self.drect.x + 30, self.drect.y + 5), 2)

    def attack(self, game):
        super().attack(game)
        self.hp += 1 #heal from attacking

class Bat(Helpful): #bat
    def __init__(self, x, y):
        super().__init__(x, y)
        self.drect = pygame.Rect(x, y, 5, 5)
        self.rect = pygame.Rect(x, y, 5, 5)
        self.woff = 0
        self.hoff = 0
        self.name = 'Bat'
        self.text = pygame.font.SysFont(self.name, 20).render(self.name, 1, pygame.Color('black'))
        self.damage = 0
        self.hpmax = 1
        self.hp = self.hpmax
        self.knockbackd = 5
        self.delay_move = 3
        self.delay_damage = float('inf')
        self.speed = 2
        self.color = pygame.Color(15, 15, 15, 255)
        self._nowdie = False

    def draw(self, game):
        super().draw(game)
        pygame.draw.rect(game.screen, self.color, self.drect)

    def render(self, game):
        self.draw(game)

        if time.time() - self.decreaseeffectslast >= 1:
            self.decreaseeffectslast = time.time()
            for effect in self.effects.keys():
                if self.effects[effect] > 0:
                    self.effects[effect] -= 1
                
        for effect in self.effects.keys():
            if self.effects[effect] > 0 and effect != 'fire':
                particle.particle(effect, self.rect.x, self.rect.x + 30, self.rect.y, self.rect.y + 35, game)
                
        if (not self.going) or (self.going and self.going.dead):
            self.going = dungeon_util.get_nearest_target(game, self, False)
            if self.going == None:
                xdiff = random.choice([self.speed, 0, 0, -self.speed])
                self.rect.x += xdiff
                ydiff = random.choice([self.speed, 0, 0, -self.speed])
                self.rect.y += ydiff
                if self.hp <= 0: #can't die normally, but only if player is not wearing his armor
                    if self._nowdie:
                        game.helpfuls.remove(self)
                        self.rect.x = 1000000
                        self.rect.y = 1000000
                    else:
                        self.hp = 1
                if self.hp > self.hpmax:
                    self.hp = self.hpmax
                self.updatepos()
                return

        self.delaymove += 1
        if self.delaymove >= self.delay_move:
            self.delaymove = 0
            if self.going.rect.x < self.rect.x:
                self.rect.x -= self.speed
                if self.effects['slowness'] > 0: self.rect.x += 1
            else:
                self.rect.x += self.speed
                if self.effects['slowness'] > 0: self.rect.x -= 1
            if self.going.rect.y < self.rect.y:
                self.rect.y -= self.speed
                if self.effects['slowness'] > 0: self.rect.y += 1
            else:
                self.rect.y += self.speed
                if self.effects['slowness'] > 0: self.rect.y -= 1

            #self.hitbox.update(self.rect.x, self.rect.y, self.reach)

        self.delaydamage += 1
        if self.delaydamage >= self.delay_damage:
            self.delaydamage = 0
            if self.rect.colliderect(self.going.hitbox):
                self.attack(game)

        if self.hp <= 0:
            if self._nowdie:
                game.helpfuls.remove(self)
                self.rect.x = 1000000
                self.rect.y = 1000000
            else:
                self.hp = 1
        if self.hp > self.hpmax:
            self.hp = self.hpmax
        self.updatepos()

    def attack(self, game):
        pass #does no damage though

from dungeon_misc import particle #gotta be at end to prevent circular import
