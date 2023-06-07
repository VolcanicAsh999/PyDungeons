import pygame
import math
import dungeon_weapons
import dungeon_settings
import time
import random
from dungeon_misc import particle
import dungeon_arrows
import dungeon_chests
import dungeon_misc

pygame.init()


class HitBox:
    def __init__(self, x, y):
        self.rect = pygame.rect.Rect(x, y, 1, 1)

    def update(self, x, y, reach):
        self.rect = pygame.Rect(x - reach, y - reach, reach * 2, reach * 2)


class Player:
    def __init__(self, x, y, difficulty):
        self.difficulty = 0
        self.dif = difficulty
        self.dx = self.dy = 0
        self.width = 30
        self.height = 35
        self.rect = pygame.rect.Rect(x, y, self.width, self.height)
        self.x = x
        self.y = y
        self.hpmax = 40
        self.hp = self.hpmax
        self.weapon = None
        self.range = None
        self.consumable = None
        self.armor = None
        self.a1 = self.a2 = self.a3 = None
        self.ia1 = self.ia2 = self.ia3 = 0
        self.effects = {'speed': 0, 'slowness': 0, 'strength': 0, 'weakness': 0,
                        'resistance': 0, 'poison': 0, 'regeneration': 0, 'fire': 0}
        self.cooldown = 0
        self.rcooldown = 0
        self.delaymove = 0
        self.colliderect = HitBox(x, y)
        self.decreaseeffectslast = time.time()
        self.weapons = [None]
        self.ranges = [None]
        self.consumables = [None]
        self.armors = [None]
        self.artifacts = [None]
        self.indexarmor = 0
        self.indexweapon = 0
        self.indexrange = 0
        self.indexc = 0
        self.emeralds = 0
        self.level = 0
        self.level_prog = 0.0
        self.kills = 0
        self.arrows = 10
        self.power = 0
        self.nextartype = 'default'
        self.attack_speed = 0
        self.timelast = time.time()

    @property
    def power_(self):
        return self.power + ((self.dif - 1) * 15)

    def render(self, game):
        if self.hp <= 0:
            self.die(game)
            return

        if self.cooldown > 0:
            self.cooldown -= time.time() - self.timelast

        if self.rcooldown > 0:
            self.rcooldown -= time.time() - self.timelast

        self.timelast = time.time()

        if time.time() - self.decreaseeffectslast >= 1:
            self.decreaseeffectslast = time.time()
            for effect in self.effects.keys():
                if self.effects[effect] > 0:
                    self.effects[effect] -= 1
            if self.effects['poison'] > 0 and self.effects['poison'] % 2 == 0 and self.hp > 1:
                self.hp -= 1
            if self.effects['regeneration'] > 0 and self.effects['regeneration'] % 2 == 0:
                self.hp += 1
            if self.effects['fire'] > 0 and self.effects['fire'] % 2 == 0:
                self.hp -= 1

        for effect in self.effects.keys():
            if self.effects[effect] > 0 and effect != 'fire':
                particle.particle(
                    effect, self.rect.x, self.rect.x + 30, self.rect.y, self.rect.y + 35, game)

        if self.hp > self.hpmax:
            self.hp = self.hpmax

        for artifact in self.artifacts:
            if artifact:
                artifact.check_cooldown(game)

        self.draw(game)

    def delete_weapon(self):
        if self.weapon:
            self.weapon.salvage(self)
            self.weapons.remove(self.weapon)
            self.weapon = None
            self.nextweapon(amount=0)
        self.update_power()

    def delete_range(self):
        if self.range:
            self.range.salvage(self)
            self.ranges.remove(self.range)
            self.range = None
            self.nextrange(amount=0)
        self.update_power()

    def delete_armor(self, game):
        if self.armor:
            self.armor.salvage(self)
            self.armors.remove(self.armor)
            self.hpmax -= self.armor
            # self.armor = None
            self.nextarmor(game, amount=0)
        self.update_power()

    def increase(self):
        increase = 0
        if self.weapon:
            increase += (self.weapon._speed //
                         2) if self.weapon._speed > 0 else self.weapon._speed
        if self.range:
            increase += (self.range._speed //
                         2) if self.range._speed > 0 else self.range._speed
        if self.armor:
            increase += (self.armor._speed //
                         2) if self.armor._speed > 0 else self.armor._speed
        return increase

    def move(self, game, x=0, y=0):
        increase = self.increase()
        x2, y2 = x, y
        if x != 0:
            if self.effects['speed'] > 0:
                if x > 0:
                    x += 1
                elif x < 0:
                    x -= 1
            if self.effects['slowness'] > 0:
                if x > 0:
                    x -= 1
                elif x < 0:
                    x += 1
            if x >= 0:
                x += increase
            if x < 0:
                x -= increase
            if x2 < 0 and x >= 0:
                x = -1
            if x2 > 0 and x <= 0:
                x = 1
            self.rect.x += x
            '''for wall in game.walls:
                """if self.rect.colliderect(wall.rect):
                    self.rect.x -= x
                    return"""
                if (self.rect.x + 20 > wall.rect.x) and (self.rect.x - 5 < wall.rect.x + 20) and (self.rect.y + 25 > wall.rect.y) and (self.rect.y - 5 < wall.rect.y + 20):
                    self.rect.x -= x
                    return'''
            # self._move(game, x, y)
        if y != 0:
            if self.effects['speed'] > 0:
                if y > 0:
                    y += 1
                elif y < 0:
                    y -= 1
            if self.effects['slowness'] > 0:
                if y > 0:
                    y -= 1
                elif y < 0:
                    y += 1
            if y >= 0:
                y += increase
            if y < 0:
                y -= increase
            if y2 < 0 and y >= 0:
                y = -1
            if y2 > 0 and y <= 0:
                y = 1
            self.rect.y += y
            '''for wall in game.walls:
                """if self.rect.colliderect(wall.rect):
                    self.rect.y -= y
                    return"""
                if (self.rect.y + 25 > wall.rect.y) and (self.rect.y - 5 < wall.rect.y + 20) and (self.rect.x + 20 > wall.rect.x) and (self.rect.x - 5 < wall.rect.x + 20):
                    self.rect.y -= y
                    return'''
            # self._move(game, x, y)

    """def _move(self, game, x=0, y=0):
        if x != 0:
            '''for i in range(x):
                self.rect.x += (1 if x > 0 else -1)
                for wall in game.walls:
                    if self.rect.colliderect(wall.rect):
                        self.rect.x -= (1 if x > 0 else -1)
                        self._move(game, 0, y)
                        return'''
            self.rect.x += x
            for wall in game.walls:
                '''if self.rect.colliderect(wall.rect):
                    self.rect.x -= x
                    return'''
                if (self.rect.x + 20 > wall.rect.x) and (self.rect.x - 5 < wall.rect.x + 20) and (self.rect.y + 25 > wall.rect.y) and (self.rect.y - 5 < wall.rect.y + 20):
                    self.rect.x -= x
                    return
        if y != 0:
            '''for i in range(y):
                self.rect.y += (1 if y > 0 else -1)
                for wall in game.walls:
                    if self.rect.colliderect(wall.rect):
                        self.rect.y -= (1 if y > 0 else -1)
                        self._move(game, y, 0)
                        return'''
            self.rect.y += y
            for wall in game.walls:
                '''if self.rect.colliderect(wall.rect):
                    self.rect.y -= y
                    return'''
                if (self.rect.y + 25 > wall.rect.y) and (self.rect.y - 5 < wall.rect.y + 20) and (self.rect.x + 20 > wall.rect.x) and (self.rect.x - 5 < wall.rect.x + 20):
                    self.rect.y -= y
                    return"""  # makes movement choppy

    def attack(self, game):
        damage = 1
        if self.weapon:
            damage = self.weapon.damage
        if self.effects['strength'] > 0:
            damage += 2
        if self.effects['weakness'] > 0:
            damage -= 1
        cooldown = .5
        if self.weapon:
            cooldown = self.weapon.cooldown
        reach = 80
        if self.weapon:
            reach = self.weapon.reach
        knockback = 20
        if self.weapon:
            knockback = self.weapon.knockback
        self.colliderect.update(self.rect.x, self.rect.y, reach)
        for enemy in game.enemies:
            if pygame.sprite.collide_rect(self.colliderect, enemy.hitbox):
                if self.weapon:
                    self.weapon.attack(enemy, self, damage, knockback)
                else:
                    enemy.take_damage(damage)
                    enemy.knockback(knockback, self)
        for i in game.other:
            if type(i) == dungeon_misc.EmeraldPot:
                i.hit(self)
        for i in game.spawners:
            if pygame.sprite.collide_rect(self.colliderect, i):
                i.take_damage(1)
        self.cooldown = cooldown
        if self.attack_speed != 0:
            self.cooldown -= self.attack_speed
        dungeon_settings.weapon_swing.play()

    def take_damage(self, damage):
        damage += (1 - self.dif) * 3
        if self.effects['resistance'] > 0:
            damage -= 2
        if self.armor:
            damage = self.armor._protect(damage)
        if damage < 0:
            damage = 0
        self.hp -= damage

    def armor_use(self, enemy, game):
        if self.armor:
            self.armor.do_special(self, enemy, game)

    def knockback(self, knockback, player):
        if knockback > 0:
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

    def draw(self, game):
        pygame.draw.rect(game.screen, pygame.Color('blue'), pygame.Rect(
            self.rect.x + 10, self.rect.y + 15, 10, 15))  # body
        pygame.draw.circle(game.screen, pygame.Color(
            'brown'), (self.rect.x + 15, self.rect.y + 10), 5)  # head
        pygame.draw.line(game.screen, pygame.Color('brown'), (self.rect.x +
                         10, self.rect.y + 15), (self.rect.x + 5, self.rect.y + 20), 3)  # arm
        pygame.draw.line(game.screen, pygame.Color('brown'), (self.rect.x + 20,
                         self.rect.y + 15), (self.rect.x + 25, self.rect.y + 20), 3)  # arm
        health_rect = pygame.Rect(
            self.rect.x - 5, self.rect.y - 5, int(self.hp), 8)
        pygame.draw.rect(game.screen, pygame.Color(
            'red'), health_rect)  # hp bar

        if self.weapon:
            self.weapon.render(
                self.rect.x + 25, self.rect.y + 20, game)  # weapon image
            self.weapon.show_info(game.screen.get_width(
            ) - 100, game.screen.get_height() - 10, game)  # weapon info

        if self.range:
            self.range.render(self.rect.x + 5, self.rect.y +
                              20, game)  # range image
            self.range.show_info(game.screen.get_width(
            ) - 300, game.screen.get_height() - 10, game)  # range info

        if self.consumable:
            # consumable image (and text)
            self.consumable.render(self.rect.x, self.rect.y - 15, game)

        if self.armor:
            self.armor.render(self.rect.x + 10, self.rect.y +
                              15, game)  # armor image
            self.armor.show_info(game.screen.get_width(
            ) - 500, game.screen.get_height() - 10, game)  # armor info

        if self.a1:
            self.a1.render(100, 10, game)  # a1 image

        if self.a2:
            self.a2.render(200, 10, game)  # a2 image

        if self.a3:
            self.a3.render(300, 10, game)  # a3 image

        emerald_text = pygame.font.SysFont('', 20).render(
            str(self.emeralds), 1, pygame.Color('light green'))
        game.screen.blit(emerald_text, (20, 10))  # emeralds

        level_text = pygame.font.SysFont('', 20).render(
            str(int(self.level)), 1, pygame.Color('green'))
        # player level
        game.screen.blit(level_text, (game.screen.get_width() // 2, 5))

        kill_text = pygame.font.SysFont('', 20).render(
            str(self.kills), 1, pygame.Color('purple'))
        game.screen.blit(kill_text, (20, 30))  # kills

        arrow_text = pygame.font.SysFont('', 20).render(
            str(self.arrows), 1, pygame.Color('brown'))
        game.screen.blit(arrow_text, (20, 50))  # arrows

        power_text = pygame.font.SysFont('', 20).render(
            'Power: ' + str(self.power), 1, pygame.Color('white'))
        game.screen.blit(power_text, (20, 70))  # power

        pygame.draw.polygon(game.screen, pygame.Color('green'), [
                            (5, 10), (5, 20), (10, 25), (15, 20), (15, 10), (10, 5)])  # emerald pic

        pygame.draw.line(game.screen, pygame.Color(
            'brown'), (5, 50), (15, 60), 3)
        pygame.draw.circle(game.screen, pygame.Color(
            'light grey'), (5, 50), 3)  # arrow pic

        if self.effects['fire'] > 0:
            pygame.draw.line(game.screen, pygame.Color(
                'red'), (self.rect.x + 10, self.rect.y + 24), (self.rect.x + 7, self.rect.y + 5), 4)
            pygame.draw.line(game.screen, pygame.Color(
                'red'), (self.rect.x + 20, self.rect.y + 27), (self.rect.x + 23, self.rect.y + 3), 4)
            pygame.draw.line(game.screen, pygame.Color(
                'red'), (self.rect.x + 14, self.rect.y + 26), (self.rect.x + 16, self.rect.y + 7), 4)

    def getloot(self, loot, emerald, game):
        if not isinstance(loot, list):
            if issubclass(type(loot), dungeon_weapons.BaseMeleeWeapon):
                if True:
                    loot.cooldown -= (self.dif - 1)
                    loot.damage += (self.dif - 1) * 4
                    loot.reach += (self.dif - 1) * 10
                    loot.knockback += (self.dif - 1) * 20
                    loot.num += (self.dif - 1) * 2
                    loot._speed += (self.dif - 1)
                    self.weapons.append(loot)
                    game.message('You got the ' + loot.name + '!', 200)

            elif issubclass(type(loot), dungeon_weapons.BaseRangeWeapon):
                if True:
                    loot.arrow['damage'] += (self.dif - 1) * 3
                    loot.arrow['knockback'] += (self.dif - 1) * 20
                    loot.cooldown -= (self.dif - 1)
                    loot._speed += (self.dif - 1)
                    self.ranges.append(loot)
                    game.message('You got the ' + loot.name + '!', 200)

            elif issubclass(type(loot), dungeon_weapons.Consumable):
                self.consumables.append(loot)
                game.message('You got the ' + loot.name + '!', 200)

            elif issubclass(type(loot), dungeon_weapons.BaseArmor):
                loot.protect += (self.dif - 1) * 3
                loot._speed += (self.dif - 1)
                self.armors.append(loot)
                game.message('You got the ' + loot.name + '!', 200)

            elif issubclass(type(loot), dungeon_weapons.Artifact):
                self.artifacts.append(loot)
                game.message('You got the ' + loot.name + '!', 250)

            elif isinstance(loot, str):
                if ' arrows' in loot:
                    if True:
                        self.arrows += int(loot[:2])
                        if self.armor:
                            self.arrows += self.armor.arrows
                        game.message('You got ' + loot[:2] + ' Arrows!', 200)

                elif loot == 'emerald':
                    amount = random.randint(emerald[0], emerald[1])
                    self.emeralds += amount
                    game.message('You got ' + str(amount) + ' Emeralds!', 200)

        elif isinstance(loot, list):
            l = loot
            for loot in l:
                self.getloot(loot, emerald, game)

    def nextweapon(self, amount=1):
        self.indexweapon += amount
        if self.indexweapon > len(self.weapons) - 1:
            self.indexweapon = 0
        self.weapon = self.weapons[self.indexweapon]
        self.update_power()

    def nextrange(self, amount=1):
        self.indexrange += amount
        if self.indexrange > len(self.ranges) - 1:
            self.indexrange = 0
        self.range = self.ranges[self.indexrange]
        self.update_power()

    def nextc(self, amount=1):
        self.indexc += amount
        if self.indexc > len(self.consumables) - 1:
            self.indexc = 0
        self.consumable = self.consumables[self.indexc]
        self.update_power()

    def nextarmor(self, game, amount=1):
        if self.armor != None:
            self.hpmax -= self.armor.hp
        self.indexarmor += amount
        if self.indexarmor > len(self.armors) - 1:
            self.indexarmor = 0
        self.armor = self.armors[self.indexarmor]
        if self.armor != None:
            #self.armor.equip(game)
            self.hpmax += self.armor.hp
        self.update_power()

    def na(self, i, amount=1):
        if i == 1:
            self.ia1 += amount
            if self.ia1 > len(self.artifacts) - 1:
                self.ia1 = 0
            self.a1 = self.artifacts[self.ia1]
            if (self.a2 != None and self.a2 == self.a1) or (self.a3 != None and self.a3 == self.a1):
                self.na(1)
        elif i == 2:
            self.ia2 += amount
            if self.ia2 > len(self.artifacts) - 1:
                self.ia2 = 0
            self.a2 = self.artifacts[self.ia2]
            if (self.a1 != None and self.a2 == self.a1) or (self.a3 != None and self.a3 == self.a2):
                self.na(2)
        elif i == 3:
            self.ia3 += amount
            if self.ia3 > len(self.artifacts) - 1:
                self.ia3 = 0
            self.a3 = self.artifacts[self.ia3]
            if (self.a1 != None and self.a3 == self.a1) or (self.a2 != None and self.a3 == self.a2):
                self.na(3)
        self.update_power()

    def enchantw(self, game):
        if self.weapon and self.level >= 1:
            self.level = self.weapon.enchant(self.level, game)
        self.update_power()

    def enchantr(self, game):
        if self.range and self.level >= 1:
            self.level = self.range.enchant(self.level, game)
        self.update_power()

    def enchanta(self, game):
        if self.armor and self.level >= 1:
            self.level = self.armor.enchant(self.level, game)
        self.update_power()

    def get_xp(self, xp):
        self.level_prog += xp
        if self.level_prog >= 1:
            self.level_prog -= 1.0
            self.level += 1

    def special(self, game):
        if self.range and self.arrows > 0:
            if self.nextartype == 'default':
                a = self.range.arrow['type']
            elif self.nextartype == 'flame':
                a = dungeon_arrows.FlamingArrow
            elif self.nextartype == 'explode':
                a = dungeon_arrows.ExplodingArrow
            self.nextartype = 'default'
            self.range.shoot(game, self, a)
            self.rcooldown = self.range.cooldown
            if self.attack_speed != 0:
                self.rcooldown -= self.attack_speed
            self.arrows -= 1

    def special2(self, game):
        if self.consumable:
            self.consumable.use(game)
            self.consumables.remove(self.consumable)
            self.consumable = None
            self.nextc(amount=0)

    def kill(self):
        if self.weapon:
            self.kills += self.weapon._kills
        if self.range:
            self.kills += self.range._kills
        if self.armor:
            self.kills += self.armor._kills
        if self.a1:
            self.kills += self.a1._gives_kill
        if self.a2:
            self.kills += self.a2._gives_kill
        if self.a3:
            self.kills += self.a3._gives_kill
        #self.kills += 1

        self.difficulty += random.choice([1/14, 1/7])
        if self.dif == 2:
            self.difficulty += random.choice([0, 1/14])
        elif self.dif == 3:
            self.difficulty += random.choice([0, 1/14, 1/7, 1/7])
        if self.difficulty > 50:
            self.difficulty = 50

    def die(self, game):
        if dungeon_settings.FRIENDLY_MODE:
            chest = dungeon_chests.PlayerLootChest(
                self.rect.x, self.rect.y, self)
            game.chests.append(chest)
            game.killall()
        self.dx = self.dy = 0
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.hpmax = 40
        self.hp = self.hpmax
        self.up = self.down = self.right = self.left = False
        self.weapon = None
        self.weapons = [None]
        self.level = 0
        self.level_prog = 0.0
        self.indexweapon = 0
        self.indexrange = 0
        self.indexc = 0
        self.emeralds = 0
        self.effects = {'speed': 0, 'slowness': 0, 'strength': 0, 'weakness': 0,
                        'resistance': 0, 'poison': 0, 'regeneration': 0, 'fire': 0}
        self.range = None
        self.ranges = [None]
        self.consumable = None
        self.consumables = [None]
        self.armors = [None]
        self.arrows = 10
        self.armor = None
        self.ia1 = self.ia2 = self.ia3 = 0
        self.a1 = self.a2 = self.a3 = None
        self.artifacts = [None]
        self.indexarmor = 0
        self.kills = 0
        self.difficulty = 0

    def usea(self, i, game):
        if hasattr(self.a1, 'using') and self.a1.using and i == 1:
            self.a1.cancel()
        elif hasattr(self.a2, 'using') and self.a2.using and i == 2:
            self.a2.cancel()
        elif hasattr(self.a3, 'using') and self.a3.using and i == 3:
            self.a3.cancel()
        elif i == 1 and self.a1 and self.a1.cooldown <= 0:
            try:
                self.a1.use(game)
            except TypeError:
                self.a1.use(game, 1)
        elif i == 2 and self.a2 and self.a2.cooldown <= 0:
            try:
                self.a2.use(game)
            except TypeError:
                self.a2.use(game, 2)
        elif i == 3 and self.a3 and self.a3.cooldown <= 0:
            try:
                self.a3.use(game)
            except TypeError:
                self.a3.use(game, 3)

    def update_power(self):
        power = 0
        num = 0
        if self.weapon:
            power += self.weapon.get_power()
            num += 1
        if self.range:
            power += self.range.get_power()
            num += 1
        if self.armor:
            power += self.armor.get_power()
            num += 1
        if self.a1:
            power += self.a1.get_power()
            num += 1
        if self.a2:
            power += self.a2.get_power()
            num += 1
        if self.a3:
            power += self.a3.get_power()
            num += 1
        if num == 0:
            self.power = 0
            return
        self.power = power // num
