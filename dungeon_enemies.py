import pygame
import random
import dungeon_arrows
import dungeon_settings
import dungeon_weapons
import time
import threading
from dungeon_misc import particle
import dungeon_misc
import math
import dungeon_util

pygame.init()


class HitBox:
    def __init__(self, x, y):
        self.rect = pygame.rect.Rect(x, y, 1, 1)
        
    def update(self, x, y, reach):
        self.rect = pygame.Rect(x - reach, y - reach, reach * 2, reach * 2)


class BaseEnemy:
    def __init__(self, x, y):
        self.maintype = ''
        self.secondtype = ''
        
        self.dx = self.dy = 0
        self.rect = pygame.rect.Rect((x, y, 30, 35))
        
        self.color_body = pygame.Color('light blue')
        self.color_head = pygame.Color('green')
        self.color_arm = pygame.Color('green')
        
        self.damage = 0
        self.delay_damage = 10
        self.delay_move = 17
        self.delaydamage = 0
        self.delaymove = 0
        self.hpmax = 20
        self.hp = self.hpmax
        
        self.name = ''
        self.text = pygame.font.SysFont(self.name, 20).render(
                    self.name, 1, pygame.Color('black'))
        
        self.xp_drop = 0.0
        self.knockback_resistance = 0
        self.armor = 0.0
        
        self.effects = {'speed': 0, 'slowness': 0, 'strength': 0,
                        'weakness': 0, 'resistance': 0, 'poison': 0,
                        'regeneration': 0, 'fire': 0}
        
        self.decreaseeffectslast = time.time()
        
        self.speed = 2
        
        self.hitbox = HitBox(x, y)
        self.reach = 15
        
        self.dead = False
        self.mode = 'ice'

    def get_target(self, game):
        return dungeon_util.get_nearest_target(game, self, True)

    def render(self, game):
        player = self.get_target(game)
        self.delaymove += 1
        if self.delaymove >= self.delay_move:
            self.delaymove = 0
            if player.rect.x < self.rect.x:
                self.rect.x -= self.speed
                if self.effects['slowness'] > 0:
                    self.rect.x += 1
            else:
                self.rect.x += self.speed
                if self.effects['slowness'] > 0:
                    self.rect.x -= 1
            if player.rect.y < self.rect.y:
                self.rect.y -= self.speed
                if self.effects['slowness'] > 0:
                    self.rect.y += 1
            else:
                self.rect.y += self.speed
                if self.effects['slowness'] > 0:
                    self.rect.y -= 1

            self.hitbox.update(self.rect.x, self.rect.y, self.reach)

        if time.time() - self.decreaseeffectslast >= 1:
            self.decreaseeffectslast = time.time()
            for effect in self.effects.keys():
                if self.effects[effect] > 0:
                    self.effects[effect] -= 1
            if self.effects['poison'] > 0 and random.randint(0, 2) == 0 \
               and self.hp > 1:
                self.hp -= 1
            if self.effects['regeneration'] > 0 and random.randint(0, 2) == 0:
                self.hp += 1
            if self.effects['fire'] > 0 and random.randint(0, 1) == 0:
                self.hp -= 1
                
        for effect in self.effects.keys():
            if self.effects[effect] > 0 and effect != 'fire':
                particle.particle(effect, self.rect.x, self.rect.x + 30,
                                  self.rect.y, self.rect.y + 35, game)

        self.draw(game)

        if self.hp > self.hpmax:
            self.hp = self.hpmax

        if self.hp <= 0:
            game.enemies.remove(self)
            for i in game.enemies:
                if type(i) == TheCauldron:
                    if dungeon_util.distance_between(i.rect.x, i.rect.y,
                                                     self.rect.y,
                                                     self.rect.y) < 300:
                        i.hp += 3
                        break
            self.rect.x = 10000
            self.rect.y = 10000
            game.player.get_xp(self.xp_drop)
            game.player.kill()
            self.dead = True

        self.delaydamage += 1
        if self.delaydamage >= self.delay_damage and self.speed > 0:
            if pygame.sprite.collide_rect(player, self.hitbox):
                if player == game.player:
                    player.take_damage(self.damage)
                    player.armor_use(self, game)
                else:
                    player.take_damage(self, self.damage)
            self.delaydamage = 0

    def draw(self, game):
        pygame.draw.rect(game.screen, self.color_body,
                         pygame.Rect(self.rect.x + 10,
                                     self.rect.y + 15, 10, 15)
                         )  # body
        pygame.draw.circle(game.screen, self.color_head,
                           (self.rect.x + 15, self.rect.y + 10), 5)  # head
        pygame.draw.line(game.screen, self.color_arm,
                         (self.rect.x + 10, self.rect.y + 15),
                         (self.rect.x + 5, self.rect.y + 20), 3)  # arm
        pygame.draw.line(game.screen, self.color_arm,
                         (self.rect.x + 20, self.rect.y + 15),
                         (self.rect.x + 25, self.rect.y + 20), 3)  # arm
        health_rect = pygame.Rect(self.rect.x - (self.hpmax // 2),
                                  self.rect.y - 5, int(self.hp * 2), 8)
        pygame.draw.rect(game.screen, pygame.Color('red'), health_rect)
        game.screen.blit(self.text, (self.rect.x - 5, self.rect.y - 20))

        if self.effects['fire'] > 0:
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 10, self.rect.y + 24),
                             (self.rect.x + 7, self.rect.y + 5), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 20, self.rect.y + 27),
                             (self.rect.x + 23, self.rect.y + 3), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 14, self.rect.y + 26),
                             (self.rect.x + 16, self.rect.y + 7), 4)

        if self.speed == 0:
            if self.mode == 'ice':
                pygame.draw.rect(game.screen, pygame.Color('light blue'),
                                 pygame.Rect(self.rect.x + 2, self.rect.y + 2,
                                 self.rect.width - 4, self.rect.height - 4))
            elif self.mode == 'chains':
                for y in range(self.rect.y, self.rect.y +self.rect.height, 10):
                    pygame.draw.line(game.screen, pygame.Color('grey'),
                                     (self.rect.x, y),
                                     (self.rect.x + self.rect.width, y), 3)

    def give_unmoving(self, seconds, mode='ice'):
        temp = self.speed
        self.speed = 0
        self.mode = mode
        
        def temp_func(seconds, enemy, speed):
            time.sleep(seconds)
            enemy.speed = speed
            
        threading.Thread(target=temp_func, args=(seconds, self, temp)).start()

    def knockback(self, knockback, player):
        if knockback > 0:
            knockback -= self.knockback_resistance
            knockback += random.randint(-5, 5)
            for knock in range(int(knockback)):
                if player.rect.x > self.rect.x:
                    self.rect.x -= 1
                if player.rect.x < self.rect.x:
                    self.rect.x += 1
                if player.rect.y < self.rect.y:
                    self.rect.y += 1
                if player.rect.y > self.rect.y:
                    self.rect.y -= 1

        elif knockback < 0:
            knockback += self.knockback_resistance
            knockback += random.randint(-5, 5)
            for knock in range(int(abs(knockback))):
                if player.rect.x > self.rect.x:
                    self.rect.x += 1
                if player.rect.x < self.rect.x:
                    self.rect.x -= 1
                if player.rect.y < self.rect.y:
                    self.rect.y -= 1
                if player.rect.y > self.rect.y:
                    self.rect.y += 1

    def take_damage(self, damage):
        damage -= self.armor
        damage += random.randint(-1, 1)
        if damage < 0:
            damage = 0
        self.hp -= damage


class BaseSpawner:
    mob = None
    
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.col = pygame.Color('black')
        self.name = 'Spawner'
        self.text = pygame.font.SysFont(self.name, 20).render(
            self.name, 1, pygame.Color('black'))
        self._dead = False
        self.spawn_delay = 300
        self.spawndelay = 0

    def render(self, game):
        self.draw(game)
        self.spawndelay += 1
        if self.spawndelay > self.spawn_delay:
            self.spawndelay = 0
            game.enemies.append(self.mob(random.randint(
                self.rect.x - 30, self.rect.x + 50),
                                         random.randint(
                self.rect.y - 30, self.rect.y + 50)))
        if self._dead:
            game.spawners.remove(self)

    def draw(self, game):
        pygame.draw.rect(game.screen, self.col, self.rect)

    def take_damage(self, dmg):
        self.rect.x = 1000000
        self.rect.y = 1000000
        self._dead = True

    def knockback(self, knockback, player):
        pass


class BaseZombie(BaseEnemy):    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.maintype = 'zombie'
        self.secondtype = 'undead'
        self.damage = 2
        self.name = 'Zombie'
        self.text = pygame.font.SysFont(self.name, 20).render(
            self.name, 1, pygame.Color('black'))
        self.xp_drop = 0.15
        self.speed = 2
        self.reach = 15

    def render(self, game):
        super().render(game)
        if self.hp < 0:
            dungeon_settings.zombie_die.play()
        if random.randint(0, 20) == 0:
            dungeon_settings.zombie_groan.play()


class BaseSkeleton(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.maintype = 'skeleton'
        self.secondtype = 'undead'
        self.color_body = pygame.Color('white')
        self.color_head = pygame.Color('white')
        self.color_arm = pygame.Color('white')
        self.name = 'Skeleton'
        self.text = pygame.font.SysFont(self.name, 20).render(
            self.name, 1, pygame.Color('black'))
        self.damage = 0
        self.arrow = {'type': dungeon_arrows.Arrow,
                      'damage': 2, 'knockback': 20}
        self.delay_damage = 70
        self.xp_drop = 0.15
        self.speed = 2
        
    def render(self, game):
        super().render(game)
        if self.delaydamage == 0 and self.speed > 0:
            self.shoot(game)

    def shoot(self, game):
        player = self.get_target(game)
        arrow = self.arrow['type']((self.rect.x, self.rect.y),
                                   (player.rect.x, player.rect.y),
                                   self.arrow['damage'],
                                   self.arrow['knockback'], self)
        game.arrows.append(arrow)


class Wraith(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.maintype = 'wraith'
        self.secondtype = 'undead'
        self.rect = pygame.Rect(x, y, 50, 40)
        self.hitbox = HitBox(self.rect.x, self.rect.y)
        self.reach = 20
        self.hpmax = 30
        self.hp = self.hpmax
        self.delay_move = 5
        self.speed = 5
        self.delay_damage = 500
        self.damage = 4
        self.xp_drop = 0.5
        self.text = pygame.font.SysFont('', 20).render(
            'Wraith', 1, pygame.Color('black'))

    def teleport_away(self):
        self.rect.x = random.randint(0,
                            pygame.display.get_surface().get_width())
        self.rect.y = random.randint(0,
                            pygame.display.get_surface().get_height())

    def render(self, game):
        super().render(game)
        if self.delaydamage == 0 and self.speed > 0:
            '''player = self.get_target(game)
            px, py = player.rect.x, player.rect.y
            sx, sy = self.rect.x, self.rect.y
            if px < sx:
                xo = -min(sx - px, 300)
            else:
                xo = min(px - sx, 300)
            if py < sy:
                yo = -min(sy - py, 300)
            else:
                yo = min(py - sy, 300)
            offset = (xo, yo)
            game.other.append(dungeon_misc.WraithFlames(
                self.rect.x + offset[0], self.rect.y + offset[1]))'''
            player = self.get_target(game)
            px, py = player.rect.x, player.rect.y
            for i in (-30, 0, 30):
                for j in (-30, 0, 30):
                    game.other.append(dungeon_misc.WraithFlames(px + i, py + j))

    def draw(self, game):
        pygame.draw.rect(game.screen, pygame.Color('dark blue'),
                         pygame.Rect(self.rect.x + 10,
                                     self.rect.y + 10, 30, 30))
        pygame.draw.circle(game.screen, pygame.Color('light blue'),
                           (self.rect.x + 25, self.rect.y + 5), 5)
        pygame.draw.line(game.screen, pygame.Color('light blue'),
                         (self.rect.x, self.rect.y + 30),
                         (self.rect.x + 10, self.rect.y + 15), 4)
        pygame.draw.line(game.screen, pygame.Color('light blue'),
                         (self.rect.x + 50, self.rect.y + 30),
                         (self.rect.x + 40, self.rect.y + 15), 4)
        health_rect = pygame.Rect(self.rect.x - (self.hpmax // 2),
                                  self.rect.y - 5, int(self.hp * 2), 8)
        pygame.draw.rect(game.screen, pygame.Color('red'), health_rect)
        game.screen.blit(self.text, (self.rect.x - 5, self.rect.y - 20))

        if self.effects['fire'] > 0:
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 10, self.rect.y + 34),
                             (self.rect.x + 7, self.rect.y + 5), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 20, self.rect.y + 37),
                             (self.rect.x + 23, self.rect.y + 3), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 14, self.rect.y + 36),
                             (self.rect.x + 16, self.rect.y + 7), 4)

        if self.speed == 0:
            if self.mode == 'ice':
                pygame.draw.rect(game.screen, pygame.Color('light blue'),
                                 pygame.Rect(self.rect.x + 2, self.rect.y + 2,
                                    self.rect.width - 4, self.rect.height - 4))
            elif self.mode == 'chains':
                for y in range(self.rect.y,
                               self.rect.y + self.rect.height, 10):
                    pygame.draw.line(game.screen, pygame.Color('grey'),
                                     (self.rect.x, y),
                                     (self.rect.x + self.rect.width, y), 3)


class Enderman(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.maintype = 'enderman'
        self.secondtype = 'living'
        self.rect = pygame.Rect(x, y, 20, 80)
        self.hitbox = HitBox(self.rect.x, self.rect.y)
        self.reach = 50
        self.hpmax = 40
        self.hp = self.hpmax
        self.delay_move = 10
        self.speed = 10
        self.delay_damage = 20
        self.damage = 5
        self.xp_drop = 0.3
        self.text = pygame.font.SysFont('', 20).render(
            'Enderman', 1, pygame.Color('black'))

    def teleport(self):
        self.rect.x = random.randint(0,
                            pygame.display.get_surface().get_width())
        self.rect.y = random.randint(0,
                            pygame.display.get_surface().get_height())

    def take_damage(self, damage):
        super().take_damage(damage)
        self.teleport()

    def render(self, game):
        super().render(game)
        if self.effects['fire'] > 0 and random.randint(0, 5) == 0:
            self.teleport()
        if self.effects['poison'] > 0 and random.randint(0, 10) == 0:
            self.teleport()

    def draw(self, game):
        pygame.draw.rect(game.screen, pygame.Color('black'),
                         pygame.Rect(self.rect.x + 3, self.rect.y + 10,
                                     self.rect.width - 6,
                                     self.rect.height - 10))
        pygame.draw.line(game.screen, pygame.Color('black'),
                         (self.rect.x, self.rect.y + 60),
                         (self.rect.x + 3, self.rect.y + 20), 2)
        pygame.draw.line(game.screen, pygame.Color('black'),
                         (self.rect.x + self.rect.width, self.rect.y + 60),
                         (self.rect.x + self.rect.width - 3,
                          self.rect.y + 20), 2)
        pygame.draw.circle(game.screen, pygame.Color('black'),
                           (self.rect.x + 10, self.rect.y + 5), 5)
        health_rect = pygame.Rect(self.rect.x - (self.hpmax // 2),
                                  self.rect.y - 5, int(self.hp * 2), 8)
        pygame.draw.rect(game.screen, pygame.Color('red'), health_rect)
        game.screen.blit(self.text, (self.rect.x - 5, self.rect.y - 20))

        if self.effects['fire'] > 0:
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 10, self.rect.y + 74),
                             (self.rect.x + 7, self.rect.y + 5), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 20, self.rect.y + 77),
                             (self.rect.x + 23, self.rect.y + 3), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 14, self.rect.y + 76),
                             (self.rect.x + 16, self.rect.y + 7), 4)

        if self.speed == 0:
            if self.mode == 'ice':
                pygame.draw.rect(game.screen, pygame.Color('light blue'),
                                 pygame.Rect(self.rect.x + 2, self.rect.y + 2,
                                             self.rect.width - 4,
                                             self.rect.height - 4))
            elif self.mode == 'chains':
                for y in range(self.rect.y,
                               self.rect.y + self.rect.height, 10):
                    pygame.draw.line(game.screen, pygame.Color('grey'),
                                     (self.rect.x, y),
                                     (self.rect.x + self.rect.width, y), 3)


class RedstoneGolem(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.maintype = 'golem'
        self.secondtype = 'living'
        self.rect = pygame.Rect(x, y, 70, 90)
        self.hitbox = HitBox(self.rect.x, self.rect.y)
        self.reach = 60
        self.hpmax = 120
        self.hp = 120
        self.name = 'Redstone Golem'
        self.text = pygame.font.SysFont(self.name, 20).render(
            self.name, 1, pygame.Color('black'))
        self.delay_move = 10
        self.speed = 1
        self.delay_damage = 20
        self.damage = 10
        self.xp_drop = 0.1

    def draw(self, game):
        super().draw(game)
        pygame.draw.rect(game.screen, pygame.Color('grey'),
                         pygame.Rect(self.rect.x + 10,
                                     self.rect.y + 10, 50, 80))
        pygame.draw.circle(game.screen, pygame.Color('grey'),
                           (self.rect.x + 35, self.rect.y + 5), 10)
        pygame.draw.line(game.screen, pygame.Color('grey'),
                         (self.rect.x, self.rect.y + 50),
                         (self.rect.x + 10, self.rect.y + 15), 4)
        pygame.draw.line(game.screen, pygame.Color('grey'),
                         (self.rect.x + 70, self.rect.y + 50),
                         (self.rect.x + 60, self.rect.y + 15), 4)
        health_rect = pygame.Rect(self.rect.x - (self.hpmax // 2),
                                  self.rect.y - 5, int(self.hp * 2), 8)
        pygame.draw.rect(game.screen, pygame.Color('red'), health_rect)
        game.screen.blit(self.text, (self.rect.x - 5, self.rect.y - 20))

        if self.effects['fire'] > 0:
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 10, self.rect.y + 84),
                             (self.rect.x + 7, self.rect.y + 5), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 14, self.rect.y + 86),
                             (self.rect.x + 16, self.rect.y + 7), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 35, self.rect.y + 87),
                             (self.rect.x + 32, self.rect.y + 3), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 40, self.rect.y + 84),
                             (self.rect.x + 42, self.rect.y + 5), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 38, self.rect.y + 86),
                             (self.rect.x + 39, self.rect.y + 7), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 49, self.rect.y + 87),
                             (self.rect.x + 48, self.rect.y + 3), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 59, self.rect.y + 84),
                             (self.rect.x + 58, self.rect.y + 5), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 51, self.rect.y + 86),
                             (self.rect.x + 52, self.rect.y + 7), 4)

        if self.speed == 0:
            if self.mode == 'ice':
                pygame.draw.rect(game.screen, pygame.Color('light blue'),
                                 pygame.Rect(self.rect.x + 2, self.rect.y + 2,
                                             self.rect.width - 4,
                                             self.rect.height - 4))
            elif self.mode == 'chains':
                for y in range(self.rect.y,
                               self.rect.y + self.rect.height, 10):
                    pygame.draw.line(game.screen, pygame.Color('grey'),
                                     (self.rect.x, y),
                                     (self.rect.x + self.rect.width, y), 3)

    def render(self, game):
        super().render(game)
        if self.delaydamage == 0 and self.speed > 0 \
           and random.randint(0, 30) == 0:
            self.shockwave(game)

    def shockwave(self, game):
        for i in range(20):
            self.rect.y -= 10
            game.play()
        for i in range(20):
            self.rect.y += 10
            game.play()
        for i in range(100):
            game.play()
            pygame.draw.circle(game.screen, pygame.Color('yellow'),
                               (self.rect.x + 35, self.rect.y + 45), 3 * i, 1)
            pygame.display.update()
            
            def distance(obj, me):
                return math.dist((obj.rect.centerx, obj.rect.centery), (me.rect.centerx, me.rect.centery))
            
            for entity in [game.player] + game.helpfuls:
                if distance(self, entity) < 3 * i:
                    if entity != game.player:
                        entity.take_damage(self, 20)
                    else:
                        entity.take_damage(20)
                        entity.armor_use(self, game)
                    entity.knockback(100, self)


class RedstoneMonstrosity(RedstoneGolem):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.maintype = 'boss'
        self.rect = pygame.Rect(x, y, 140, 180) #4x the size
        self.reach = 120
        self.hpmax = 200
        self.hp = 200
        self.name = 'Redstone Monstrosity'
        self.text = pygame.font.SysFont(self.name, 20).render(
            self.name, 1, pygame.Color('black'))
        self.delay_move = 20
        self.delay_damage = 40
        self.damage = 20
        self.xp_drop = 2.0

    def render(self, game):
        super().render(game)
        if self.delaydamage == 0 and self.speed > 0 and \
           random.randint(0, 10) == 0:
            game.enemies.append(RedstoneCube(
                random.randint(self.rect.x - 20, self.rect.x + 180),
                random.randint(self.rect.y - 20, self.rect.y + 220)))

    def shockwave(self, game):
        for i in range(20):
            self.rect.y -= 20
            game.play()
        for i in range(20):
            self.rect.y += 20
            game.play()
        for i in range(200):
            game.play()
            pygame.draw.circle(game.screen, pygame.Color('yellow'),
                               (self.rect.x + 70, self.rect.y + 90), 3 * i, 1)
            pygame.display.update()
            def distance(obj, me):
                return math.dist((obj.rect.centerx, obj.rect.centery), (me.rect.centerx, me.rect.centery))
            for entity in [game.player] + game.helpfuls:
                if distance(self, entity) < 3 * i:
                    if entity != game.player:
                        entity.take_damage(self, 35)
                    else:
                        entity.take_damage(35)
                        entity.armor_use(self, game)
                    entity.knockback(100, self)

    def draw(self, game):
        pygame.draw.rect(game.screen, pygame.Color('grey'),
                         pygame.Rect(self.rect.x + 20,
                                     self.rect.y + 20, 100, 160))
        pygame.draw.circle(game.screen, pygame.Color('grey'),
                           (self.rect.x + 70, self.rect.y + 10), 20)
        pygame.draw.line(game.screen, pygame.Color('grey'),
                         (self.rect.x, self.rect.y + 100),
                         (self.rect.x + 20, self.rect.y + 30), 4)
        pygame.draw.line(game.screen, pygame.Color('grey'),
                         (self.rect.x + 140, self.rect.y + 100),
                         (self.rect.x + 120, self.rect.y + 30), 4)
        health_rect = pygame.Rect(self.rect.x - (self.hpmax // 2),
                                  self.rect.y - 5, int(self.hp * 2), 8)
        pygame.draw.rect(game.screen, pygame.Color('red'), health_rect)
        game.screen.blit(self.text, (self.rect.x - 5, self.rect.y - 20))

        if self.effects['fire'] > 0:
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 10, self.rect.y + 164),
                             (self.rect.x + 7, self.rect.y + 5), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 40, self.rect.y + 167),
                             (self.rect.x + 43, self.rect.y + 3), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 14, self.rect.y + 166),
                             (self.rect.x + 16, self.rect.y + 7), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 47, self.rect.y + 164),
                             (self.rect.x + 48, self.rect.y + 5), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 35, self.rect.y + 167),
                             (self.rect.x + 32, self.rect.y + 3), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 60, self.rect.y + 166),
                             (self.rect.x + 66, self.rect.y + 7), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 40, self.rect.y + 164),
                             (self.rect.x + 42, self.rect.y + 5), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 85, self.rect.y + 167),
                             (self.rect.x + 87, self.rect.y + 3), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 38, self.rect.y + 166),
                             (self.rect.x + 39, self.rect.y + 7), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 125, self.rect.y + 164),
                             (self.rect.x + 123, self.rect.y + 5), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 49, self.rect.y + 167),
                             (self.rect.x + 48, self.rect.y + 3), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 121, self.rect.y + 166),
                             (self.rect.x + 124, self.rect.y + 7), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 59, self.rect.y + 164),
                             (self.rect.x + 58, self.rect.y + 5), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 105, self.rect.y + 167),
                             (self.rect.x + 104, self.rect.y + 3), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 51, self.rect.y + 166),
                             (self.rect.x + 52, self.rect.y + 7), 4)

        if self.speed == 0:
            if self.mode == 'ice':
                pygame.draw.rect(game.screen, pygame.Color('light blue'),
                                 pygame.Rect(self.rect.x + 2, self.rect.y + 2,
                                             self.rect.width - 4,
                                             self.rect.height - 4))
            elif self.mode == 'chains':
                for y in range(self.rect.y,
                               self.rect.y + self.rect.height, 10):
                    pygame.draw.line(game.screen, pygame.Color('grey'),
                                     (self.rect.x, y),
                                     (self.rect.x + self.rect.width, y), 3)


class Slime(BaseEnemy):
    def __init__(self, x, y, size=3):
        super().__init__(x, y)
        d1 = {3: 18, 2: 6, 1: 1}
        d2 = {3: 4, 2: 2, 1: 0}
        self.maintype = 'slime'
        self.secondtype = 'living'
        self.rect = pygame.Rect(x - 2, y - 2, (size * 9) + 4, (size * 9) + 4)
        self.hitbox = self
        self.size = size
        self.hp = self.hpmax = d1[size]
        self.damage = d2[size]
        self.delay_move = self.delay_damage = 80
        self.speed = 15
        self.text = pygame.font.SysFont('', 20).render(
            'Slime', 1, pygame.Color('black'))

    def render(self, game):
        player = self.get_target(game)
        self.delaymove += 1
        if self.delaymove >= self.delay_move:
            self.delaymove = 0
            if player.rect.x < self.rect.x:
                self.rect.x -= self.speed
                if self.effects['slowness'] > 0:
                    self.rect.x += 1
            else:
                self.rect.x += self.speed
                if self.effects['slowness'] > 0:
                    self.rect.x -= 1
            if player.rect.y < self.rect.y:
                self.rect.y -= self.speed
                if self.effects['slowness'] > 0:
                    self.rect.y += 1
            else:
                self.rect.y += self.speed
                if self.effects['slowness'] > 0:
                    self.rect.y -= 1

        if time.time() - self.decreaseeffectslast >= 1:
            self.decreaseeffectslast = time.time()
            for effect in self.effects.keys():
                if self.effects[effect] > 0:
                    self.effects[effect] -= 1
            if self.effects['poison'] > 0 and random.randint(0, 2) == 0 \
               and self.hp > 1:
                self.hp -= 1
            if self.effects['regeneration'] > 0 and random.randint(0, 2) == 0:
                self.hp += 1
            if self.effects['fire'] > 0 and random.randint(0, 1) == 0:
                self.hp -= 1
                
        for effect in self.effects.keys():
            if self.effects[effect] > 0 and effect != 'fire':
                particle.particle(effect, self.rect.x, self.rect.x + 30,
                                  self.rect.y, self.rect.y + 35, game)

        self.draw(game)

        if self.hp > self.hpmax:
            self.hp = self.hpmax

        if self.hp <= 0:
            game.enemies.remove(self)
            for i in game.enemies:
                if type(i) == TheCauldron:
                    if dungeon_util.distance_between(i.rect.x, i.rect.y,
                                            self.rect.y, self.rect.y) < 300:
                        i.hp += 3
                        break
            self.die(game)
            self.rect.x = 10000
            self.rect.y = 10000
            game.player.get_xp(0.2 if self.size in [1, 2] else 0.1)
            game.player.kill()
            self.dead = True

        self.delaydamage += 1
        if self.delaydamage >= self.delay_damage and self.speed > 0:
            if pygame.sprite.collide_rect(player, self):
                if player == game.player:
                    player.take_damage(self.damage)
                    game.player.armor_use(self, game)
                else:
                    player.take_damage(self, self.damage)
            self.delaydamage = 0

    def die(self, game):
        if self.size == 3:
            for slime in range(random.randint(2, 4)):
                game.enemies.append(Slime(
                    random.randint(self.rect.x - 5, self.rect.x + 35),
                    random.randint(self.rect.y - 5, self.rect.y + 35), 2))
        elif self.size == 2:
            for slime in range(random.randint(2, 4)):
                game.enemies.append(Slime(
                    random.randint(self.rect.x - 5, self.rect.x + 25),
                    random.randint(self.rect.y - 5, self.rect.y + 25), 1))

    def draw(self, game):
        pygame.draw.rect(game.screen, pygame.Color('green'),
                         pygame.Rect(self.rect.x + 2, self.rect.y + 2,
                                     (self.size * 9), (self.size * 9)))
        health_rect = pygame.Rect(self.rect.x - (self.hpmax // 2),
                                  self.rect.y - 7, int(self.hp * 2), 8)
        pygame.draw.rect(game.screen, pygame.Color('red'), health_rect)
        game.screen.blit(self.text, (self.rect.x - 5, self.rect.y - 22))

        if self.effects['fire'] > 0:
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 10, self.rect.y + 24),
                             (self.rect.x + 7, self.rect.y + 5), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 20, self.rect.y + 27),
                             (self.rect.x + 23, self.rect.y + 3), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 14, self.rect.y + 26),
                             (self.rect.x + 16, self.rect.y + 7), 4)

        if self.speed == 0:
            if self.mode == 'ice':
                pygame.draw.rect(game.screen, pygame.Color('light blue'),
                                 pygame.Rect(self.rect.x + 2, self.rect.y + 2,
                                             self.rect.width - 4,
                                             self.rect.height - 4))
            elif self.mode == 'chains':
                for y in range(self.rect.y,
                               self.rect.y + self.rect.height, 10):
                    pygame.draw.line(game.screen, pygame.Color('grey'),
                                     (self.rect.x, y),
                                     (self.rect.x + self.rect.width, y), 3)


class RedstoneCube(Slime):
    def __init__(self, x, y):
        super().__init__(x, y, 1)
        self.delay_move = 30
        self.speed = 2
        self.delay_damage = 10
        self.damage = 3
        self.text = pygame.font.SysFont('', 20).render(
            'Redstone Cube', 1, pygame.Color('black'))
        self.hpmax = 10
        self.hp = 10
        self.col = pygame.Color('red')

    def draw(self, game):
        pygame.draw.rect(game.screen, self.col,
                         pygame.Rect(self.rect.x + 2, self.rect.y + 2,
                                     (self.size * 9), (self.size * 9)))
        health_rect = pygame.Rect(self.rect.x - (self.hpmax // 2),
                                  self.rect.y - 7, int(self.hp * 2), 8)
        pygame.draw.rect(game.screen, pygame.Color('red'), health_rect)
        game.screen.blit(self.text, (self.rect.x - 5, self.rect.y - 22))

        if self.effects['fire'] > 0:
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 10, self.rect.y + 24),
                             (self.rect.x + 7, self.rect.y + 5), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 20, self.rect.y + 27),
                             (self.rect.x + 23, self.rect.y + 3), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 14, self.rect.y + 26),
                             (self.rect.x + 16, self.rect.y + 7), 4)

        if self.speed == 0:
            if self.mode == 'ice':
                pygame.draw.rect(game.screen, pygame.Color('light blue'),
                            pygame.Rect(self.rect.x + 2, self.rect.y + 2,
                                        self.rect.width - 4,
                                        self.rect.height - 4))
            elif self.mode == 'chains':
                for y in range(self.rect.y,
                               self.rect.y + self.rect.height, 10):
                    pygame.draw.line(game.screen, pygame.Color('grey'),
                                     (self.rect.x, y),
                                     (self.rect.x + self.rect.width, y), 3)


class ConjuredSlime(RedstoneCube):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.delay_move = 10
        self.speed = 2
        self.delay_damage = 70
        self.damage = 1
        self.text = pygame.font.SysFont('', 20).render(
            'Conjured Slime', 1, pygame.Color('black'))
        self.hpmax = 20
        self.hp = 20
        self.col = pygame.Color('purple')

    def render(self, game):
        super().render(game)
        if self.delaydamage == 0:
            game.arrows.append(
                dungeon_misc.ConjuredProjectile(self.rect.x, self.rect.y))


class Piglin(BaseSkeleton):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.maintype = 'piglin'
        self.secondtype = 'living'
        self.color_body = pygame.Color('brown')
        self.color_head = pygame.Color('pink')
        self.color_arm = pygame.Color('pink')
        self.weapon = dungeon_weapons.Crossbow()
        self.delay_damage = 100
        self.hp = 24
        self.name = 'Piglin'
        self.text = pygame.font.SysFont(self.name, 20).render(
            self.name, 1, pygame.Color('black'))
        self.xp_drop = 0.1
        self.hpmax = self.hp
        self.speed = 3
        self.arrow = {'type': dungeon_arrows.Arrow,
                      'damage': 4, 'knockback': 30}

    def draw(self, game):
        super().draw(game)
        self.weapon.render(self.rect.x + 5, self.rect.y + 20, game)


class PiglinSword(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.maintype = 'piglin'
        self.secondtype = 'living'
        self.color_body = pygame.Color('brown')
        self.color_head = pygame.Color('pink')
        self.color_arm = pygame.Color('pink')
        self.weapon = dungeon_weapons.GoldenSword()
        self.damage = 5
        self.xp_drop = 0.1
        self.hp = 24
        self.hpmax = self.hp
        self.speed = 3
        self.delay_damage = 10
        self.name = 'Piglin'
        self.text = pygame.font.SysFont(self.name, 20).render(
            self.name, 1, pygame.Color('black'))

    def draw(self, game):
        super().draw(game)
        self.weapon.render(self.rect.x + 25, self.rect.y + 20, game)


class PiglinBrute(PiglinSword):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.weapon = dungeon_weapons.GoldenAxe()
        self.damage = 11
        self.xp_drop = 0.5
        self.hp = 50
        self.hpmax = self.hp
        self.speed = 5
        self.delay_damage = 5
        self.name = 'Piglin Brute'
        self.text = pygame.font.SysFont(self.name, 20).render(
            self.name, 1, pygame.Color('black'))


class BaseIllager(BaseEnemy):    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.maintype = 'illager'
        self.secondtype = 'living'
        self.melee = False
        self.color_body = pygame.Color('brown')
        self.color_head = pygame.Color('grey')
        self.color_arm = pygame.Color('grey')
        self.has_weapon = True
        self.weapon = dungeon_weapons.Crossbow()
        self.damage = 2
        self.delay_damage = 10 if self.melee else 80
        self.hp = 24
        self.name = 'Pillager'
        self.text = pygame.font.SysFont(self.name, 20).render(
            self.name, 1, pygame.Color('black'))
        self.xp_drop = 0.15
        self.hpmax = self.hp
        self.speed = 2
        self.arrow = {'type': dungeon_arrows.Arrow,
                      'damage': 3, 'knockback': 25}
        self.fix()

    def fix(self):
        self.delay_damage = 10 if self.melee else 80
        if self.melee:
            self.damage = self.weapon.damage
        else:
            self.arrow = self.weapon.arrow
        self.text = pygame.font.SysFont(self.name, 20).render(
            self.name, 1, pygame.Color('black'))

    def render(self, game):
        super().render(game)

        self.attack(game)

    def attack(self, game):
        player = self.get_target(game)
        if self.melee:
            self.delaydamage += 1
            if self.delaydamage >= self.delay_damage and self.speed > 0:
                if pygame.sprite.collide_rect(player, self.hitbox):
                    if player == game.player:
                        player.take_damage(self.damage)
                        game.player.armor_use(self, game)
                    else:
                        player.take_damage(self, self.damage)
                self.delaydamage = 0
        else:
            self.delaydamage += 1
            if self.delaydamage >= self.delay_damage and self.speed > 0:
                self.delaydamage = 0
                arrow = self.arrow['type']((self.rect.x, self.rect.y),
                                           (player.rect.x, player.rect.y),
                                           self.arrow['damage'],
                                           self.arrow['knockback'], self)
                game.arrows.append(arrow)

    def draw(self, game):
        super().draw(game)

        if self.has_weapon:
            self.weapon.render(self.rect.x + (25 if self.melee else 5),
                               self.rect.y + 20, game)


class Creeper(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.maintype = 'creeper'
        self.secondtype = 'living'
        self.delay = 0
        self.fused = False
        self.name = 'Creeper'
        self.text = pygame.font.SysFont(self.name, 20).render(
            self.name, 1, pygame.Color('black'))
        self.delay_damage = float('inf')

    def render(self, game):
        super().render(game)
        player = self.get_target(game)
        if math.dist((player.rect.x, player.rect.y), (self.rect.x, self.rect.y)) <= 100:
            if not self.fused:
                self.fused = True
                self.delay = time.time()
        elif self.fused:
            self.fused = False
        if time.time() - self.delay >= 3 and self.fused:
            self.blow(game)

    def draw(self, game):
        pygame.draw.rect(game.screen, pygame.Color('green'),
                         pygame.Rect(self.rect.x + 5, self.rect.y + 5, 20, 30))
        health_rect = pygame.Rect(self.rect.x - (self.hpmax // 2),
                                  self.rect.y - 5, int(self.hp * 2), 8)
        pygame.draw.rect(game.screen, pygame.Color('red'), health_rect)
        game.screen.blit(self.text, (self.rect.x - 5, self.rect.y - 20))

        if self.effects['fire'] > 0:
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 10, self.rect.y + 24),
                             (self.rect.x + 7, self.rect.y + 5), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 20, self.rect.y + 27),
                             (self.rect.x + 23, self.rect.y + 3), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 14, self.rect.y + 26),
                             (self.rect.x + 16, self.rect.y + 7), 4)

        if self.speed == 0:
            if self.mode == 'ice':
                pygame.draw.rect(game.screen, pygame.Color('light blue'),
                                 pygame.Rect(self.rect.x + 2, self.rect.y + 2,
                                             self.rect.width - 4,
                                             self.rect.height - 4))
            elif self.mode == 'chains':
                for y in range(self.rect.y,
                               self.rect.y + self.rect.height, 10):
                    pygame.draw.line(game.screen, pygame.Color('grey'),
                                     (self.rect.x, y),
                                     (self.rect.x + self.rect.width, y), 3)

    def blow(self, game):
        game.enemies.remove(self)
        for enemy in game.enemies:
            if type(enemy) == TheCauldron:
                if dungeon_util.distance_between(enemy.rect.x, enemy.rect.y,
                                            self.rect.y, self.rect.y) < 300:
                    enemy.hp += 3  # heal the cauldron
                    break
        player = self.get_target(game)
        player.knockback(100, self)
        self.rect.x = 10000
        self.rect.y = 10000
        self.dead = True
        if player == game.player:
            player.take_damage(30)
        else:
            player.take_damage(self, 30)


class Spider(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.maintype = 'spider'
        self.secondtype = 'living'
        self.name = 'Spider'
        self.text = pygame.font.SysFont(self.name, 20).render(
            self.name, 1, pygame.Color('black'))
        self.damage = 2
        self.col = pygame.Color('black')
        self.eyecol = pygame.Color('red')
        self.delay_move = 5
        self.speed = 4

    def draw(self, game):
        pygame.draw.rect(game.screen, self.col,
                         pygame.Rect(self.rect.x + 10,
                                     self.rect.y + 5, 10, 30))  # body
        pygame.draw.line(game.screen, self.col,
                         (self.rect.x + 5, self.rect.y),
                         (self.rect.x + 10, self.rect.y + 5), 2)  # leg 1
        pygame.draw.line(game.screen, self.col,
                         (self.rect.x + 5, self.rect.y + 8),
                         (self.rect.x + 10, self.rect.y + 12), 2)  # leg 2
        pygame.draw.line(game.screen, self.col,
                         (self.rect.x + 5, self.rect.y + 22),
                         (self.rect.x + 10, self.rect.y + 18), 2)  # leg 3
        pygame.draw.line(game.screen, self.col,
                         (self.rect.x + 5, self.rect.y + 30),
                         (self.rect.x + 10, self.rect.y + 25), 2)  # leg 4
        pygame.draw.line(game.screen, self.col,
                         (self.rect.x + 25, self.rect.y),
                         (self.rect.x + 20, self.rect.y + 5), 2)  # leg 5
        pygame.draw.line(game.screen, self.col,
                         (self.rect.x + 25, self.rect.y + 8),
                         (self.rect.x + 20, self.rect.y + 12), 2)  # leg 6
        pygame.draw.line(game.screen, self.col,
                         (self.rect.x + 25, self.rect.y + 22),
                         (self.rect.x + 20, self.rect.y + 18), 2)  # leg 7
        pygame.draw.line(game.screen, self.col,
                         (self.rect.x + 25, self.rect.y + 30),
                         (self.rect.x + 20, self.rect.y + 25), 2)  # leg 8
        pygame.draw.circle(game.screen, self.eyecol,
                           (self.rect.x + 13, self.rect.y + 8), 2)
        pygame.draw.circle(game.screen, self.eyecol,
                           (self.rect.x + 17, self.rect.y + 8), 2)  # eyes
        health_rect = pygame.Rect(self.rect.x - (self.hpmax // 2),
                                  self.rect.y - 5, int(self.hp * 2), 8)
        pygame.draw.rect(game.screen, pygame.Color('red'), health_rect)
        game.screen.blit(self.text, (self.rect.x - 5, self.rect.y - 20))

        if self.effects['fire'] > 0:
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 10, self.rect.y + 24),
                             (self.rect.x + 7, self.rect.y + 5), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 20, self.rect.y + 27),
                             (self.rect.x + 23, self.rect.y + 3), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 14, self.rect.y + 26),
                             (self.rect.x + 16, self.rect.y + 7), 4)

        if self.speed == 0:
            if self.mode == 'ice':
                pygame.draw.rect(game.screen, pygame.Color('light blue'),
                                 pygame.Rect(self.rect.x + 2,
                                             self.rect.y + 2,
                                             self.rect.width - 4,
                                             self.rect.height - 4))
            elif self.mode == 'chains':
                for y in range(self.rect.y,
                               self.rect.y + self.rect.height, 10):
                    pygame.draw.line(game.screen, pygame.Color('grey'),
                                     (self.rect.x, y),
                                     (self.rect.x + self.rect.width, y), 3)


class CaveSpider(Spider):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.name = 'Cave Spider'
        self.text = pygame.font.SysFont(self.name, 20).render(
            self.name, 1, pygame.Color('black'))
        self.damage = 1
        self.col = pygame.Color('dark blue')
        self.delay_move = 4
        self.speed = 5

    def render(self, game):
        super().render(game)
        player = self.get_target(game)
        if self.delaydamage == 0 and self.speed > 0 and \
           pygame.sprite.collide_rect(player, self) and \
           player.effects['poison'] < 5:
            player.effects['poison'] = 5


class Zombie(BaseZombie):
    pass  # so Zombie is a subclass of BaseZombie


class Husk(BaseZombie):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color_body = pygame.Color(15, 10, 8)
        self.color_head = pygame.Color('tan')
        self.color_arm = pygame.Color('tan')
        self.delay_move = 13
        self.delay_damage = 8
        self.name = 'Husk'
        self.text = pygame.font.SysFont(self.name, 20).render(
            self.name, 1, pygame.Color('black'))
        self.xp_drop = 0.25
        self.damage = 3
        self.hpmax = self.hp


class Drowned(BaseZombie):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color_body = pygame.Color('blue')
        self.color_head = pygame.Color('light blue')
        self.color_arm = pygame.Color('light blue')
        self.delay_move = 12
        self.delay_damage = 8
        self.name = 'Drowned'
        self.text = pygame.font.SysFont(self.name, 20).render(
            self.name, 1, pygame.Color('black'))
        self.xp_drop = 0.25
        self.hpmax = self.hp
        self.damage = 4


class PlantZombie(BaseZombie):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color_body = pygame.Color('green')
        self.delay_move = 8
        self.delay_damage = 5
        self.name = 'Plant Zombie'
        self.text = pygame.font.SysFont(self.name, 20).render(
            self.name, 1, pygame.Color('black'))
        self.xp_drop = 0.4
        self.hpmax = 30
        self.hp = self.hpmax
        self.knockback_resistance = 10
        self.reach = 20
        self.damage = 5

    def render(self, game):
        super().render(game)
        player = self.get_target(game)
        if self.delaydamage == 0 and self.speed > 0 and \
           pygame.sprite.collide_rect(player, self) and \
           player.effects['slowness'] < 30:
            player.effects['slowness'] = 30


class ArmoredZombie(BaseZombie):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color_body = pygame.Color('light grey')
        self.delay_move = 10
        self.delay_damage = 10
        self.name = 'Armored Zombie'
        self.text = pygame.font.SysFont(self.name, 20).render(
            self.name, 1, pygame.Color('black'))
        self.armor = 10
        self.reach = 30
        self.damage = 2


class BabyZombie(BaseZombie):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.delay_move = 3
        self.delay_damage = 3
        self.name = 'Baby Zombie'
        self.text = pygame.font.SysFont(self.name, 20).render(
            self.name, 1, pygame.Color('black'))
        self.reach = 10
        self.damage = 2
        self.rect.width = 15
        self.rect.height = 20
        self.hpmax = 10
        self.hp = self.hpmax
        self.xp_drop = 0.4

    def draw(self, game):
        pygame.draw.rect(game.screen, self.color_body,
                         pygame.Rect(self.rect.x + 5,
                                     self.rect.y + 10, 5, 10)) #body
        pygame.draw.circle(game.screen, self.color_head,
                           (self.rect.x + 10, self.rect.y + 5), 5) #head
        pygame.draw.line(game.screen, self.color_arm,
                         (self.rect.x, self.rect.y + 15),
                         (self.rect.x + 5, self.rect.y + 10), 3) #arm
        pygame.draw.line(game.screen, self.color_arm,
                         (self.rect.x + 15, self.rect.y + 15),
                         (self.rect.x + 10, self.rect.y + 10), 3) #arm
        health_rect = pygame.Rect(self.rect.x - (self.hpmax // 2),
                                  self.rect.y - 5, int(self.hp * 2), 8)
        pygame.draw.rect(game.screen, pygame.Color('red'), health_rect)
        game.screen.blit(self.text, (self.rect.x - 5, self.rect.y - 10))

        if self.effects['fire'] > 0:
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 5, self.rect.y + 19),
                             (self.rect.x + 1, self.rect.y + 2), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 15, self.rect.y + 18),
                             (self.rect.x + 17, self.rect.y + 3), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 9, self.rect.y + 20),
                             (self.rect.x + 10, self.rect.y + 7), 4)

        if self.speed == 0:
            if self.mode == 'ice':
                pygame.draw.rect(game.screen, pygame.Color('light blue'),
                        pygame.Rect(self.rect.x + 2, self.rect.y + 2,
                                    self.rect.width - 4, self.rect.height - 4))
            elif self.mode == 'chains':
                for y in range(self.rect.y,
                               self.rect.y + self.rect.height, 10):
                    pygame.draw.line(game.screen, pygame.Color('grey'),
                                     (self.rect.x, y),
                                     (self.rect.x + self.rect.width, y), 3)


class ChickenJockey(BabyZombie):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.delay_move = 2
        self.name = 'Chicken Jockey'
        self.text = pygame.font.SysFont(self.name, 20).render(
            self.name, 1, pygame.Color('black'))
        self.rect.height = 30
        self.xp_drop = 0.5

    def draw(self, game):
        pygame.draw.rect(game.screen, pygame.Color('white'),
                         pygame.Rect(self.rect.x + 3,
                                     self.rect.y + 19, 9, 10)) #chicken
        pygame.draw.rect(game.screen, self.color_body,
                         pygame.Rect(self.rect.x + 5,
                                     self.rect.y + 10, 5, 10)) #body
        pygame.draw.circle(game.screen, self.color_head,
                           (self.rect.x + 10, self.rect.y + 5), 5) #head
        pygame.draw.line(game.screen, self.color_arm,
                         (self.rect.x, self.rect.y + 15),
                         (self.rect.x + 5, self.rect.y + 10), 3) #arm
        pygame.draw.line(game.screen, self.color_arm,
                         (self.rect.x + 15, self.rect.y + 15),
                         (self.rect.x + 10, self.rect.y + 10), 3) #arm
        health_rect = pygame.Rect(self.rect.x - (self.hpmax // 2),
                                  self.rect.y - 5, int(self.hp * 2), 8)
        pygame.draw.rect(game.screen, pygame.Color('red'), health_rect)
        game.screen.blit(self.text, (self.rect.x - 5, self.rect.y - 10))

        if self.effects['fire'] > 0:
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 5, self.rect.y + 29),
                             (self.rect.x + 1, self.rect.y + 2), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 15, self.rect.y + 28),
                             (self.rect.x + 17, self.rect.y + 3), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 9, self.rect.y + 30),
                             (self.rect.x + 10, self.rect.y + 7), 4)

        if self.speed == 0:
            if self.mode == 'ice':
                pygame.draw.rect(game.screen, pygame.Color('light blue'),
                                 pygame.Rect(self.rect.x + 2, self.rect.y + 2,
                                             self.rect.width - 4,
                                             self.rect.height - 4))
            elif self.mode == 'chains':
                for y in range(self.rect.y,
                               self.rect.y + self.rect.height, 10):
                    pygame.draw.line(game.screen, pygame.Color('grey'),
                                     (self.rect.x, y),
                                     (self.rect.x + self.rect.width, y), 3)


class ChickenJockeyTower(ChickenJockey):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.name = 'Chicken Jockey Tower'
        self.text = pygame.font.SysFont(self.name, 20).render(
            self.name, 1, pygame.Color('black'))
        self.rect.height = 90
        self.hpmax = 10
        self.hp = self.hpmax
        self.xp_drop = 0
        self._game = None

    def drawzombie(self, x, y, game):
        pygame.draw.rect(game.screen, self.color_body,
                         pygame.Rect(x + 5, y + 10, 5, 10)) #body
        pygame.draw.circle(game.screen, self.color_head,
                           (x + 10, y + 5), 5) #head
        pygame.draw.line(game.screen, self.color_arm,
                         (x, y + 15), (x + 5, y + 10), 3) #arm
        pygame.draw.line(game.screen, self.color_arm,
                         (x + 15, y + 15), (x + 10, y + 10), 3) #arm

    def draw(self, game):
        if self._game is None:
            self._game = game
        pygame.draw.rect(game.screen, pygame.Color('white'),
                         pygame.Rect(self.rect.x + 3,
                                     self.rect.y + 79, 9, 10)) #chicken
        self.drawzombie(self.rect.x, self.rect.y + 60, game)
        self.drawzombie(self.rect.x, self.rect.y + 41, game)
        self.drawzombie(self.rect.x, self.rect.y + 22, game)
        self.drawzombie(self.rect.x, self.rect.y + 3, game)
        health_rect = pygame.Rect(self.rect.x - (self.hpmax // 2),
                                  self.rect.y - 5, int(self.hp * 2), 8)
        pygame.draw.rect(game.screen, pygame.Color('red'), health_rect)
        game.screen.blit(self.text, (self.rect.x - 5, self.rect.y - 10))

        if self.effects['fire'] > 0:
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 5, self.rect.y + 89),
                             (self.rect.x + 1, self.rect.y + 2), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 15, self.rect.y + 88),
                             (self.rect.x + 17, self.rect.y + 3), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 9, self.rect.y + 90),
                             (self.rect.x + 10, self.rect.y + 7), 4)

        if self.speed == 0:
            if self.mode == 'ice':
                pygame.draw.rect(game.screen, pygame.Color('light blue'),
                                 pygame.Rect(self.rect.x + 2, self.rect.y + 2,
                                             self.rect.width - 4,
                                             self.rect.height - 4))
            elif self.mode == 'chains':
                for y in range(self.rect.y,
                               self.rect.y + self.rect.height, 10):
                    pygame.draw.line(game.screen, pygame.Color('grey'),
                                     (self.rect.x, y),
                                     (self.rect.x + self.rect.width, y), 3)

    def take_damage(self, damage):
        super().take_damage(damage)
        for i in range(4):
            x = random.randint(self.rect.x, self.rect.x + self.rect.width)
            y = random.randint(self.rect.y, self.rect.y + self.rect.height)
            self._game.enemies.append(BabyZombie(x, y))


class SpeedyZombie(BaseZombie):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.delay_move = 6
        self.delay_damage = 4
        self.name = 'Speedy Zombie'
        self.text = pygame.font.SysFont(self.name, 20).render(
            self.name, 1, pygame.Color('black'))
        self.xp_drop = 0.35


class Necromancer(BaseZombie):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.maintype = 'wizard'
        self.delay_move = 8
        self.delay_damage = 200
        self.damage = 0
        self.name = 'Necromancer'
        self.text = pygame.font.SysFont(self.name, 20).render(
            self.name, 1, pygame.Color('black'))
        self.xp_drop = 0.6
        self.hpmax = 40
        self.hp = self.hpmax
        self.summondelay = 0
        self.summon_delay = 100
        self.color_head  = pygame.Color('black')
        self.color_arm = self.color_body = self.color_head
        self.shot = dungeon_arrows.Bolt
        self.summonable = [Zombie, Skeleton]

    def render(self, game):
        super().render(game)
        player = self.get_target(game)
        if self.delaydamage == 0 and self.speed > 0:
            arrow = self.shot((self.rect.x, self.rect.y),
                              (player.rect.x, player.rect.y), self)
            game.arrows.append(arrow)
            
        self.summondelay += 1
        if self.summondelay >= self.summon_delay and self.speed > 0:
            self.summondelay = 0
            enemy = random.choice(self.summonable)
            game.enemies.append(enemy(random.randint(
                self.rect.x - 50, self.rect.x + 80),
                                      random.randint(
                    self.rect.y - 50, self.rect.y + 85)))

        for enemy in game.enemies:
            if ((enemy.maintype == 'skeleton' or enemy.maintype == 'zombie')
               and math.dist((self.rect.x, self.rect.y), (game.player.rect.x, game.player.rect.y)) < 300):
                if enemy.effects['strength'] < 1:
                    enemy.effects['strength'] = 1
                if enemy.effects['speed'] < 1:
                    enemy.effects['speed'] = 1


class NamelessOne(Necromancer):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.maintype = 'boss'
        self.delay_move = 5
        self.delay_damage = 100
        self.damage = 3
        self.name = 'The Nameless One'
        self.text = pygame.font.SysFont(self.name, 20).render(
            self.name, 1, pygame.Color('black'))
        self.xp_drop = 1.5
        self.hpmax = 100
        self.hp = self.hpmax
        self.color_body = pygame.Color('white')
        self.color_head = pygame.Color('green')
        self.color_arm = pygame.Color('white')
        self.summon_delay = 80
        self.summonable = [SkeletonVanguard, SkeletonVanguard,
                           SkeletonVanguard, Necromancer]
        self.poses = []
        self.switchdelay = 0
        self.switch_delay = 300
        self.fix_poses()

    def render(self, game):
        super().render(game)
        self.switchdelay += 1
        if self.switchdelay >= self.switch_delay:
            self.switchdelay = 0
            self.fix_poses()
        if self.summondelay == 0 and self.speed > 0:
            for x, y in self.poses:
                enemy = random.choice(self.summonable)
                game.enemies.append(enemy(random.randint(x - 50, x + 80),
                                          random.randint(y - 50, y + 85)))
        if self.delaydamage == 0 and self.speed > 0:
            player = self.get_target(game)
            for x, y in self.poses:
                arrow = self.shot((self.rect.x, self.rect.y),
                                  (player.rect.x, player.rect.y), self)
                game.arrows.append(arrow)

    def fix_poses(self):
        self.poses.clear()
        for i in range(4):
            self.poses.append((random.randint(-80, 80),
                               random.randint(-80, 80)))
        self.rect.x += random.randint(-80, 80)
        self.rect.y += random.randint(-80, 80)

    def draw(self, game):
        super().draw(game)
        x = self.rect.x
        y = self.rect.y
        for x2, y2 in self.poses:
            self.rect.x += x2
            self.rect.y += y2
            super().draw(game)
            self.rect.x = x
            self.rect.y = y


class Skeleton(BaseSkeleton):
    pass


class Stray(BaseSkeleton):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color_body = pygame.Color('dark grey')
        self.arrow['type'] = dungeon_arrows.SlowArrow
        self.name = 'Stray'
        self.text = pygame.font.SysFont(self.name, 20).render(
            self.name, 1, pygame.Color('black'))


class MossSkeleton(BaseSkeleton):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color_body = self.color_head = pygame.Color('green')
        self.color_arm = pygame.Color('light green')
        self.name = 'Mossy Skeleton'
        self.text = pygame.font.SysFont(self.name, 20).render(
            self.name, 1, pygame.Color('black'))
        self.arrow['type'] = dungeon_arrows.PoisonArrow


class FlamingSkeleton(BaseSkeleton):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color_body = self.color_head = self.color_arm = pygame.Color('red')
        self.name = 'Flaming Skeleton'
        self.text = pygame.font.SysFont(self.name, 20).render(
            self.name, 1, pygame.Color('black'))
        self.arrow['type'] = dungeon_arrows.FlamingArrow


class SkeletonHorse(BaseZombie):
    # SkeletonHorse is just a BaseZombie so it can have most code written already.
    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.name = 'Skeleton Horse'
        self.text = pygame.font.SysFont(self.name, 20).render(
            self.name, 1, pygame.Color('black'))
        self.delay_damage = float('inf')  # Never damages you... kind of.
        self.col = pygame.Color(250, 250, 250, 255)  # Bones are an off-white.
        self.rect = pygame.Rect(x, y, 55, 25)

    def render(self, game):
        super().render(game)
        for i in game.helpfuls + [game.player]:
            if dungeon_util.distance_between(i.rect.x, i.rect.y,
                                             self.rect.x, self.rect.y) < 100:
                self.transform(game)

    def draw(self, game):
        pygame.draw.polygon(game.screen, self.col, [
            (self.rect.x, self.rect.y + 10),
            (self.rect.x + 5, self.rect.y + 15),
            (self.rect.x + 20, self.rect.y + 5),
            (self.rect.x + 15, self.rect.y)])
        pygame.draw.line(game.screen, self.col,
                         (self.rect.x + 20, self.rect.y + 5),
                         (self.rect.x + 25, self.rect.y + 15), 2)
        pygame.draw.rect(game.screen, self.col,
                         pygame.Rect(self.rect.x + 25, self.rect.y + 15,
                                     30, 10))
        pygame.draw.line(game.screen, self.col,
                         (self.rect.x + 30, self.rect.y + 15),
                         (self.rect.x + 28, self.rect.y + 25), 2)
        pygame.draw.line(game.screen, self.col,
                         (self.rect.x + 50, self.rect.y + 15),
                         (self.rect.x + 52, self.rect.y + 25), 2)
        health_rect = pygame.Rect(self.rect.x - (self.hpmax // 2),
                                  self.rect.y - 5, int(self.hp * 2), 8)
        pygame.draw.rect(game.screen, pygame.Color('red'), health_rect)
        game.screen.blit(self.text, (self.rect.x - 5, self.rect.y - 20))

        if self.effects['fire'] > 0:
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 10, self.rect.y + 74),
                             (self.rect.x + 7, self.rect.y + 5), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 20, self.rect.y + 77),
                             (self.rect.x + 23, self.rect.y + 3), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 14, self.rect.y + 76),
                             (self.rect.x + 16, self.rect.y + 7), 4)

        if self.speed == 0:
            if self.mode == 'ice':
                pygame.draw.rect(game.screen, pygame.Color('light blue'),
                                 pygame.Rect(self.rect.x + 2, self.rect.y + 2,
                                             self.rect.width - 4,
                                             self.rect.height - 4))
            elif self.mode == 'chains':
                for y in range(self.rect.y,
                               self.rect.y + self.rect.height, 10):
                    pygame.draw.line(game.screen, pygame.Color('grey'),
                                     (self.rect.x, y),
                                     (self.rect.x + self.rect.width, y), 3)

    def transform(self, game):
        for i in range(4):
            x = random.randint(self.rect.x, self.rect.x + self.rect.width)
            y = random.randint(self.rect.y, self.rect.y + self.rect.height)
            game.enemies.append(SkeletonHorseman(x, y))
        for i in game.enemies:
            if type(i) == TheCauldron:
                if dungeon_util.distance_between(
                    i.rect.x, i.rect.y, self.rect.y, self.rect.y) < 300:
                    i.hp += 3
                    break
        self.rect.x = 1000000
        self.rect.y = 1000000
        game.enemies.remove(self)
        self.dead = True


class SkeletonHorseman(BaseSkeleton):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.name = 'Skeleton Horseman'
        self.text = pygame.font.SysFont(self.name, 20).render(
            self.name, 1, pygame.Color('black'))
        self.armor = 1
        self.hpmax = 50
        self.hp = self.hpmax
        self.col = pygame.Color(250, 250, 250, 255)

    def draw(self, game):
        super().draw(game)
        self.horse_render(game)

    def horse_render(self, game):
        self.rect.x -= 5
        self.rect.y += 30
        pygame.draw.polygon(game.screen, self.col, [
            (self.rect.x, self.rect.y + 10),
            (self.rect.x + 5, self.rect.y + 15),
            (self.rect.x + 20, self.rect.y + 5),
            (self.rect.x + 15, self.rect.y)])
        pygame.draw.line(game.screen, self.col,
                         (self.rect.x + 20, self.rect.y + 5),
                         (self.rect.x + 25, self.rect.y + 15), 2)
        pygame.draw.rect(game.screen, self.col,
                         pygame.Rect(self.rect.x + 25, self.rect.y + 15,
                                     30, 10))
        pygame.draw.line(game.screen, self.col,
                         (self.rect.x + 30, self.rect.y + 15),
                         (self.rect.x + 28, self.rect.y + 25), 2)
        pygame.draw.line(game.screen, self.col,
                         (self.rect.x + 50, self.rect.y + 15),
                         (self.rect.x + 52, self.rect.y + 25), 2)
        self.rect.x += 5
        self.rect.y -= 30  # So it renders the horse under the rider


class Pillager(BaseIllager):
    pass


class Vindicator(BaseIllager):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.melee = True
        self.weapon = dungeon_weapons.IronAxe()
        self.name = 'Vindicator'
        self.delay_move = 10
        self.speed = 3
        self.fix()


class Vex(BaseIllager):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.melee = True
        self.weapon = dungeon_weapons.IronSword()
        self.name = 'Vex'
        self.delay_move = 5
        self.speed = 5
        self.color_arm = pygame.Color('light blue')
        self.color_body = self.color_arm
        self.color_head = self.color_arm
        self.fix()

    def draw(self, game):
        #Renders differently than normal illagers.
        pygame.draw.rect(game.screen, self.color_body,
                         pygame.Rect(self.rect.x + 10, self.rect.y + 15,
                                     10, 8))  # upper body
        pygame.draw.rect(game.screen, self.color_body,
                         pygame.Rect(self.rect.x + 12, self.rect.y + 23,
                                     6, 4))  # middle body
        pygame.draw.rect(game.screen, self.color_body,
                         pygame.Rect(self.rect.x + 14, self.rect.y + 27,
                                     4, 3))  # lower body
        pygame.draw.circle(game.screen, self.color_head,
                           (self.rect.x + 15, self.rect.y + 10), 5)  # head
        pygame.draw.line(game.screen, self.color_arm,
                         (self.rect.x + 10, self.rect.y + 15),
                         (self.rect.x + 5, self.rect.y + 20), 3) #arm
        pygame.draw.line(game.screen, self.color_arm,
                         (self.rect.x + 20, self.rect.y + 15),
                         (self.rect.x + 25, self.rect.y + 20), 3) #arm
        health_rect = pygame.Rect(self.rect.x - (self.hpmax // 2),
                                  self.rect.y - 5, int(self.hp * 2), 8)
        pygame.draw.rect(game.screen, pygame.Color('red'), health_rect)
        game.screen.blit(self.text, (self.rect.x - 5, self.rect.y - 20))

        if self.effects['fire'] > 0:
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 10, self.rect.y + 24),
                             (self.rect.x + 7, self.rect.y + 5), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 20, self.rect.y + 27),
                             (self.rect.x + 23, self.rect.y + 3), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 14, self.rect.y + 26),
                             (self.rect.x + 16, self.rect.y + 7), 4)

        if self.speed == 0:
            if self.mode == 'ice':
                pygame.draw.rect(game.screen, pygame.Color('light blue'),
                                 pygame.Rect(self.rect.x + 2, self.rect.y + 2,
                                             self.rect.width - 4,
                                             self.rect.height - 4))
            elif self.mode == 'chains':
                for y in range(self.rect.y,
                               self.rect.y + self.rect.height, 10):
                    pygame.draw.line(game.screen, pygame.Color('grey'),
                                     (self.rect.x, y),
                                     (self.rect.x + self.rect.width, y), 3)

        if self.has_weapon:
            self.weapon.render(self.rect.x + (25 if self.melee else 5),
                               self.rect.y + 20, game)


class Evoker(BaseIllager):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.melee = True
        # Just make shorthand weapons for illagers, except the vindicator.
        self.weapon = type('EvokerWand',
                           (object,),
                           {'damage': 0, 'render': self.wand_render})()
        self.name = 'Evoker'
        self.delay_move = 10
        self.speed = 2
        self.wand_color = pygame.Color('yellow')
        self.fix()
        self.delay_damage = 500

    def wand_render(self, x, y, game):
        pygame.draw.line(game.screen, self.wand_color,
                         (x, y), (x + 10, y + 10), 3)

    def attack(self, game):
        self.delaydamage += 1
        if self.delaydamage >= self.delay_damage and self.speed > 0:
            self.delaydamage = 0
            if random.randint(0, 2) == 0:
                game.enemies.append(Vex(self.rect.x + random.randint(-20, 20),
                                        self.rect.y + random.randint(-20, 20)))
                game.enemies.append(Vex(self.rect.x + random.randint(-20, 20),
                                        self.rect.y + random.randint(-20, 20)))
                game.enemies.append(Vex(self.rect.x + random.randint(-20, 20),
                                        self.rect.y + random.randint(-20, 20)))
            else:
                player = self.get_target(game)
                px, py = player.rect.x, player.rect.y
                sx, sy = self.rect.x, self.rect.y
                if px < sx:
                    xo = -min(sx - px, 100)
                else:
                    xo = min(px - sx, 100)
                if py < sy:
                    yo = -min(sy - py, 100)
                else:
                    yo = min(py - sy, 100)
                offset = (xo, yo)
                game.other.append(dungeon_misc.EvokerSpikes(
                    self.rect.x + offset[0],
                    self.rect.y + offset[1]))


class Iceologer(BaseIllager):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.melee = True
        self.has_weapon = False
        self.name = 'Iceologer'
        self.delay_damage = time.time()
        self.weapon = type('IceologerWand',
                           (object,),
                           {'damage': 0, 'render': lambda game: ...})()
        self.body_color = pygame.Color('blue')
        self.fix()

    def attack(self, game):
        if (time.time() - self.delay_damage > 5) and self.speed > 0:
            print('attack')
            self.delay_damage = time.time()
            player = self.get_target(game)
            game.other.append(dungeon_misc.IceBlock(player.rect.x, player.rect.y))


class Enchanter(BaseIllager):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.melee = True
        self.has_weapon = False
        self.name = 'Enchanter'
        self.connected = None
        self.weapon = type('EnchanterBook',
                           (object,),
                           {'damage': 0, 'render': lambda game: ...})()
        self.fix()

    def render(self, game):
        super().render(game)
        if len(game.enemies) <= 1:
            return
        if not self.connected:
            self.connected = self.closest(self, game.enemies)
        elif self.connected.hp <= 0:
            self.connected = self.closest(self, game.enemies)
        if self.connected is None:
            return
        if self.connected.effects['speed'] < 3:
            self.connected.effects['speed'] = 3
        if self.connected.effects['strength'] < 3:
            self.connected.effects['strength'] = 3
        if self.connected.effects['resistance'] < 3:
            self.connected.effects['resistance'] = 3
        self.draw_connected(game)
        
    def closest(self, obj, list):
        closest = None
        distance = 10000000000000000
        for i in list:
            if i is obj:
                continue
            dist = math.dist((i.rect.x, i.rect.y), (self.rect.x, self.rect.y))
            if dist < distance:
                distance = dist
                closest = i
        return closest

    def draw_connected(self, game):
        pygame.draw.line(game.screen, pygame.Color('white'),
                         (self.rect.x, self.rect.y),
                         (self.connected.rect.x, self.connected.rect.y), 5)

    def draw(self, game):
        super().draw(game)
        pygame.draw.rect(game.screen, pygame.Color('red'),
                         pygame.Rect(self.rect.x, self.rect.y, 30, 5))


class Geomancer(BaseIllager):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.melee = True
        self.has_weapon = False
        self.name = 'Geomancer'
        self.weapon = type('GeomancerRock',
                           (object,),
                           {'damage': 0, 'render': lambda game: ...})()
        self.fix()
        self.delay_damage = 70
        self.num = 0

    def attack(self, game):
        self.delaydamage += 1
        if self.delaydamage >= self.delay_damage and self.speed > 0:
            self.num += 1
            player = self.get_target(game)
            self.delaydamage = 0
            t = random.choice(([True] * 2) + ([False] * 5))
            px, py = player.rect.x, player.rect.y
            sx, sy = self.rect.x, self.rect.y
            if px < sx:
                xo = -min(sx - px, 300)
            else:
                xo = min(px - sx, 300)
            if py < sy:
                yo = -min(sy - py, 300)
            else:
                yo = min(py - sy, 300)
            offset = (xo, yo)
            game.other.append(dungeon_misc.GeomancerColumn(
                self.rect.x + offset[0], self.rect.y + offset[1], explode=t))
            if self.num > 10:
                found = False
                for i in game.other:
                    if type(i) == dungeon_misc.GeomancerColumn:
                        game.other.remove(i)
                        found = True
                    if found: break
                self.num -= 1


class Witch(BaseIllager):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.melee = True
        self.has_weapon = False
        self.name = 'Witch'
        self.weapon = type('WitchPotion',
                           (object,),
                           {'damage': 0, 'render': lambda game: ...})()
        self.fix()
        self.delay_damage = 150
        self.color_body = pygame.Color('purple')

    def attack(self, game):
        self.delaydamage += 1
        if self.delaydamage >= self.delay_damage and self.speed > 0:
            self.delaydamage = 0
            player = self.get_target(game)
            effect = random.choice([
                'poison', 'poison', 'poison',
                'weakness', 'weakness',
                'slowness'])
            potion = dungeon_misc.ThrowingPotion(
                (self.rect.x, self.rect.y),
                (player.rect.x, player.rect.y), self, effect)
            game.arrows.append(potion)


class RoyalGuard(BaseIllager):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.melee = True
        self.name = 'Royal Guard'
        self.weapon = type('SpikedClub',
                           (object,),
                           {'damage': 7, 'render': self.club_render})()
        self.fix()
        self.delay_damage = 100
        self.has_shield = True
        self.armor = 2
        self.spikecolor = pygame.Color('grey')

    def club_render(self, x, y, game):
        pygame.draw.line(game.screen, self.spikecolor,
                         (x, y), (x + 5, y + 10), 3)
        pygame.draw.circle(game.screen, self.spikecolor,
                           (x + 5, y + 10), 6)
        if self.has_shield:
            pygame.draw.lines(game.screen, pygame.Color('yellow'), True, [
                (self.rect.x - 5, self.rect.y + 5),
                (self.rect.x - 5, self.rect.y + 20),
                (self.rect.x + 5, self.rect.y + 20),
                (self.rect.x + 5, self.rect.y + 5)], 1)
            pygame.draw.rect(game.screen, pygame.Color('dark grey'),
                             pygame.Rect(self.rect.x - 4,
                                         self.rect.y + 6, 8, 13))

    def take_damage(self, damage):
        if self.has_shield:
            self.has_shield = False
            return
        else:
            super().take_damage(damage)


class SkeletonVanguard(RoyalGuard):  # Very similar to each other.
    def __init__(self, x, y):
        super().__init__(x, y)
        self.weapon = type('VanguardBlades',
                           (object,),
                           {'damage': 7, 'render': self.club_render})
        self.armor = 3
        self.body_color = pygame.Color('white')
        self.head_color = pygame.Color('white')
        self.arm_color = pygame.Color('white')
        self.name = 'Skeleton Vanguard'
        self.maintype = 'skeleton'
        self.secondtype = 'undead'
        self.place = dungeon_weapons.IronSword()
        self.fix()

    def club_render(self, x, y, game):
        self.place.render(x, y, game)
        if self.has_shield:
            pygame.draw.lines(game.screen, pygame.Color('yellow'), True, [
                (self.rect.x - 5, self.rect.y + 5),
                (self.rect.x - 5, self.rect.y + 20),
                (self.rect.x + 5, self.rect.y + 20),
                (self.rect.x + 5, self.rect.y + 5)], 1)
            pygame.draw.rect(game.screen, pygame.Color('dark grey'),
                             pygame.Rect(self.rect.x - 4,
                                         self.rect.y + 6, 8, 13))


class ZombieSpawner(BaseSpawner):
    mob = Zombie
    
    def draw(self, game):
        super().draw(game)
        pygame.draw.rect(game.screen, pygame.Color('light blue'),
                         pygame.Rect(self.rect.x + 5, self.rect.y + 2, 10, 16))


class SkeletonSpawner(BaseSpawner):
    mob = Skeleton
    
    def draw(self, game):
        super().draw(game)
        pygame.draw.rect(game.screen, pygame.Color('white'),
                         pygame.Rect(self.rect.x + 5, self.rect.y + 2, 10, 16))


class SpiderSpawner(BaseSpawner):
    mob = Spider
    
    def draw(self, game):
        super().draw(game)
        pygame.draw.rect(game.screen, pygame.Color(5, 5, 5, 255),
                         pygame.Rect(self.rect.x + 5, self.rect.y + 2, 10, 16))


class CreeperSpawner(BaseSpawner):
    mob = Creeper
    
    def draw(self, game):
        super().draw(game)
        pygame.draw.rect(game.screen, pygame.Color('green'),
                         pygame.Rect(self.rect.x + 5, self.rect.y + 2, 10, 16))


class TheCauldron(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.text = pygame.font.SysFont('', 20).render(
            'The Cauldron', 20, pygame.Color('black'))
        self.delay_damage = 5
        self.damage = 3
        self.delay_move = float('inf')
        self.summondelay = 0
        self.summon_delay = 100
        self.rect = pygame.Rect(x, y, 100, 100)
        self.hpmax = 200
        self.hp = self.hpmax

    def render(self, game):
        super().render(game)
        self.summondelay += 1
        if self.summondelay >= self.summon_delay:
            self.summondelay = 0
            game.enemies.append(ConjuredSlime(
                random.randint(self.rect.x - 30, self.rect.x + 160),
                random.randint(self.rect.y - 30, self.rect.y + 160)))

    def draw(self, game):
        pygame.draw.rect(game.screen, pygame.Color('black'), self.rect)
        pygame.draw.circle(game.screen, pygame.Color('purple'),
                           (self.rect.x + 20, self.rect.y + 20), 10)
        pygame.draw.circle(game.screen, pygame.Color('purple'),
                           (self.rect.x + 80, self.rect.y + 20), 10)
        pygame.draw.lines(game.screen, pygame.Color('purple'), False, [
            (self.rect.x + 10, self.rect.y + 70),
            (self.rect.x + 15, self.rect.y + 80),
            (self.rect.x + 25, self.rect.y + 90),
            (self.rect.x + 75, self.rect.y + 90),
            (self.rect.x + 85, self.rect.y + 80),
            (self.rect.x + 90, self.rect.y + 70)], 4)
        health_rect = pygame.Rect(self.rect.x - (self.hpmax // 2),
                                  self.rect.y - 5, int(self.hp * 2), 8)
        pygame.draw.rect(game.screen, pygame.Color('red'), health_rect)
        game.screen.blit(self.text, (self.rect.x - 5, self.rect.y - 20))

        if self.effects['fire'] > 0:
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 10, self.rect.y + 94),
                             (self.rect.x + 7, self.rect.y + 5), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 20, self.rect.y + 97),
                             (self.rect.x + 23, self.rect.y + 3), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 14, self.rect.y + 96),
                             (self.rect.x + 16, self.rect.y + 7), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 27, self.rect.y + 94),
                             (self.rect.x + 24, self.rect.y + 5), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 38, self.rect.y + 97),
                             (self.rect.x + 41, self.rect.y + 3), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 34, self.rect.y + 96),
                             (self.rect.x + 36, self.rect.y + 7), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 50, self.rect.y + 94),
                             (self.rect.x + 47, self.rect.y + 5), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 60, self.rect.y + 97),
                             (self.rect.x + 63, self.rect.y + 3), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 54, self.rect.y + 96),
                             (self.rect.x + 56, self.rect.y + 7), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 67, self.rect.y + 94),
                             (self.rect.x + 64, self.rect.y + 5), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 78, self.rect.y + 97),
                             (self.rect.x + 101, self.rect.y + 3), 4)
            pygame.draw.line(game.screen, pygame.Color('red'),
                             (self.rect.x + 84, self.rect.y + 96),
                             (self.rect.x + 96, self.rect.y + 7), 4)

        if self.speed == 0:
            if self.mode == 'ice':
                pygame.draw.rect(game.screen, pygame.Color('light blue'),
                                 pygame.Rect(self.rect.x + 2, self.rect.y + 2,
                                             self.rect.width - 4,
                                             self.rect.height - 4))
            elif self.mode == 'chains':
                for y in range(self.rect.y,
                               self.rect.y + self.rect.height, 10):
                    pygame.draw.line(game.screen, pygame.Color('grey'),
                                     (self.rect.x, y),
                                     (self.rect.x + self.rect.width, y), 3)


easy = [Zombie, Skeleton, Stray, Slime, Creeper, Spider, BabyZombie, Piglin]
medium = [Husk, Drowned, MossSkeleton, SpeedyZombie, Vindicator,
          Pillager, Enchanter, RoyalGuard, ArmoredZombie,
          ChickenJockey, CaveSpider, Iceologer, PiglinSword]
hard = [PlantZombie, FlamingSkeleton, Evoker, Geomancer,
        ChickenJockeyTower, Witch, Enderman, PiglinBrute]
very_hard = [Necromancer, SkeletonHorse, Wraith, RedstoneGolem]
actual_boss = [NamelessOne, RedstoneMonstrosity, TheCauldron]
spawners = [ZombieSpawner, SkeletonSpawner, SpiderSpawner, CreeperSpawner]
