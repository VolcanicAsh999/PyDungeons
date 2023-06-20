import pygame
import random
import dungeon_arrows
import dungeon_misc
import dungeon_settings
import dungeon_helpful
import dungeon_gui
import dungeon_chests
import time
import math
from threading import Thread


class Help:
    def __init__(self, r):
        self.rect = r


def distance_to(target1, target2):
    return math.dist((target1.rect.x, target1.rect.y), (target2.rect.x, target2.rect.y))


class BaseMeleeWeapon:
    enchants = ['Leeching', 'Sharpness', 'Smiting', 'Illager\'s Bane', 'Radiance', 'Chains', 'Anima Conduit',
                'Ambush', 'Comitted', 'Echo', 'Fire Aspect', 'Freezing', 'Leeching', 'Looting', 'Poison Cloud',
                'Prospector', 'Rampaging', 'Soul Siphon', 'Stunning', 'Thundering', 'Weakening', 'Critical Hit',
                'Exploding', 'Gravity', 'Shockwave', 'Swirling', 'Void Strike', 'Refreshment', 'Busy Bee', 'Dynamo',
                'Guarding Strike', 'Pain Cycle', 'Unchanting']
    
    def __repr__(self):
        return f'{self.name}(damage={self.damage}, cooldown={self.cooldown}, reach={self.reach}, knockback={self.knockback}, speed={self._speed}, power={self.pow})'

    def __init__(self, pow):
        self.damage = 0
        self.cooldown = 0
        self.reach = 0
        self.knockback = 0
        self.descript = ''
        self.name = ''
        self.x = 0
        self.y = 0
        self._spent = 0
        self._speed = 0
        self._kills = 0
        self.pow = 0
        self._bonus = []
        self.slots = {1: None, 2: None, 3: None}
        self.slotlevel = {1: 0, 2: 0, 3: 0}
        self.cools = {'echo': 0, 'rampaging': 0}
        self.lasttime = time.time()
        self.bees = []
        self.stacked = 0
        self.randomize_enchants()

    def randomize_enchants(self):
        self.slots[1] = random.choice(BaseMeleeWeapon.enchants)
        self.slots[2] = random.choice(BaseMeleeWeapon.enchants)
        self.slots[3] = random.choice(BaseMeleeWeapon.enchants)

    def show_info(self, x, y, game):
        text1 = pygame.font.SysFont(self.name, 20)
        text2 = []
        for text in self.descript:
            text2.append(pygame.font.SysFont(text, 20).render(
                text, 1, pygame.Color('black')))
        game.screen.blit(text1.render(
            self.name, 1, pygame.Color('black')), (x, y - 20))
        for text in range(len(text2)):
            game.screen.blit(text2[text], (x, y - ((text + 2) * 20)))

    def render(self, x, y, game):
        self.x = x
        self.y = y
        for key, val in self.cools.items():
            if val > 0:
                self.cools[key] -= time.time() - self.lasttime
        if self.cools['rampaging'] < 0:
            game.player.attack_speed += .5
        self.draw(game)
        self.lasttime = time.time()

    def draw(self, game):
        pass

    def salvage(self, player):
        player.emeralds += random.randint(13, 17)
        player.level += self._spent

    def enchant(self, game):
        index = dungeon_gui.get_enchant(self, game)
        if game.player.level <= self.slotlevel[index]: return game.player.level
        self._spent += self.slotlevel[index] + 1
        self.slotlevel[index] += 1
        self.update_descript()
        return game.player.level - self.slotlevel[index]

    def update_descript(self):
        if type(self.damage) == float:
            self.damage = random.choice([int(self.damage), int(self.damage) + 1])
        if self.damage < 1: self.damage = 1
        self.descript = ['', '', '', '', '', '', '']
        self.descript[1] = f'Cooldown: {self.cooldown}'
        self.descript[3] = f'Damage: {self.damage}'
        self.descript[2] = f'Reach: {self.reach}'
        self.descript[0] = f'Knockback: {self.knockback}'
        self.descript[4] = f'Speed increase: {self._speed}'
        self.descript[5] = f'Power: {self.pow}'
        if self.slotlevel[1] > 0:
            self.descript.append(f'{self.slots[1]} [{self.slotlevel[1]}')
        if self.slotlevel[2] > 0:
            self.descript.append(f'{self.slots[2]} [{self.slotlevel[2]}')
        if self.slotlevel[3] > 0:
            self.descript.append(f'{self.slots[3]} [{self.slotlevel[3]}')
        for i in self._bonus:
            self.descript.append(i)

    def attack(self, enemy, player, damage, knockback, game):
        enemy.take_damage(damage)
        enemy.knockback(knockback, player)
        dungeon_settings.weapon_hit.play()
        if 'Heals nearby allies' in self._bonus and random.randint(0, 4) == 0:
            for x in game.helpfuls:
                if distance_to(x, game.player) < 100:
                    x.hp += 1
            player.hp += 1
        if 'Chains mobs' in self._bonus and random.randint(1, 10) < 4:
            enemy.give_unmoving(1, 'chains')
        if 'Steals health on hit' in self._bonus:
            player.hp += round(damage * .04)
        if 'Extra damage to undead' in self._bonus and enemy.secondtype == 'undead':
            enemy.take_damage(damage * .2)
        if 'Pulls in mobs' in self._bonus:
            for i in game.enemies:
                for j in range(5):
                    if self.x < i.rect.x:
                        i.rect.x -= 3
                    else:
                        i.rect.x += 3
                    if self.y < i.rect.y:
                        i.rect.y -= 3
                    else:
                        i.rect.y += 3

                i.hitbox.update(i.rect.x, i.rect.y, i.reach)
            
        if 'Extra damage to unsuspecting enemies' in self._bonus and enemy.get_target(player._game) != player:
            enemy.take_damage(damage * .2)

        enemy.give_unmoving(random.uniform(max(self.cooldown-.1, .1), max(self.cooldown+.1, .3)), 'got whacked boi')
        
        self.check_enchants('attack', player, enemy, damage, knockback, game)

    def speed(self, amount):
        self._speed += amount

    def get_power(self):
        return self.pow

    def check_enchants(self, trigger, player, enemy=None, damage=0, knockback=0, game=None):
        if trigger == 'roll':
            for i in range(1, 4):
                if self.slotlevel[i] == 1:  # level 1 enchants
                    if self.slots[i] == 'Dynamo' and self.stacked < 20:
                        self.stacked += 1
                elif self.slotlevel[i] == 2:
                    if self.slots[i] == 'Dynamo' and self.stacked < 20:
                        self.stacked += 1
                elif self.slotlevel[i] == 3:
                    if self.slots[i] == 'Dynamo' and self.stacked < 20:
                        self.stacked += 1
        elif trigger == 'attack':
            for i in range(1, 4):
                if self.slotlevel[i] == 1:  # level 1 enchants
                    if self.slots[i] == 'Chains' and random.randint(1, 10) < 4:
                        enemy.give_unmoving(1, 'chains')
                    elif self.slots[i] == 'Sharpness':
                        enemy.take_damage(damage * .1)
                    elif self.slots[i] == 'Smiting' and enemy.secondtype == 'undead':
                        enemy.take_damage(damage * .2)
                    elif self.slots[i] == 'Illager\'s Bane' and enemy.maintype == 'illager':
                        enemy.take_damage(damage * .2)
                    elif self.slots[i] == 'Radiance' and random.randint(0, 4) == 0:
                        for x in game.helpfuls:
                            if distance_to(x, player) < 100:
                                x.hp += 1 + (self.pow * .02)
                        player.hp += 1 + (self.pow * .02)
                    elif self.slots[i] == 'Leeching':
                        player.hp += (damage * .04)
                    elif self.slots[i] == 'Anima Conduit':
                        if enemy.hp <= 0:
                            player.kills += 1
                            player.hp += enemy.hpmax * .02
                    elif self.slots[i] == 'Ambush' and enemy.get_target(game) != player:
                        enemy.take_damage(damage * .2)
                    elif self.slots[i] == 'Commited':
                        enemy.take_damage(((damage + enemy.hpmax - enemy.hp) / enemy.hpmax) * 50)
                    elif self.slots[i] == 'Echo' and self.cools['echo'] <= 0:
                        enemy.take_damage(damage)
                        self.cools['echo'] = 5
                    elif self.slots[i] == 'Fire Aspect':
                        enemy.effects_['fire'] = (3, 1 + (self.pow * .02))
                    elif self.slots[i] == 'Freezing':
                        enemy.effects_['freezing'] = (3, .8)
                    elif self.slots[i] == 'Looting' and enemy.hp <= 0:
                        enemy.luck_cons += 100
                    elif self.slots[i] == 'Poison Cloud':
                        game.other.append(dungeon_misc.PoisonCloud_(self.x, self.y, 1 + (self.pow * .02)))
                    elif self.slots[i] == 'Prospector' and enemy.hp <= 0:
                        enemy.luck_ems += 100
                    elif self.slots[i] == 'Rampaging' and self.cools['rampaging'] < 0 and random.randint(1, 10) == 1:
                        player.attack_speed -= .5
                        self.cools['rampaging'] = 5
                    elif self.slots[i] == 'Soul Siphon' and enemy.hp <= 0 and random.randint(1, 10) == 1:
                        player.kills += 3
                    elif self.slots[i] == 'Stunning' and random.randint(1, 100) < 6:
                        enemy.give_unmoving(1, 'stunned')
                    elif self.slots[i] == 'Thundering' and random.randint(1, 10) < 4:
                        for i in range(20):
                            game.play()
                            pygame.draw.line(game.screen, pygame.Color('light blue'), (self.x, self.y), (self.x + random.randint(-5, 5), self.y - 30 + random.randint(-10, 5)), 4)
                            pygame.display.update()
                        for i in game.enemies:
                            if math.dist((i.rect.x, i.rect.y), (self.x, self.y)) < 60:
                                enemy.take_damage(3 + (self.pow * .01))
                    elif self.slots[i] == 'Weakening':
                        for i in game.enemies:
                            if math.dist((i.rect.x, i.rect.y), (self.x, self.y)) < 100:
                                enemy.effects_['weakened'] = (5, .8)
                    elif self.slots[i] == 'Critical Hit' and random.randint(0, 100) < 11:
                        enemy.take_damage(damage * 2)
                    elif self.slots[i] == 'Exploding' and enemy.hp <= 0:
                        for i in game.enemies:
                            if math.dist((i.rect.x, i.rect.y), (enemy.rect.x, enemy.rect.y)) < 70:
                                i.take_damage(enemy.hpmax * .2)
                    elif self.slots[i] == 'Gravity':
                        for i in game.enemies:
                            for j in range(5):
                                if self.x < i.rect.x:
                                    i.rect.x -= 3
                                else:
                                    i.rect.x += 3
                                if self.y < i.rect.y:
                                    i.rect.y -= 3
                                else:
                                    i.rect.y += 3
                            i.hitbox.update(i.rect.x, i.rect.y, i.reach)
                    elif (self.slots[i] == 'Shockwave' or self.slots[i] == 'Swirling') and random.randint(0, 5) == 0:  # Make them the same because simplicity
                        for i in game.enemies:
                            if math.dist((i.rect.x, i.rect.y), (self.x, self.y)) < 100:
                                enemy.take_damage(2 + (self.pow * .02))
                    elif self.slots[i] == 'Void Strike':
                        if enemy.effects_['void strike'][0] < 0:
                            enemy.effects_['void strike'] = (4,1)
                        else:
                            if enemy.effects_['void strike'][0] >= 1:
                                time = 4 - enemy.effects_['void strike'][0]
                                enemy.take_damage(((time/3) * 2) * damage)
                            else:
                                enemy.take_damage(2 * damage)
                            enemy.effects_['void strike'] = (-1,1)
                    elif self.slots[i] == 'Refreshment' and enemy.hp <= 0:
                        if player.potion_cooldown >= 1:
                            player.potion_cooldown -= 1
                    elif self.slots[i] == 'Busy Bee' and random.randint(1, 10) < 3:
                        bee = dungeon_helpful.Bee(self.x, self.y, self.pow)
                        self.bees.append(bee)
                        game.helpfuls.append(bee)
                        if len(self.bees) > 3:
                            game.helpfuls.remove(self.bees.pop(0))
                    elif self.slots[i] == 'Dynamo' and self.stacked > 0:
                        extra = damage + ((self.stacked - 1) * (damage * .5))
                    elif self.slots[i] == 'Guarding Strike':
                        player.effects_['guarding strike'] = (2, .5)
                    elif self.slots[i] == 'Pain Cycle':
                        if player._pain >= 5:
                            player._pain = 0
                            enemy.take_damage(3 * damage)
                        else:
                            player.hp *= .97
                            player._pain += 1
                    elif self.slots[i] == 'Unchanting' and enemy.enchants:
                        enemy.take_damage(damage * .5)
                elif self.slotlevel[i] == 2:  # level 2 enchants
                    if self.slots[i] == 'Chains' and random.randint(1, 10) < 4:
                        enemy.give_unmoving(2, 'chains')
                    elif self.slots[i] == 'Sharpness':
                        enemy.take_damage(damage * .21)
                    elif self.slots[i] == 'Smiting' and enemy.secondtype == 'undead':
                        enemy.take_damage(damage / 3)
                    elif self.slots[i] == 'Illager\'s Bane' and enemy.maintype == 'illager':
                        enemy.take_damage(damage / 3)
                    elif self.slots[i] == 'Radiance' and random.randint(0, 4) == 0:
                        for x in game.helpfuls:
                            if distance_to(x, player) < 100:
                                x.hp += 2 + (self.pow * .025)
                        player.hp += 2 + (self.pow * .025)
                    elif self.slots[i] == 'Leeching':
                        player.hp += (damage * .06)
                    elif self.slots[i] == 'Anima Conduit':
                        if enemy.hp <= 0:
                            player.kills += 1
                            player.hp += enemy.hpmax * .04
                    elif self.slots[i] == 'Ambush' and enemy.get_target(game) != player:
                        enemy.take_damage(damage * .4)
                    elif self.slots[i] == 'Commited':
                        enemy.take_damage(((damage + enemy.hpmax - enemy.hp) / enemy.hpmax) * 75)
                    elif self.slots[i] == 'Echo' and self.cools['echo'] <= 0:
                        enemy.take_damage(damage)
                        self.cools['echo'] = 4
                    elif self.slots[i] == 'Fire Aspect':
                        enemy.effects_['fire'] = (3, 2 + (self.pow * .02))
                    elif self.slots[i] == 'Freezing':
                        enemy.effects_['freezing'] = (3, .6)
                    elif self.slots[i] == 'Looting':
                        enemy.luck_cons += 200
                    elif self.slots[i] == 'Poison Cloud':
                        game.other.append(dungeon_misc.PoisonCloud_(self.x, self.y, 2 + (self.pow * .025)))
                    elif self.slots[i] == 'Prospector' and enemy.hp <= 0:
                        enemy.luck_ems += 200
                    elif self.slots[i] == 'Rampaging' and self.cools['rampaging'] < 0 and random.randint(1, 10) == 1:
                        player.attack_speed -= .5
                        self.cools['rampaging'] = 10
                    elif self.slots[i] == 'Soul Siphon' and enemy.hp <= 0 and random.randint(1, 10) == 1:
                        player.kills += 6
                    elif self.slots[i] == 'Stunning' and random.randint(1, 100) < 11:
                        enemy.give_unmoving(1, 'stunned')
                    elif self.slots[i] == 'Thundering' and random.randint(1, 10) < 4:
                        for i in range(20):
                            game.play()
                            pygame.draw.line(player._game.screen, pygame.Color('light blue'), (self.x, self.y), (self.x + random.randint(-5, 5), self.y - 30 + random.randint(-10, 5)), 4)
                            pygame.display.update()
                        for i in game.enemies:
                            if math.dist((i.rect.x, i.rect.y), (self.x, self.y)) < 60:
                                enemy.take_damage(4 + (self.pow * .02))
                    elif self.slots[i] == 'Weakening':
                        for i in game.enemies:
                            if math.dist((i.rect.x, i.rect.y), (self.x, self.y)) < 100:
                                enemy.effects_['weakened'] = (5, .7)
                    elif self.slots[i] == 'Critical Hit' and random.randint(0, 100) < 16:
                        enemy.take_damage(damage * 2)
                    elif self.slots[i] == 'Exploding' and enemy.hp <= 0:
                        for i in game.enemies:
                            if math.dist((i.rect.x, i.rect.y), (enemy.rect.x, enemy.rect.y)) < 70:
                                i.take_damage(enemy.hpmax * .4)
                    elif self.slots[i] == 'Gravity':
                        for i in game.enemies:
                            for j in range(6):
                                if self.x < i.rect.x:
                                    i.rect.x -= 4
                                else:
                                    i.rect.x += 4
                                if self.y < i.rect.y:
                                    i.rect.y -= 4
                                else:
                                    i.rect.y += 4
                            i.hitbox.update(i.rect.x, i.rect.y, i.reach)
                    elif (self.slots[i] == 'Shockwave' or self.slots[i] == 'Swirling') and random.randint(0, 5) == 0:  # Make them the same because simplicity
                        for i in game.enemies:
                            if math.dist((i.rect.x, i.rect.y), (self.x, self.y)) < 100:
                                enemy.take_damage(3 + (self.pow * .03))
                    elif self.slots[i] == 'Void Strike':
                        if enemy.effects_['void strike'][0] < 0:
                            enemy.effects_['void strike'] = (4,1)
                        else:
                            if enemy.effects_['void strike'][0] >= 1:
                                time = 4 - enemy.effects_['void strike'][0]
                                enemy.take_damage(((time/3) * 4) * damage)
                            else:
                                enemy.take_damage(4 * damage)
                            enemy.effects_['void strike'] = (-1,1)
                    elif self.slots[i] == 'Refreshment' and enemy.hp <= 0:
                        if player.potion_cooldown >= 2:
                            player.potion_cooldown -= 2
                    elif self.slots[i] == 'Busy Bee' and random.randint(1, 10) < 4:
                        bee = dungeon_helpful.Bee(self.x, self.y, self.pow)
                        self.bees.append(bee)
                        game.helpfuls.append(bee)
                        if len(self.bees) > 3:
                            game.helpfuls.remove(self.bees.pop(0))
                    elif self.slots[i] == 'Dynamo' and self.stacked > 0:
                        extra = (damage * 1.25) + ((self.stacked - 1) * (damage * .75))
                    elif self.slots[i] == 'Guarding Strike':
                        player.effects_['guarding strike'] = (2, .5)
                    elif self.slots[i] == 'Pain Cycle':
                        if player._pain >= 5:
                            player._pain = 0
                            enemy.take_damage(4 * damage)
                        else:
                            player.hp *= .97
                            player._pain += 1
                    elif self.slots[i] == 'Unchanting' and enemy.enchants:
                        enemy.take_damage(damage * .75)
                elif self.slotlevel[i] == 3:  # level 3 enchants
                    if self.slots[i] == 'Chains' and random.randint(1, 10) < 4:
                        enemy.give_unmoving(3, 'chains')
                    elif self.slots[i] == 'Sharpness':
                        enemy.take_damage(damage / 3)
                    elif self.slots[i] == 'Smiting' and enemy.secondtype == 'undead':
                        enemy.take_damage(damage * .4)
                    elif self.slots[i] == 'Illager\'s Bane' and enemy.maintype == 'illager':
                        enemy.take_damage(damage * .4)
                    elif self.slots[i] == 'Radiance' and random.randint(0, 4) == 0:
                        for x in game.helpfuls:
                            if distance_to(x, player) < 100:
                                x.hp += 3 + (self.pow * .03)
                        player.hp += 3 + (self.pow * .03)
                    elif self.slots[i] == 'Leeching':
                        player.hp += (damage * .08)
                    elif self.slots[i] == 'Anima Conduit':
                        if enemy.hp <= 0:
                            player.kills += 1
                            player.hp += enemy.hpmax * .06
                    elif self.slots[i] == 'Ambush' and enemy.get_target(game) != player:
                        enemy.take_damage(damage * .6)
                    elif self.slots[i] == 'Commited':
                        enemy.take_damage(((damage + enemy.hpmax - enemy.hp) / enemy.hpmax) * 100)
                    elif self.slots[i] == 'Echo' and self.cools['echo'] <= 0:
                        enemy.take_damage(damage)
                        self.cools['echo'] = 3
                    elif self.slots[i] == 'Fire Aspect':
                        enemy.effects_['fire'] = (3, 3 + (self.pow * .03))
                    elif self.slots[i] == 'Freezing':
                        enemy.effects_['freezing'] = (3, .4)
                    elif self.slots[i] == 'Looting':
                        enemy.luck_cons += 300
                    elif self.slots[i] == 'Poison Cloud':
                        player._game.other.append(dungeon_misc.PoisonCloud_(self.x, self.y, 3 + (self.pow * .03)))
                    elif self.slots[i] == 'Prospector' and enemy.hp <= 0:
                        enemy.luck_ems += 300
                    elif self.slots[i] == 'Rampaging' and self.cools['rampaging'] < 0 and random.randint(1, 10) == 1:
                        player.attack_speed -= .5
                        self.cools['rampaging'] = 15
                    elif self.slots[i] == 'Soul Siphon' and enemy.hp <= 0 and random.randint(1, 10) == 1:
                        player.kills += 9
                    elif self.slots[i] == 'Stunning' and random.randint(1, 100) < 16:
                        enemy.give_unmoving(1, 'stunned')
                    elif self.slots[i] == 'Thundering' and random.randint(1, 10) < 4:
                        for i in range(20):
                            game.play()
                            pygame.draw.line(game.screen, pygame.Color('light blue'), (self.x, self.y), (self.x + random.randint(-5, 5), self.y - 30 + random.randint(-10, 5)), 4)
                            pygame.display.update()
                        for i in game.enemies:
                            if math.dist((i.rect.x, i.rect.y), (self.x, self.y)) < 60:
                                enemy.take_damage(5 + (self.pow * .03))
                    elif self.slots[i] == 'Weakening':
                        for i in game.enemies:
                            if math.dist((i.rect.x, i.rect.y), (self.x, self.y)) < 100:
                                enemy.effects_['weakened'] = (5, .6)
                    elif self.slots[i] == 'Critical Hit' and random.randint(0, 100) < 21:
                        enemy.take_damage(damage * 2)
                    elif self.slots[i] == 'Exploding' and enemy.hp <= 0:
                        for i in game.enemies:
                            if math.dist((i.rect.x, i.rect.y), (enemy.rect.x, enemy.rect.y)) < 70:
                                i.take_damage(enemy.hpmax * .6)
                    elif self.slots[i] == 'Gravity':
                        for i in game.enemies:
                            for j in range(8):
                                if self.x < i.rect.x:
                                    i.rect.x -= 4
                                else:
                                    i.rect.x += 4
                                if self.y < i.rect.y:
                                    i.rect.y -= 4
                                else:
                                    i.rect.y += 4
                            i.hitbox.update(i.rect.x, i.rect.y, i.reach)
                    elif (self.slots[i] == 'Shockwave' or self.slots[i] == 'Swirling') and random.randint(0, 5) == 0:  # Make them the same because simplicity
                        for i in game.enemies:
                            if math.dist((i.rect.x, i.rect.y), (self.x, self.y)) < 100:
                                enemy.take_damage(4 + (self.pow * .04))
                    elif self.slots[i] == 'Void Strike':
                        if enemy.effects_['void strike'][0] < 0:
                            enemy.effects_['void strike'] = (4,1)
                        else:
                            if enemy.effects_['void strike'][0] >= 1:
                                time = 4 - enemy.effects_['void strike'][0]
                                enemy.take_damage(((time/3) * 6) * damage)
                            else:
                                enemy.take_damage(6 * damage)
                            enemy.effects_['void strike'] = (-1,1)
                    elif self.slots[i] == 'Refreshment' and enemy.hp <= 0:
                        if player.potion_cooldown >= 3:
                            player.potion_cooldown -= 3
                    elif self.slots[i] == 'Busy Bee' and random.randint(1, 10) < 5:
                        bee = dungeon_helpful.Bee(self.x, self.y, self.pow)
                        self.bees.append(bee)
                        game.helpfuls.append(bee)
                        if len(self.bees) > 3:
                            game.helpfuls.remove(self.bees.pop(0))
                    elif self.slots[i] == 'Dynamo' and self.stacked > 0:
                        extra = (damage * 1.5) + ((self.stacked - 1) * damage)
                    elif self.slots[i] == 'Guarding Strike':
                        player.effects_['guarding strike'] = (2, .5)
                    elif self.slots[i] == 'Pain Cycle':
                        if player._pain >= 5:
                            player._pain = 0
                            enemy.take_damage(5 * damage)
                        else:
                            player.hp *= .97
                            player._pain += 1
                    elif self.slots[i] == 'Unchanting' and enemy.enchants:
                        enemy.take_damage(damage)

    def roll(self, game):
        self.check_enchants('roll', game.player, game)
    

class BaseRangeWeapon:
    enchants = ['Anima Conduit', 'Accelerate', 'Artifact Charge', 'Bonus Shot', 'Enigma Resonator', 'Fuse Shot', 'Growing', 'Infinity', 'Multishot', 'Piercing',
                'Poison Cloud', 'Power', 'Punch', 'Radiance Shot', 'Rapid Fire', 'Ricochet', 'Supercharge', 'Unchanting', 'Wild Rage', 'Chain Reaction', 'Gravity',
                'Tempo Theft', 'Void Strike', 'Levitation Shot', 'Overcharge', 'Shock Web', 'Burst Bowstring', 'Cooldown Shot', 'Dipping Poison', 'Dynamo', 'Roll Charge',
                'Weakening']
    
    def __repr__(self):
        return f'{self.name}(cooldown = {self.cooldown}, damage={self.arrow["damage"]}, knockback={self.arrow["knockback"]}, type={self.arrow["name"]})'

    def __init__(self, pow):
        self.numshoot = 1
        self.arrow = {'type': dungeon_arrows.Arrow, 'damage': pow,
                      'knockback': 20, 'name': 'Normal Arrow'}
        self.cooldown = .4
        self.x = 0
        self.y = 0
        self.descript = ''
        self.name = ''
        self._speed = 0
        self._kills = 0
        self._bonus = []
        self._amount_chained = 0
        self._enchant = 0
        self._spent = 0
        self._is_increased = False
        self.pow = pow
        self.slots = {1: None, 2: None, 3: None}
        self.slotlevels = {1: 0, 2: 0, 3: 0}
        self.cools = {'accelerate': [0,0]}
        self.randomize_enchants()
        self.update_descript()

    @property
    def slotlevel(self): return self.slotlevels

    def cooldown_mul(self):
        return 1 - self.cools['accelerate'][1]

    def randomize_enchants(self):
        self.slots[1] = random.choice(BaseRangeWeapon.enchants)
        self.slots[2] = random.choice(BaseRangeWeapon.enchants)
        self.slots[3] = random.choice(BaseRangeWeapon.enchants)

    def get_ench(self, ench):
        if self.slots[1] == ench: return self.slotlevel[1]
        elif self.slots[2] == ench: return self.slotlevel[2]
        elif self.slots[3] == ench: return self.slotlevel[3]
        return 0

    def shoot(self, game, player, t):
        arrow = t((player.rect.x, player.rect.y), pygame.mouse.get_pos(), self.arrow['damage'] + self._is_increased, self.arrow['knockback'], player, chain=self.get_ench('Chain Reaction'), growing=self.get_ench('Growing'))
        game.arrows.append(arrow)
        dungeon_settings.bow_shoot.play()
        self.check_enchants('shot', player, game, arrow=arrow)
        if self.get_ench('Infinity') and random.randint(1, 100) < 1 + (self.get_ench('Infinity') * 16):
            game.player.arrows += 1

    def render(self, x, y, game):
        self.x = x
        self.y = y
        for key, val in self.cools.items():
            if val[0] > 0:
                self.cools[key][0] -= time.time() - self.lasttime
                if self.cools[key][0] <= 0:
                    self.cools[key][1] = 0
        self.lasttime = time.time()
        
        self._is_increased = False
        self.draw(game)

    def show_info(self, x, y, game):
        text1 = pygame.font.SysFont(self.name, 20)
        text2 = []
        for text in self.descript:
            text2.append(pygame.font.SysFont(text, 20).render(
                text, 1, pygame.Color('black')))
        game.screen.blit(text1.render(
            self.name, 1, pygame.Color('black')), (x, y - 20))
        for text in range(len(text2)):
            game.screen.blit(text2[text], (x, y - ((text + 2) * 20)))

    def draw(self, game):
        pass

    def enchant(self, game):
        index = dungeon_gui.get_enchant(self, game)
        if game.player.level <= self.slotlevel[index]: return game.player.level
        self._spent += self.slotlevel[index] + 1
        self.slotlevel[index] += 1
        self.update_descript()
        return game.player.level - self.slotlevel[index]

    def chain(self):
        if self._amount_chained == 0:
            self._amount_chained = 1
        else:
            self._amount_chained += 0.1

    def update_descript(self):
        if self.arrow['damage'] < 1: self.arrow['damage'] = 1
        self.descript = ['', '', '', '', '']
        self.descript[0] = f'Arrow type: {self.arrow["name"]}'
        self.descript[1] = f'Arrow damage: {self.arrow["damage"]}'
        self.descript[2] = f'Arrow knockback: {self.arrow["knockback"]}'
        self.descript[3] = f'Cooldown: {self.cooldown}'
        self.descript[4] = f'Power: {self.pow}'
        if self._bonus:
            self.descript += self._bonus
        if self.slotlevel[1] > 0:
            self.descript.append(f'{self.slots[1]} [{self.slotlevel[1]}')
        if self.slotlevel[2] > 0:
            self.descript.append(f'{self.slots[2]} [{self.slotlevel[2]}')
        if self.slotlevel[3] > 0:
            self.descript.append(f'{self.slots[3]} [{self.slotlevel[3]}')

    def salvage(self, player):
        player.emeralds += random.randint(13, 17)
        player.level += self._spent

    def check_enchants(self, trigger, player, game, enemy=None):
        if trigger == 'soul':
            for i in range(1, 4):
                if self.slotlevel[i] == 1:
                    if self.slots[i] == 'Anima Conduit':
                        player.hp *= 1.04
                elif self.slotlevel[i] == 2:
                    if self.slots[i] == 'Anima Conduit':
                        player.hp *= 1.06
                elif self.slotlevel[i] == 3:
                    if self.slots[i] == 'Anima Conduit':
                        player.hp *= 1.08
        elif trigger == 'arrowhit': pass
        elif trigger == 'shot':
            for i in range(1, 4):
                if self.slotlevel[i] == 1:
                    if self.slots[i] == 'Accelerate':
                        self.cools['accelerate'] = [1, self.cools[1] + .08]
                elif self.slotlevel[i] == 2:
                    if self.slots[i] == 'Accelerate':
                        self.cools['accelerate'] = [1, self.cools[1] + .1]
                elif self.slotlevel[i] == 3:
                    if self.slots[i] == 'Accelerate':
                        self.cools['accelerate'] = [1, self.cools[1] + .12]

    def get_power(self):
        return self.pow

    def got_soul(self, player):
        self.check_enchants('soul', player, player._game)

    def arrow_hit(self, game, enemy):
        self.check_enchants('arrowhit', game.player, player, enemy)
    

class Consumable:
    def __repr__(self):
        return f'{self.name}()'

    def __init__(self):
        self.name = 'Consumable'
        self.x = 0
        self.y = 0

    def render(self, x, y, game):
        self.x = x
        self.y = y
        self.draw(game)

    def draw(self, game):
        t = pygame.font.SysFont('', 20).render(
            self.name, 1, pygame.Color('black'))
        game.screen.blit(t, (self.x - (t.get_width() // 2), self.y - 20))

    def use(self, game):
        pass


class Artifact:
    def __repr__(self):
        return f'{self.name}(cooldown={self.maxcooldown})'

    def __init__(self, pow):
        self.name = 'Artifact'
        self.x = 0
        self.y = 0
        self.cooldown = 0
        self.maxcooldown = 1
        self._needed = 0
        self.pow = pow
        self._last = time.time()
        self._gives_kill = 0

    def render(self, x, y, game):
        self.x = x
        self.y = y
        self.draw(game)

    def draw(self, game):
        t = pygame.font.SysFont('', 20).render(
            self.name, 1, pygame.Color('black'))
        game.screen.blit(t, (self.x, self.y))
        t = pygame.font.SysFont('', 20).render(
            str(self.pow), 1, pygame.Color('black'))
        game.screen.blit(t, (self.x - 20, self.y))

        cooldown_rect = pygame.Rect(self.x, self.y + 25, self.cooldown, 5)
        pygame.draw.rect(game.screen, pygame.Color('green'), cooldown_rect)

    def _draw(self, game):
        pass

    def use(self, game):
        if game.player.kills >= self._needed and self.cooldown <= 0:
            game.player.kills -= self._needed
            self.cooldown = self.maxcooldown
        else:
            return False
        return True

    def get_power(self):
        return self.pow

    def check_cooldown(self, game):
        if self.cooldown > 0:
            if time.time() - self._last >= 1:
                self._last = time.time()
                self.cooldown -= 1

    def wait(self, game, seconds):
        t = time.time()
        while time.time() - t < seconds:
            game.play(self._draw)


class BaseArmor:  # armor enchants are way more complex as they have to do more with 'per-tick' things
    enchants = ['Acrobat', 'Bag of Souls', 'Burning', 'Cool Down', 'Cowardice', 'Deflect', 'Electrified', 'Explorer', 'Fire Trail', 'Food Reserves',
                'Frenzied', 'Health Synergy', 'Lucky Explorer', 'Potion Barrier', 'Recycler', 'Snowball', 'Soul Speed', 'Speed Synergy', 'Suprise Gift',
                'Swiftfooted', 'Thorns', 'Chilling', 'Final Shout', 'Gravity Pulse', 'Protection', 'Reckless', 'Luck of the Sea', 'Rush', 'Tumblebee']
    # Currently removed: Final Shout, Life Boost, Focus-es, Beast enchants, Shadow Surge, Shadow Blast (no shadow form, helpful boosts, or death functionality yet)
    def __repr__(self):
        return f'{self.name}(protection={self.protect}, hp={self.hp}]'

    def __init__(self, pow):
        self.name = 'Armor'
        self.protect = 0
        self.hp = 0
        self.x = 0
        self.y = 0
        self.color = pygame.Color('brown')
        self.descript = []
        self._bonus = []
        self._speed = 0
        self._spent = 0
        self._enchant = 0
        self._kills = 0
        self._move = 1
        self._didboost = False
        self.arrows = 0
        self.pow = pow
        self.slots = {1: None, 2: None, 3: None}
        self.slotlevel = {1: 0, 2: 0, 3: 0}
        self.cools = {'final shout': 0, 'burning': 0, 'snowball': 0, 'chilling': 0, 'gravity pulse': 0}
        self.blocks_moved = 0
        self._arrow = 0
        self.prot_dict = {0: 1, 1: .94, 2: .89, 3: .85}
        self.dmg_mul = 0
        self.bees = []
        self._soul = 0
        self._art = 0
        self.arrow_boost = 0
        self.attack_speed = 0
        self.life_aura = 0
        self.lasttime = time.time()
        self.randomize_enchants()

    def randomize_enchants(self):
        self.slots[1] = random.choice(BaseArmor.enchants)
        self.slots[2] = random.choice(BaseArmor.enchants)
        self.slots[3] = random.choice(BaseArmor.enchants)

    def has_ench(self, ench):
        return any((self.slots[1] == ench, self.slots[2] == ench, self.slots[3] == ench))

    def get_ench(self, ench):
        if self.slots[1] == ench: return self.slotlevel[1]
        elif self.slots[2] == ench: return self.slotlevel[2]
        elif self.slots[3] == ench: return self.slotlevel[3]
        return 0

    def get_soul_max_mul(self):
        return 1 + (self.get_ench('Bag of Souls') * .5)

    def damage_mul(self):
        if self.get_ench('Reckless'):
            return 1 + self.dmg_mul + (.3 + .2 * self.get_ench('Reckless'))
        return 1 + self.dmg_mul

    def render(self, x, y, game):
        self.x = x
        self.y = y
        for key, val in self.cools.items():
            if val > 0:
                self.cools[key] -= time.time() - self.lasttime
        self.lasttime = time.time()
        if game.player.hp < (game.player.hp / 4) and self.has_ench('Final Shout') and self.cools['final shout'] <= 0:
            # self._bonus.remove('Final Shout')
            for artifact in [game.player.a1, game.player.a2, game.player.a3]:
                if artifact is None:
                    continue
                temp = artifact.cooldown
                artifact.cooldown = 0
                artifact.use(game)
                artifact.cooldown = temp
            self.cools['final shout'] = 14 - (2 * self.get_ench('Final Shout'))
        if self.has_ench('Frenzied') and game.player.hp < (game.player.hpmax / 2) and not self._didboost:
            self._didboost = True
            game.player.attack_speed += .1 * self.get_ench('Frenzied')
        elif self.has_ench('Frenzied') and self._didboost and game.player.hp >= game.player.hpmax / 2:
            self._didboost = False
            game.player.attack_speed -= .1 * self.get_ench('Frenzied')
        if self.has_ench('Burning') and self.cools['burning'] <= 0:
            self.cools['burning'] = .5
            for i in game.enemies:
                try:
                    if math.dist((i.rect.x, i.rect.y), (self.x, self.y)) < game.player.weapon.reach:
                        i.take_damage(self.get_ench('burning') + (self.pow * (self.get_ench('burning') / 100)))
                except AttributeError:  # using their fists
                    if math.dist((i.rect.x, i.rect.y), (self.x, self.y)) < 30:
                        i.take_damage(self.get_ench('burning') + (self.pow * (self.get_ench('burning') / 100)))
        if self.has_ench('Snowball') and self.cools['snowball'] <= 0:
            self.cools['snowball'] = 7 - (2 * self.get_ench('Snowball'))
            c = None
            l = float('inf')
            for i in game.enemies:
                if math.dist((i.rect.x, i.rect.y), (self.x, self.y)) < l:
                    l = math.dist((i.rect.x, i.rect.y), (self.x, self.y))
                    c = i
            if c: c.give_unmoving(4, 'stunned')
        if self.has_ench('Chilling') and self.cools['chilling'] <= 0:
            self.cools['chilling'] = 2
            for i in game.enemies:
                if math.dist((i.rect.x, i.rect.y), (self.x, self.y)) < 200:
                    i.effects_['freezing'] = (1, 1 - (.2 * self.get_ench('Chilling')))
                    i.effects_['weakened'] = (1, 1 - (.2 * self.get_ench('Chilling')))
        if self.has_ench('Gravity Pulse') and self.cools['gravity pulse'] <= 0:
            self.cools['gravity pulse'] = 5
            for i in game.enemies:
                for j in range(5 * self.get_ench('Gravity Pulse')):
                    if self.x < i.rect.x:
                        i.rect.x -= 3
                    else:
                        i.rect.x += 3
                    if self.y < i.rect.y:
                        i.rect.y -= 3
                    else:
                        i.rect.y += 3

                i.hitbox.update(i.rect.x, i.rect.y, i.reach)
        self.draw(game)

    def draw(self, game):
        pygame.draw.rect(game.screen, self.color,
                         pygame.Rect(self.x, self.y, 10, 15))

    def show_info(self, x, y, game):
        text1 = pygame.font.SysFont(self.name, 20)
        text2 = []
        for text in self.descript:
            text2.append(pygame.font.SysFont(text, 20).render(
                text, 1, pygame.Color('black')))
        game.screen.blit(text1.render(
            self.name, 1, pygame.Color('black')), (x, y - 20))
        for text in range(len(text2)):
            game.screen.blit(text2[text], (x, y - ((text + 2) * 20)))

    def update_descript(self):
        self.descript = [f'Armor health: {self.hp}']
        if self._bonus:
            self.descript += self._bonus
        if self.slotlevel[1] > 0:
            self.descript.append(f'{self.slots[1]} [{self.slotlevel[1]}')
        if self.slotlevel[2] > 0:
            self.descript.append(f'{self.slots[2]} [{self.slotlevel[2]}')
        if self.slotlevel[3] > 0:
            self.descript.append(f'{self.slots[3]} [{self.slotlevel[3]}')

    def salvage(self, player):
        player.emeralds += random.randint(3, 7) + self._enchant
        player.level += self._spent

    def enchant(self, spent, game):
        index = dungeon_gui.get_enchant(self, game)
        if game.player.level <= self.slotlevel[index]: return game.player.level
        self._spent += self.slotlevel[index] + 1
        self.slotlevel[index] += 1
        self.update_descript()
        return game.player.level - self.slotlevel[index]

    def _protect(self, damage):
        if random.randint(1, 10) < self.get_ench('Deflect') * 2 + 1:
            return 0
        return self.protect * damage * self.prot_dict[self.get_ench('Protection')]

    def get_power(self):
        return self.pow

    def do_special(self, player, enemy, game):
        pass

    def use_potion(self, game):
        self.check_enchants('potion', game.player, game)

    def equip(self, game):
        pass

    def remove(self, game):
        pass

    @property
    def slotslevel(self): return self.slotlevel  # Because I keep writing slotslevel

    def check_enchants(self, trigger, player, game=None, art=None, enemy=None):
        if trigger == 'potion':
            for i in range(1, 4):
                if self.slotlevel[i] == 1:  # level 1 enchants
                    if self.slots[i] == 'Food Reserves':
                        game.chests.append(dungeon_chests.Hack(self.x + random.randint(-30, 30), self.y + random.randint(-30, 30), random.choice([i for i in cloot if not issubclass(i, Potion) and type(i) != TNT])))
                    elif self.slots[i] == 'Potion Barrier':
                        player.effects_['potion barrier'] = (5, .1)
                    elif self.slots[i] == 'Suprise Gift' and random.randint(0, 1) == 1:
                        game.chests.append(dungeon_chests.Hack(self.x + random.randint(-30, 30), self.y + random.randint(-30, 30), random.choice(cloot)))
                elif self.slotlevel[i] == 2:
                    if self.slots[i] == 'Food Reserves':
                        game.chests.append(dungeon_chests.Hack(self.x + random.randint(-30, 30), self.y + random.randint(-30, 30), random.choice([i for i in cloot if not issubclass(i, Potion) and type(i) != TNT])))
                        game.chests.append(dungeon_chests.Hack(self.x + random.randint(-30, 30), self.y + random.randint(-30, 30), random.choice([i for i in cloot if not issubclass(i, Potion) and type(i) != TNT])))
                    elif self.slots[i] == 'Potion Barrier':
                        player.effects_['potion barrier'] = (7, .1)
                    elif self.slots[i] == 'Suprise Gift':
                        game.chests.append(dungeon_chests.Hack(self.x + random.randint(-30, 30), self.y + random.randint(-30, 30), random.choice(cloot)))
                elif self.slotlevel[i] == 3:
                    if self.slots[i] == 'Food Reserves':
                        game.chests.append(dungeon_chests.Hack(self.x + random.randint(-30, 30), self.y + random.randint(-30, 30), random.choice([i for i in cloot if not issubclass(i, Potion) and type(i) != TNT])))
                        game.chests.append(dungeon_chests.Hack(self.x + random.randint(-30, 30), self.y + random.randint(-30, 30), random.choice([i for i in cloot if not issubclass(i, Potion) and type(i) != TNT])))
                        game.chests.append(dungeon_chests.Hack(self.x + random.randint(-30, 30), self.y + random.randint(-30, 30), random.choice([i for i in cloot if not issubclass(i, Potion) and type(i) != TNT])))
                    elif self.slots[i] == 'Potion Barrier':
                        player.effects_['potion barrier'] = (9, .1)
                    elif self.slots[i] == 'Suprise Gift':
                        game.chests.append(dungeon_chests.Hack(self.x + random.randint(-30, 30), self.y + random.randint(-30, 30), random.choice(cloot)))
                        if random.randint(0, 1) == 1:
                            game.chests.append(dungeon_chests.Hack(self.x + random.randint(-30, 30), self.y + random.randint(-30, 30), random.choice(cloot)))
        elif trigger == 'roll':
            for i in range(1, 4):
                if self.slotslevel[i] == 1:
                    if self.slots[i] == 'Acrobat':
                        player.roll_cooldown *= .85
                    elif self.slots[i] == 'Electrified':
                        enemies = []
                        for i in game.enemies:
                            if math.dist((i.rect.x, i.rect.y), (self.x, self.y)) < 80:
                                enemies.append(i)
                        for i in range(30):
                            game.play()
                            for j in enemies:
                                pygame.draw.line(game.screen, pygame.Color('yellow'), (self.x, self.y), (j.rect.x, j.rect.y), 2)
                        for j in enemies:
                            j.take_damage(2 + (self.pow * .02))
                    elif self.slots[i] == 'Fire Trail':
                        game.other.append(dungeon_misc.HelpFire(self.x, self.y, {'dmg': 1 + (self.pow * .01)}))
                    elif self.slots[i] == 'Swiftfooted':
                        player.effects_['swiftfooted'] = (3, .3)
                    elif self.slots[i] == 'Tumblebee' and random.randint(1, 100) < 34:
                        self.bees = [i for i in self.bees if i.hp > 0]
                        if len(self.bees) < 3:
                            game.helpfuls.append(dungeon_helpful.Bee(self.x, self.y, self.pow))
                            self.bees.append(game.helpfuls[-1])
                elif self.slotslevel[i] == 2:
                    if self.slots[i] == 'Acrobat':
                        player.roll_cooldown *= .7
                    elif self.slots[i] == 'Electrified':
                        enemies = []
                        for i in game.enemies:
                            if math.dist((i.rect.x, i.rect.y), (self.x, self.y)) < 80:
                                enemies.append(i)
                        for i in range(30):
                            game.play()
                            for j in enemies:
                                pygame.draw.line(game.screen, pygame.Color('yellow'), (self.x, self.y), (j.rect.x, j.rect.y), 2)
                        for j in enemies:
                            j.take_damage(4 + (self.pow * .02))
                    elif self.slots[i] == 'Fire Trail':
                        game.other.append(dungeon_misc.HelpFire(self.x, self.y, {'dmg': 2 + (self.pow * .02)}))
                    elif self.slots[i] == 'Swiftfooted':
                        player.effects_['swiftfooted'] = (3, .4)
                    elif self.slots[i] == 'Tumblebee' and random.randint(1, 100) < 68:
                        self.bees = [i for i in self.bees if i.hp > 0]
                        if len(self.bees) < 3:
                            game.helpfuls.append(dungeon_helpful.Bee(self.x, self.y, self.pow))
                            self.bees.append(game.helpfuls[-1])
                elif self.slotslevel[i] == 3:
                    if self.slots[i] == 'Acrobat':
                        player.roll_cooldown *= .55
                    elif self.slots[i] == 'Electrified':
                        enemies = []
                        for i in game.enemies:
                            if math.dist((i.rect.x, i.rect.y), (self.x, self.y)) < 80:
                                enemies.append(i)
                        for i in range(30):
                            game.play()
                            for j in enemies:
                                pygame.draw.line(game.screen, pygame.Color('yellow'), (self.x, self.y), (j.rect.x, j.rect.y), 2)
                        for j in enemies:
                            j.take_damage(6 + (self.pow * .02))
                    elif self.slots[i] == 'Fire Trail':
                        game.other.append(dungeon_misc.HelpFire(self.x, self.y, {'dmg': 3 + (self.pow * .03)}))
                    elif self.slots[i] == 'Swiftfooted':
                        player.effects_['swiftfooted'] = (3, .5)
                    elif self.slots[i] == 'Tumblebee':
                        self.bees = [i for i in self.bees if i.hp > 0]
                        if len(self.bees) < 3:
                            game.helpfuls.append(dungeon_helpful.Bee(self.x, self.y, self.pow))
                            self.bees.append(game.helpfuls[-1])
                            if random.randint(1, 100) == 1 and len(self.bees) < 3:
                                game.helpfuls.append(dungeon_helpful.Bee(self.x, self.y, self.pow))
                                self.bees.append(game.helpfuls[-1])
        elif trigger == 'artifact':
            for i in range(1, 4):
                if self.slotslevel[i] == 1:
                    if self.slots[i] == 'Cool Down':
                        art.cooldown *= .9
                    elif self.slots[i] == 'Health Synergy':
                        player.hp *= 1.03
                    elif self.slots[i] == 'Speed Synergy':
                        player.effects['speed'] += 1
                elif self.slotslevel[i] == 2:
                    if self.slots[i] == 'Cool Down':
                        art.cooldown *= .81
                    elif self.slots[i] == 'Health Synergy':
                        player.hp *= 1.04
                    elif self.slots[i] == 'Speed Synergy':
                        player.effects['speed'] += 2
                elif self.slotslevel[i] == 3:
                    if self.slots[i] == 'Cool Down':
                        art.cooldown *= .73
                    elif self.slots[i] == 'Health Synergy':
                        player.hp *= 1.05
                    elif self.slots[i] == 'Speed Synergy':
                        player.effects['speed'] += 3
        elif trigger == 'move':
            for i in range(1, 4):
                if self.slotslevel[i] == 1:
                    if self.slots[i] == 'Explorer':
                        self.blocks_moved += 1
                        if self.blocks_moved > 100:
                            self.blocks_moved = 0
                            player.hp *= 1.003
                    elif self.slots[i] == 'Lucky Explorer' and random.randint(1, 20) == 1:
                        game.chests.append(dungeon_chests.Hack2(self.x, self.y, 1))
                elif self.slotslevel[i] == 2:
                    if self.slots[i] == 'Explorer':
                        self.blocks_moved += 1
                        if self.blocks_moved > 100:
                            self.blocks_moved = 0
                            player.hp *= 1.007
                    elif self.slots[i] == 'Lucky Explorer' and random.randint(1, 20) == 1:
                        game.chests.append(dungeon_chests.Hack2(self.x, self.y, 3))
                elif self.slotslevel[i] == 3:
                    if self.slots[i] == 'Explorer':
                        self.blocks_moved += 1
                        if self.blocks_moved > 100:
                            self.blocks_moved = 0
                            player.hp *= 1.01
                    elif self.slots[i] == 'Lucky Explorer' and random.randint(1, 20) == 1:
                        game.chests.append(dungeon_chests.Hack2(self.x, self.y, 5))
        elif trigger == 'arrow':
            for i in range(1, 4):
                if self.slotslevel[i] == 1:
                    if self.slots[i] == 'Recycler':
                        self._arrow += 1
                        if self._arrow >= 30:
                            self._arrow = 0
                            player.arrows += 5
                if self.slotslevel[i] == 2:
                    if self.slots[i] == 'Recycler':
                        self._arrow += 1
                        if self._arrow >= 20:
                            self._arrow = 0
                            player.arrows += 5
                if self.slotslevel[i] == 3:
                    if self.slots[i] == 'Recycler':
                        self._arrow += 1
                        if self._arrow >= 10:
                            self._arrow = 0
                            player.arrows += 5
        elif trigger == 'soul':
            for i in range(1, 4):
                if self.slotlevel[i] == 1:
                    if self.slots[i] == 'Soul Speed':
                        player.effects_['soul speed'] = (2, player.effects_['soul speed'][1] + 1)
                if self.slotlevel[i] == 2:
                    if self.slots[i] == 'Soul Speed':
                        player.effects_['soul speed'] = (3, player.effects_['soul speed'][1] + 1)
                if self.slotlevel[i] == 3:
                    if self.slots[i] == 'Soul Speed':
                        player.effects_['soul speed'] = (4, player.effects_['soul speed'][1] + 1)
        elif trigger == 'hit':
            for i in range(1, 4):
                if self.slotlevel[i] == 1:
                    if self.slots[i] == 'Thorns':
                        enemy.take_damage(player.saved_damage)
                    elif self.slots[i] == 'Rush':
                        player.effects_['rush'] = (1, .3)
                if self.slotlevel[i] == 2:
                    if self.slots[i] == 'Thorns':
                        enemy.take_damage(player.saved_damage * 1.5)
                    elif self.slots[i] == 'Rush':
                        player.effects_['rush'] = (1, .6)
                if self.slotlevel[i] == 3:
                    if self.slots[i] == 'Thorns':
                        enemy.take_damage(player.saved_damage * 2)
                    elif self.slots[i] == 'Rush':
                        player.effects_['rush'] = (1, .9)

    def move(self, game):
        self.check_enchants('move', game.player, game)

    def roll(self, game):
        self.check_enchants('roll', game.player, game)

    def act_art(self, game, art):
        self.check_enchants('artifact', game.player, game, art)

    def arrow_hit(self, game):
        self.check_enchants('arrow', game.player, game)

    def got_soul(self, player):
        self.check_enchants('soul', player)

    def got_hit(self, player, enemy, game):
        self.check_enchants('hit', player, game, enemy=enemy)


class Sword(BaseMeleeWeapon):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Sword'
        self.hiltcolor = pygame.Color('brown')
        self.bladecolor = pygame.Color('brown')

    def draw(self, game):
        pygame.draw.line(game.screen, self.hiltcolor,
                         (self.x, self.y), (self.x + 10, self.y + 10), 3)
        pygame.draw.line(game.screen, self.hiltcolor,
                         (self.x, self.y + 10), (self.x + 5, self.y + 5), 3)
        pygame.draw.line(game.screen, self.bladecolor,
                         (self.x + 6, self.y + 4), (self.x + 20, self.y - 10), 3)


class Axe(BaseMeleeWeapon):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Axe'
        self.handlecolor = pygame.Color('brown')
        self.bladecolor = pygame.Color('brown')

    def draw(self, game):
        pygame.draw.line(game.screen, self.handlecolor,
                         (self.x, self.y), (self.x + 15, self.y - 15), 3)
        pygame.draw.polygon(game.screen, self.bladecolor, [(
            self.x + 15, self.y - 15), (self.x + 10, self.y - 15), (self.x + 15, self.y - 20)])


class Mallet(BaseMeleeWeapon):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Mallet'
        self.handlecolor = pygame.Color('brown')
        self.blockcolor = pygame.Color('brown')

    def draw(self, game):
        pygame.draw.line(game.screen, self.handlecolor,
                         (self.x, self.y), (self.x + 15, self.y - 15), 3)
        pygame.draw.polygon(game.screen, self.blockcolor, [(
            self.x + 10, self.y - 20), (self.x + 15, self.y - 25), (self.x + 20, self.y - 15), (self.x + 15, self.y - 10)])


class Mace(BaseMeleeWeapon):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Mace'
        self.handlecolor = pygame.Color('grey')
        self.ballcolor = pygame.Color('grey')

    def draw(self, game):
        pygame.draw.line(game.screen, self.handlecolor,
                         (self.x, self.y), (self.x + 15, self.y - 15), 3)
        pygame.draw.circle(game.screen, self.ballcolor, (self.x + 17, self.y - 17), 4)


class Fist(BaseMeleeWeapon):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Fist'
        self.fistcolor = pygame.Color('brown')

    def draw(self, game):
        pygame.draw.line(game.screen, self.fistcolor,
                         (self.x, self.y), (self.x, self.y), 4)


class Knife(BaseMeleeWeapon):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Knife'
        self.bladecolor = pygame.Color('brown')
        self.handlecolor = pygame.Color('brown')

    def draw(self, game):
        pygame.draw.line(game.screen, self.bladecolor,
                         (self.x + 6, self.y - 6), (self.x + 20, self.y - 20), 3)
        pygame.draw.line(game.screen, self.handlecolor,
                         (self.x, self.y), (self.x + 5, self.y - 5), 3)


class Scythe(BaseMeleeWeapon):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Scythe'
        self.bladecolor = pygame.Color('brown')
        self.handlecolor = pygame.Color('brown')

    def draw(self, game):
        pygame.draw.line(game.screen, self.handlecolor,
                         (self.x, self.y), (self.x + 20, self.y - 20), 3)
        pygame.draw.line(game.screen, self.bladecolor, (self.x +
                         20, self.y - 20), (self.x + 13, self.y - 18), 3)


class Bow(BaseRangeWeapon):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Bow'
        self.bowcolor = pygame.Color('brown')
        self.stringcolor = pygame.Color('light grey')

    def draw(self, game):
        pygame.draw.lines(game.screen, self.bowcolor, False, [
                          (self.x - 5, self.y + 5), (self.x, self.y + 5), (self.x + 5, self.y), (self.x + 5, self.y - 5)], 2)
        pygame.draw.line(game.screen, self.stringcolor,
                         (self.x - 5, self.y + 5), (self.x + 5, self.y - 5))


class Crossbow(BaseRangeWeapon):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Crossbow'
        self.bowcolor = pygame.Color('brown')
        self.stringcolor = pygame.Color('light grey')
        self.arrow['damage'] = pow + 1
        self.arrow['knockback'] = 15
        self.cooldown = .85

    def draw(self, game):
        pygame.draw.line(game.screen, self.bowcolor,
                         (self.x, self.y), (self.x - 10, self.y - 10), 2)
        pygame.draw.line(game.screen, self.bowcolor,
                         (self.x - 10, self.y), (self.x, self.y - 10), 2)
        pygame.draw.lines(game.screen, self.stringcolor, False, [
                          (self.x - 10, self.y), (self.x - 10, self.y - 5), (self.x - 5, self.y - 10), (self.x, self.y - 10)])


class WoodSword(Sword):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Wood Sword'
        self.cooldown = .9
        self.reach = 20
        self.damage = pow
        self.update_descript()


class StoneSword(Sword):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Stone Sword'
        self.cooldown = .8
        self.reach = 25
        self.damage = pow * 1.05
        self.bladecolor = pygame.Color('dark grey')
        self.update_descript()


class IronSword(Sword):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Iron Sword'
        self.cooldown = .7
        self.reach = 25
        self.damage = pow * 1.08
        self.bladecolor = pygame.Color('light grey')
        self.update_descript()


class GoldenSword(Sword):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Golden Sword'
        self.cooldown = .8
        self.reach = 20
        self.damage = pow
        self.bladecolor = pygame.Color('gold')
        self.update_descript()


class DiamondSword(Sword):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Diamond Sword'
        self.cooldown = .63
        self.reach = 30
        self.damage = 2 + (pow * 1.1)
        self.bladecolor = pygame.Color('light blue')
        self._speed = 1
        self.update_descript()


class SpeedySword(Sword):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Speedy Sword'
        self.cooldown = .4
        self.reach = 20
        self.damage = pow + 8
        self.bladecolor = pygame.Color('red')
        self._speed = 2
        self.update_descript()


class Claymore(Sword):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Claymore'
        self.cooldown = 1.1
        self.reach = 30
        self.damage = 5 + (pow * 0.4)
        self.bladecolor = pygame.Color('white')
        self.handlecolor = pygame.Color('grey')
        self.update_descript()


class Heartstealer(Sword):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Heartstealer'
        self.cooldown = 1.1
        self.reach = 30
        self.damage = 5 + (pow * 0.4)
        self.bladecolor = pygame.Color('red')
        self.handlecolor = pygame.Color('grey')
        self._bonus.append('Steals health on hit')
        self.update_descript()


class Mace_(Mace):
    def __init__(self, pow):
        super().__init__(pow)
        self.cooldown = .9
        self.reach = 20
        self.damage = 6 + (pow * .1)
        self.update_descript()


class SunsGrace(Mace):
    def __init__(self, pow):
        super().__init__(pow)
        self.cooldown = .9
        self.reach = 20
        self.damage = 6 + (pow * .1)
        self._bonus.append('Heals nearby allies')
        self.update_descript()


class WoodAxe(Axe):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Wood Axe'
        self.cooldown = 1.2
        self.reach = 30
        self.damage = pow + 2
        self.update_descript()


class IronAxe(Axe):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Iron Axe'
        self.cooldown = 1.13
        self.reach = 30
        self.damage = 3 + (pow * 1.05)
        self.bladecolor = pygame.Color('grey')
        self.update_descript()


class GoldenAxe(Axe):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Golden Axe'
        self.cooldown = 1.18
        self.reach = 25
        self.damage = 2 + (pow * .1)
        self.update_descript()
        self.bladecolor = pygame.Color('gold')


class WeightedAxe(Axe):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Weighted Axe'
        self.cooldown = 1.3
        self.reach = 50
        self.damage = 15 + (pow * .02)
        self.bladecolor = pygame.Color('dark grey')
        self._speed = -1
        self.update_descript()


class CursedAxe(Axe):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Cursed Axe'
        self.cooldown = 1.22
        self.reach = 30
        self.damage = pow * 1.03
        self.bladecolor = pygame.Color('grey')
        self.handlecolor = pygame.Color('purple')
        self._bonus.append('Extra damage to undead')
        self.update_descript()


class IronMallet(Mallet):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Iron Mallet'
        self.blockcolor = pygame.Color('grey')
        self.knockback = 10
        self.cooldown = 1
        self.reach = 30
        self.damage = pow + 4
        self.update_descript()


class BigMallet(Mallet):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Big Mallet'
        self.blockcolor = pygame.Color('light blue')
        self.knockback = 50
        self.cooldown = 0.9
        self.reach = 60
        self.damage = 1 + (pow * .3)
        self._bonus.append('Great pushback')
        self.update_descript()


class HerosMallet(Mallet):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Hero\'s Mallet'
        self.blockcolor = pygame.Color('dark blue')
        self.knockback = 15
        self.cooldown = 1.06
        self.reach = 40
        self.damage = pow + 10
        self.update_descript()


class XPGatherer(Mallet):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'XP Gatherer'
        self.blockcolor = pygame.Color('green')
        self.knockback = 10
        self.cooldown = 1
        self.reach = 20
        self.damage = 15 + (pow * .1)
        self.update_descript()

    def attack(self, enemy, player, damage, knockback):
        super().attack(enemy, player, damage, knockback)
        player.get_xp(0.07)


class GravityHammer(Mallet):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Gravity Hammer'
        self.blockcolor = pygame.Color('purple')
        self.knockback = 50
        self.cooldown = 1.2
        self.reach = 90
        self.damage = 3 + (pow * .5)
        self._speed = -1
        self._bonus.extend(['Great Pushback', 'Pulls in mobs'])
        self.update_descript()


class KillFist(Fist):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Maulers'
        self.fistcolor = pygame.Color('black')
        self.cooldown = .1
        self.reach = 20
        self.damage = 1 + (pow * .07)
        self.update_descript()


class SoulFists(Fist):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Soul Fists'
        self.fistcolor = pygame.Color('yellow')
        self.cooldown = .1
        self.reach = 20
        self.damage = 2 + (pow * .075)
        self._kills = 2
        self.update_descript()

    def attack(self, enemy, player, damage, knockback):
        if random.randint(1, 3) == 1:
            damage *= 3
        super().attack(enemy, player, damage, knockback)


class GaleKnife(Knife):  # why is this called gale knife? i have no idea
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Resolute Tempest Knife'
        self.bladecolor = pygame.Color('light blue')
        self.cooldown = 0.9
        self.reach = 30
        self.damage = 3 + (pow * .05)
        self._bonus.append('Speed burst on kill')
        self.update_descript()

    def attack(self, enemy, player, damage, knockback):
        super().attack(enemy, player, damage, knockback)

        if enemy.hp <= 0:
            if player.effects['speed'] < 2:
                player.effects['speed'] = 2


class TempestKnife(Knife):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Tempest Knife'
        self.bladecolor = pygame.Color('light blue')
        self.cooldown = 0.9
        self.reach = 30
        self.damage = 3 + (pow * .05)
        self.update_descript()


class FangsOfFrost(Knife):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Fangs of Frost'
        self.bladecolor = pygame.Color('light blue')
        self.cooldown = 0.26
        self.reach = 15
        self.damage = 0.5 + (pow * .05)
        self._bonus.append('Freezes mobs')
        self.update_descript()

    def attack(self, enemy, player, damage, knockback):
        super().attack(enemy, player, damage, knockback)
        enemy.give_unmoving(1)


class DarkKatana(Knife):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Dark Katana'
        self.bladecolor = pygame.Color('purple')
        self.handlecolor = pygame.Color('black')
        self.cooldown = 0.8
        self.reach = 20
        self.damage = 10 + (pow * .03)
        self._speed = 1
        self.update_descript()


class EternalKnife(Knife):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Eternal Knife'
        self.bladecolor = pygame.Color('purple')
        self.handlecolor = pygame.Color('black')
        self.cooldown = .7
        self.reach = 20
        self.damage = pow + 1
        self._kills = 2
        self.update_descript()


class Backstabber(Knife):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Backstabber'
        self.bladecolor = pygame.Color('lavender')
        self.handlecolor = pygame.Color('brown')
        self.cooldown = .2
        self.reach = 20
        self.damage = pow + 2
        self._bonus.append('Extra damage to unsuspecting enemies')
        self.update_descript()


class JailorScythe(Scythe):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Jailor\'s Scythe'
        self.bladecolor = pygame.Color('white')
        self.handlecolor = pygame.Color('purple')
        self.cooldown = 0.8
        self.reach = 60
        self.damage = 6
        self._bonus = ['Chains mobs']
        self.update_descript()


class GraveBane(Scythe):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Grave Bane'
        self.bladecolor = pygame.Color('yellow')
        self.handlecolor = pygame.Color('yellow')
        self.cooldown = 0.76
        self.reach = 100
        self.damage = 10 + (pow * .3)
        self._bonus = ['Extra damage to undead', 'Longer reach']
        self.update_descript()


class PurpleStorm(Bow):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Purple Storm'
        self.bowcolor = pygame.Color('purple')
        self.cooldown = .06
        self.arrow['damage'] = pow
        self.update_descript()


class FlameBow(Bow):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Flame Bow'
        self.bowcolor = pygame.Color('red')
        self.stringcolor = pygame.Color('red')
        self.cooldown = .3
        self.arrow['type'] = dungeon_arrows.FlamingArrow
        self.arrow['name'] = 'Flaming Arrow'
        self.update_descript()


class PoisonBow(Bow):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Poison Bow'
        self.bowcolor = pygame.Color('green')
        self.arrow['type'] = dungeon_arrows.PoisonArrow
        self.arrow['knockback'] = 25
        self.arrow['name'] = 'Poison Arrow'
        self.update_descript()


class PowerBow(Bow):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Power Bow'
        self.stringcolor = pygame.Color('light grey')
        self.bowcolor = pygame.Color('red')
        self.cooldown = .4
        self.arrow['damage'] = 6 + (pow * .3)
        self.update_descript()


class Sabrewing(PowerBow):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Sabrewing'
        self.bowcolor = pygame.Color('gold')
        self.update_descript()

    def shoot(self, game, player, t):
        super().shoot(game, player, t)
        if game.player.effects['regeneration'] < 10:
            game.player.effects['regeneration'] = 10


class Longbow(Bow):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Longbow'
        self.arrow['damage'] = pow
        self.arrow['knockback'] = 30
        self.update_descript()


class BurstGaleBow(Bow):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Burst Gale Bow'
        self.arrow['type'] = dungeon_arrows.SpeedWhenHurtArrow
        self.update_descript()


class SlowCrossbow(Crossbow):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Slow Crossbow'
        self.bowcolor = pygame.Color('dark grey')
        self.cooldown = 1
        self.arrow['type'] = dungeon_arrows.SlowArrow
        self.arrow['name'] = 'Slow Arrow'
        self.update_descript()


class ExplodingCrossbow(Crossbow):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Exploding Crossbow'
        self.bowcolor = pygame.Color('white')
        self.cooldown = .95
        self.arrow['type'] = dungeon_arrows.ExplodingArrow
        self.arrow['name'] = 'Exploding Arrow'
        self.update_descript()


class ImplodingCrossbow(Crossbow):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Imploding Crossbow'
        self.bowcolor = pygame.Color('red')
        self.cooldown = .73
        self.arrow['type'] = dungeon_arrows.ImplodingArrow
        self.arrow['name'] = 'Imploding Arrow'
        self.update_descript()


class HeavyCrossbow(Crossbow):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Heavy Crossbow'
        self.cooldown = 1.1
        self.arrow['damage'] = 10 + (pow * .06)
        self.arrow['knockback'] = 50
        self._speed = -1
        self.update_descript()


class Voidcaller(Crossbow):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Voidcaller'
        self.cooldown = 0.4
        self.arrow['damage'] = 3 + (pow * .1)
        self._kills = 2
        self.update_descript()


class ButterflyCrossbow(Crossbow):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Butterfly Crossbow'
        self.cooldown = .3
        self.arrow['damage'] = pow
        self._speed = 1
        self.update_descript()


class HarpCrossbow(Crossbow):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Harp Crossbow'
        self.cooldown = .2
        self.bowcolor = pygame.Color('gold')
        self.arrow['knockback'] = 20
        self.arrow['damage'] = 4 + (pow * .1)
        self.update_descript()


class Apple(Consumable):
    def __init__(self):
        super().__init__()
        self.name = 'Apple'

    def draw(self, game):
        super().draw(game)
        pygame.draw.circle(game.screen, pygame.Color(
            'red'), (self.x, self.y - 8), 8)

    def use(self, game):
        game.player.hp += 6


class Bread(Consumable):
    def __init__(self):
        super().__init__()
        self.name = 'Bread'

    def draw(self, game):
        super().draw(game)
        pygame.draw.ellipse(game.screen, pygame.Color(
            'brown'), pygame.Rect(self.x - 5, self.y - 5, 35, 15))

    def use(self, game):
        if game.player.effects['regeneration'] < 30:
            game.player.effects['regeneration'] = 30


class Pork(Consumable):
    def __init__(self):
        super().__init__()
        self.name = 'Pork'

    def draw(self, game):
        super().draw(game)
        pygame.draw.ellipse(game.screen, pygame.Color(
            'pink'), pygame.Rect(self.x - 5, self.y - 5, 25, 20))

    def use(self, game):
        game.player.hp += 4
        if game.player.effects['regeneration'] < 20:
            game.player.effects['regeneration'] = 20


class CookedSalmon(Consumable):
    def __init__(self):
        super().__init__()
        self.name = 'Cooked Salmon'

    def draw(self, game):
        super().draw(game)
        pygame.draw.ellipse(game.screen, pygame.Color(
            'dark red'), pygame.Rect(self.x - 5, self.y - 5, 15, 10))

    def use(self, game):
        game.player.hp += 4


class SweetBrew(Consumable):
    def __init__(self):
        super().__init__()
        self.name = 'Sweet Brew'

    def draw(self, game):
        super().draw(game)
        pygame.draw.ellipse(game.screen, pygame.Color(
            'red'), pygame.Rect(self.x - 5, self.y - 5, 35, 10))

    def use(self, game):
        game.player.hp += 5
        if game.player.effects['resistance'] < 25:
            game.player.effects['resistance'] = 25


class TNT(Consumable):
    def __init__(self):
        super().__init__()
        self.name = 'TNT'

    def draw(self, game):
        super().draw(game)
        pygame.draw.rect(game.screen, pygame.Color('red'),
                         pygame.Rect(self.x - 5, self.y - 5, 15, 15))
        pygame.draw.rect(game.screen, pygame.Color('white'),
                         pygame.Rect(self.x - 5, self.y, 15, 5))

    def use(self, game):
        game.other.append(dungeon_misc.TNT(
            game.player.rect.x, game.player.rect.y))


class Potion(Consumable):
    def __init__(self):
        super().__init__()
        self.name = 'Potion'
        self.color = pygame.Color('brown')
        self.effect = ''
        self.effect2 = ''

    def draw(self, game):
        super().draw(game)
        pygame.draw.circle(game.screen, pygame.Color(
            'light grey'), (self.x, self.y - 8), 8)
        pygame.draw.circle(game.screen, self.color, (self.x, self.y - 8), 7)

    def use(self, game):
        if game.player.effects[self.effect] < 30:
            game.player.effects[self.effect] = 30
        if self.effect2:
            if game.player.effects[self.effect2] < 30:
                game.player.effects[self.effect2] = 30


class StrengthPotion(Potion):
    def __init__(self):
        super().__init__()
        self.name = 'Strength Potion'
        self.color = pygame.Color('red')
        self.effect = 'strength'


class SwiftnessPotion(Potion):
    def __init__(self):
        super().__init__()
        self.name = 'Swiftness Potion'
        self.color = pygame.Color('light blue')
        self.effect = 'speed'


class ShadowBrew(Potion):
    def __init__(self):
        super().__init__()
        self.name = 'Shadow Brew'
        self.color = pygame.Color('purple')
        self.effect = 'speed'
        self.effect2 = 'strength'


class ReinforcedMail(BaseArmor):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Reinforced Mail'
        self.hp = pow * 1.13
        self.color = pygame.Color('grey')
        self.protect = .65
        self._bonus = ['35% Damage Reduction', '30% Chance to negate hits', '+100% Longer roll cooldown']
        self.update_descript()

    def roll(self, game):
        super().roll(game)
        game.player.roll_cooldown *= 2

    def _protect(self, damage):
        if random.randint(1, 10) < 4:
            return 0
        return super()._protect(damage)


class HunterArmor(BaseArmor):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Hunter\'s Armor'
        self.hp = pow * .9
        self.arrows = 10
        self._bonus = ['+10 Arrows per bundle', '+30% Arrow damage']
        self.arrow_boost = .3
        self.color = pygame.Color('tan')
        self.update_descript()


class HeroArmor(BaseArmor):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Hero\'s Armor'
        self.hp = pow
        self.color = pygame.Color('yellow')
        self._bonus = ['40% Faster Potion cooldown', 'Health potions heal nearby allies', '35% Damage reduction', 'Mobs target you more']
        self.update_descript()

    def use_potion(self, game):
        super().use_potion(game)
        game.player.potion_cooldown *= .6


class SoulRobe(BaseArmor):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Soul Robe'
        self.hp = max(pow, pow - 5)
        self.color = pygame.Color('dark grey')
        self._soul = .5
        self._art = .5
        self._bonus = ['+50% Soul Gathering', '+50% Artifact damage']
        self.update_descript()


class SplendidRobe(BaseArmor):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Splendid Robe'
        self.hp = pow * .94
        self.color = pygame.Color('purple')
        self._bonus = ['+30% Melee Damage', '+50% Artifact damage', '-40% Artifact cooldown']
        self._art = .5
        self.dmg_mul = .3
        self.update_descript()

    def act_art(self, game, art):
        super().act_art(game, art)
        art.cooldown *= .6


class MysteryArmor(BaseArmor):
    choices = ['+10 Arrows per bundle', 'Health potions heal nearby allies', '35% damage reduction', '+25% melee attack speed', '+50% Artifact damage', '+50% Souls gathered',
               '6% Lifesteal Aura', '-40% Potion cooldown', '+30% Melee damage', '+20% Weapon damage boost aura', '+50% Faster roll', '+15% Movespeed aura', 'Gives the player a pet bat',
               '30% Chance to negate hits', '-40% Artifact cooldown', '+30% Ranged damage']
    others = ['Mobs target you more', '-10% Movement speed', '100% Longer roll cooldown']
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Mystery Armor'
        self.hp = pow * round(random.uniform(.93, 1.07), 2)
        self.color = pygame.Color('light grey')
        # self.randomize_modifiers()  # coming soon
        choice1 = random.choice(MysteryArmor.choices)
        choice2 = random.choice(MysteryArmor.choices)
        self.parse(choice1)
        self.parse(choice2)
        self._bonus = [choice1, choice2]
        if random.randint(1, 15) == 1:
            choice3 = random.choice(MysteryArmor.others)
            if choice3 == '-10% Movement speed':
                self._move -= .1
            self._bonus.append(choice3)
        self._bat = None
        self.update_descript()

    def parse(self, c):
        if c == '+10 Arrows per bundle':
            self.arrows = 10
        elif c == '35% damage reduction':
            self.protect = .65
        elif c == '+25% melee attack speed':
            self.attack_speed = .25
        elif c == '+50% Artifact damage':
            self._art = .5
        elif c == '+50% Souls gathered':
            self._soul = .5
        elif c == '6% Lifesteal aura':
            self.life_aura = .06
        elif c == '+30% Melee Damage':
            self.dmg_mul += .3
        elif c == '+20% Weapon damage boost aura':
            self.dmg_mul += .2
        elif c == '+30% Ranged damage':
            self.arrow_boost = .3
        elif c == '+15% Movespeed aura':
            self._move += .15

    def _protect(self, damage):
        if random.randint(1, 10) < self.get_ench('Deflect') * 2 + 1:
            return 0
        if '30% Chance to negate hits' in self._bonus and random.randint(1, 10) < 4:
            return 0
        return damage * self.protect * self.prot_dict[self.get_ench('Protection')]

    def roll(self, game):
        super().roll(game)
        if '+50% Faster roll' in self._bonus: game.player.roll_cooldown *= .5
        if '100% Longer roll cooldown' in self._bonus: game.player.roll_cooldown *= 2

    def act_art(self, game, art):
        super().act_art(game, art)
        if '-40% Artifact cooldown' in self._bonus: art.cooldown *= .6

    def use_potion(self, game):
        super().use_potion(game)
        if '-40% Potion cooldown' in self._bonus: game.player.potion_cooldown *= .6

    def equip(self, game):
        if 'Gives you a pet bat' in self._bonus:
            self._bat = dungeon_helpful.Bat(game.player.rect.x, game.player.rect.y)
            game.helpfuls.append(self._bat)

    def remove(self, game):
        if 'Gives you a pet bat' in self._bonus:
            self._bat._nowdie = True
            self._bat.hp = 0


class SpelunkerArmor(BaseArmor):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Spelunker Armor'
        self.hp = pow * .86
        self.color = pygame.Color('orange')
        self._bat = None
        self._bonus = ['Gives you a pet bat', '20% Weapon damage boost aura']
        self.dmg_mul = .2
        self.update_descript()

    def equip(self, game):
        self._bat = dungeon_helpful.Bat(game.player.rect.x, game.player.rect.y)
        game.helpfuls.append(self._bat)

    def remove(self, game):
        self._bat._nowdie = True
        self._bat.hp = 0


class FoxArmor(BaseArmor):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Fox Armor'
        self.hp = pow
        self.color = pygame.Color('orange')
        self._bonus = ['30% chance to negate damage', '+20% Weapon damage boost aura', 'Health potions heal nearby allies']
        self.dmg_boost = .2
        self.update_descript()

    def _protect(self, damage):
        if random.randint(1, 10) < self.get_ench('Deflect') * 2 + 1:
            return 0
        if random.randint(1, 10) < 4:
            return 0
        return damage * self.prot_dict[self.get_ench('Protection')]


class FrostBite(BaseArmor):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Frost Bite'
        self.hp = pow - 1
        self.color = pygame.Color('light blue')
        self._bonus = ['+30% Ranged damage', '+50% Souls Gathered', 'Spawns a snowy companion']
        self._soul = .5
        self.arrow_boost = .3
        self.update_descript()


class MetalArmor(BaseArmor):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Full Metal Armor'
        self.hp = pow * 1.14
        self.color = pygame.Color('grey')
        self.protect = .65
        self._bonus = ['35% Damage Reduction', '30% chance to negate damage', '+30% Melee damage', '100% Longer roll cooldown']
        self.dmg_mul = .3
        self.update_descript()

    def _protect(self, damage):
        if random.randint(1, 10) < self.get_ench('Deflect') * 2 + 1:
            return 0
        if random.randint(1, 10) < 4:
            return 0
        return damage * .65 * self.prot_dict[self.get_ench('Protection')]

    def roll(self, game):
        super().roll(game)
        game.player.roll_cooldown *= 2


class SpiderArmor(BaseArmor):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Spider Armor'
        self.hp = pow * 1.08
        self.color = pygame.Color('black')
        self._bonus = ['+25% Melee attack speed', '6% Lifesteal aura']
        self.attack_speed = .25
        self.life_aura = .06
        self.update_descript()


class MercenaryArmor(BaseArmor):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Mercenary Armor'
        self.hp = pow + 3
        self.color = pygame.Color('red')
        self._bonus = ['35% Damage reduction', '+20% Weapon damage boost aura']
        self.dmg_mul = .2
        self.protect = .65
        self.update_descript()


class DeathCapMushroom(Artifact):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Death Cap Mushroom'
        self.maxcooldown = 20
        self.pow = pow

    def draw(self, game):
        super().draw(game)
        pygame.draw.rect(game.screen, pygame.Color('tan'),
                         pygame.Rect(self.x + 12, self.y + 20, 6, 13))
        pygame.draw.circle(game.screen, pygame.Color(
            'purple'), (self.x + 15, self.y + 15), 8)

    def use(self, game):
        if super().use(game):
            if game.player.effects['strength'] < 10 + (self.pow * .01):
                game.player.effects['strength'] = 10 + (self.pow * .01)
            if game.player.effects['speed'] < 10 + (self.pow * .03):
                game.player.effects['speed'] = 10 + (self.pow * .03)


class FlameQuiver(Artifact):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Flame Quiver'
        self.maxcooldown = 4
        self.pow = pow

    def draw(self, game):
        super().draw(game)
        pygame.draw.line(game.screen, pygame.Color('brown'),
                         (self.x, self.y + 20), (self.x + 15, self.y + 5), 10)
        pygame.draw.line(game.screen, pygame.Color('red'),
                         (self.x + 15, self.y + 5), (self.x + 20, self.y), 2)
        pygame.draw.line(game.screen, pygame.Color('red'),
                         (self.x + 20, self.y + 5), (self.x + 25, self.y), 2)

    def use(self, game):
        if super().use(game):
            game.player.nextartype = 'flame'


class ExplodingQuiver(Artifact):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Exploding Quiver'
        self.maxcooldown = 3
        self._arrow = dungeon_arrows.ExplodingArrow
        self.pow = pow

    def draw(self, game):
        super().draw(game)
        pygame.draw.line(game.screen, pygame.Color('brown'),
                         (self.x, self.y + 20), (self.x + 15, self.y + 5), 10)
        pygame.draw.line(game.screen, pygame.Color('white'),
                         (self.x + 15, self.y + 5), (self.x + 20, self.y), 2)
        pygame.draw.line(game.screen, pygame.Color('white'),
                         (self.x + 20, self.y + 5), (self.x + 25, self.y), 2)

    def use(self, game):
        if super().use(game):
            game.player.nextartype = 'explode'


class Beacon(Artifact):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Corrupted Beacon'
        self.maxcooldown = 3
        self.pow = pow
        self.using = False
        self._gives_kill = 1
        # self._needed = 30

    def draw(self, game):
        super().draw(game)
        pygame.draw.rect(game.screen, pygame.Color('white'),
                         pygame.Rect(self.x, self.y, 20, 20))
        pygame.draw.rect(game.screen, pygame.Color('purple'),
                         pygame.Rect(self.x + 2, self.y + 2, 16, 16))

    def get_ends(self, game):
        x, y = pygame.mouse.get_pos()
        px, py = game.player.rect.x, game.player.rect.y
        lx1, ly1 = x - px, y - py
        hyp1 = math.sqrt(lx1 ** 2 + ly1 ** 2)
        angle = math.acos(lx1 / hyp1)
        lx2 = math.cos(angle) * 5000  # 5000 length
        ly2 = math.sin(angle) * 5000
        if y < py:
            ly2 = -ly2
        return [(game.player.rect.x, game.player.rect.y), (game.player.rect.x + lx2, game.player.rect.y + ly2)]

    def _draw(self, game):
        ends = self.get_ends(game)
        pygame.draw.line(game.screen, pygame.Color(
            'purple'), ends[0], ends[1], 30)

    def cancel(self):
        self.using = False

    def use(self, game, a=None):
        if super().use(game):
            self.using = True
            while game.player.kills > 0 and self.using:
                self.wait(game, 0.2)
                for enemy in game.enemies:
                    start, end = self.get_ends(game)
                    dx = (end[0] - start[0]) / 1000
                    dy = (end[1] - start[1]) / 1000
                    did = False
                    for i in range(300):
                        if did:
                            break
                        if enemy.rect.x < start[0] + (i*dx) < enemy.rect.x + enemy.rect.w:
                            for j in range(300):
                                if did:
                                    break
                                if enemy.rect.y < start[1] + (i*dy) < enemy.rect.y + enemy.rect.h:
                                    enemy.take_damage(3 + (self.pow * .1))
                                    did = True
                self.wait(game, 0.2)
                for enemy in game.enemies:
                    start, end = self.get_ends(game)
                    dx = (end[0] - start[0]) / 1000
                    dy = (end[1] - start[1]) / 1000
                    did = False
                    for i in range(300):
                        if did:
                            break
                        if enemy.rect.x < start[0] + (i*dx) < enemy.rect.x + enemy.rect.w:
                            for j in range(300):
                                if did:
                                    break
                                if enemy.rect.y < start[1] + (i*dy) < enemy.rect.y + enemy.rect.h:
                                    enemy.take_damage(3 + (self.pow * .1))
                                    did = True
                self.wait(game, 0.2)
                for enemy in game.enemies:
                    start, end = self.get_ends(game)
                    dx = (end[0] - start[0]) / 1000
                    dy = (end[1] - start[1]) / 1000
                    did = False
                    for i in range(300):
                        if did:
                            break
                        if enemy.rect.x < start[0] + (i*dx) < enemy.rect.x + enemy.rect.w:
                            for j in range(300):
                                if did:
                                    break
                                if enemy.rect.y < start[1] + (i*dy) < enemy.rect.y + enemy.rect.h:
                                    enemy.take_damage(3 + (self.pow * .1))
                                    did = True
                self.wait(game, 0.2)
                for enemy in game.enemies:
                    start, end = self.get_ends(game)
                    dx = (end[0] - start[0]) / 1000
                    dy = (end[1] - start[1]) / 1000
                    did = False
                    for i in range(300):
                        if did:
                            break
                        if enemy.rect.x < start[0] + (i*dx) < enemy.rect.x + enemy.rect.w:
                            for j in range(300):
                                if did:
                                    break
                                if enemy.rect.y < start[1] + (i*dy) < enemy.rect.y + enemy.rect.h:
                                    enemy.take_damage(3 + (self.pow * .1))
                                    did = True
                game.player.kills -= 1
            self.cooldown = self.maxcooldown


class LightningRod(Artifact):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Lightning Rod'
        self.maxcooldown = 2
        self.pow = pow
        self._needed = 15
        self._gives_kill = 1
        self._enemies = []

    def draw(self, game):
        super().draw(game)
        pygame.draw.line(game.screen, pygame.Color('yellow'),
                         (self.x, self.y + 20), (self.x + 20, self.y), 2)
        pygame.draw.rect(game.screen, pygame.Color('white'),
                         pygame.Rect(self.x - 1, self.y + 19, 2, 2))

    def _draw(self, game):
        x, y = game.player.rect.x, game.player.rect.y
        pygame.draw.lines(game.screen, pygame.Color('yellow'), True, [(x - 5, y - 100), (x + 5, y - 80), (x, y - 60), (x + 20, y - 40), (x + 10, y - 20), (x - 5, y), (x + 5, y + 20)], 3)

    def use(self, game):
        if super().use(game):
            for enemy in game.enemies:
                if math.dist((game.player.rect.x, game.player.rect.y), (enemy.rect.x, enemy.rect.y)) < 100:
                    self._enemies.append(enemy)
            self._draw(game)
            pygame.display.update()
            self.wait(game, 2)
            for enemy in self._enemies:
                enemy.take_damage(40 + (self.pow * .01))
            self._enemies.clear()


class GongWeakening(Artifact):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Gong of Weakening'
        self.maxcooldown = 20
        self.pow = pow
        # self._needed = 5

    def draw(self, game):
        super().draw(game)
        pygame.draw.lines(game.screen, pygame.Color('brown'), False, [
                          (self.x, self.y + 10), (self.x, self.y), (self.x + 20, self.y), (self.x + 20, self.y + 10)], 2)
        pygame.draw.circle(game.screen, pygame.Color(
            'light grey'), (self.x + 10, self.y + 15), 10)

    def use(self, game):
        if super().use(game):
            for enemy in game.enemies:
                if distance_to(game.player, enemy) < 400:
                    if enemy.effects['weakness'] < 20 + (self.pow * .005):
                        enemy.effects['weakness'] = 20 + (self.pow * .005)
                    if enemy.effects['slowness'] < 10 + (self.pow * .005):
                        enemy.effects['slowness'] = 10 + (self.pow * .005)


class ShockPowder(Artifact):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Shock Powder'
        self.maxcooldown = 10
        self.pow = pow
        # self._needed = 10

    def draw(self, game):
        super().draw(game)
        pygame.draw.rect(game.screen, pygame.Color('yellow'),
                         pygame.Rect(self.x, self.y + 3, 20, 10))
        pygame.draw.rect(game.screen, pygame.Color('purple'),
                         pygame.Rect(self.x + 7, self.y, 6, 3))

    def use(self, game):
        if super().use(game):
            for enemy in game.enemies:
                if distance_to(game.player, enemy) < 200:
                    enemy.take_damage(5 + (self.pow * .01))
                    enemy.knockback(50, game.player)
                    enemy.give_unmoving(2 + (self.pow * .02), 'stunned')


class TotemRegeneration(Artifact):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Totem of Regeneration'
        self.maxcooldown = 10
        self.pow = pow
        # self._needed = 3

    def draw(self, game):
        super().draw(game)
        pygame.draw.rect(game.screen, pygame.Color('brown'),
                         pygame.Rect(self.x + 5, self.y + 5, 10, 15))
        pygame.draw.circle(game.screen, pygame.Color(
            'red'), (self.x + 10, self.y + 12), 5)

    def use(self, game):
        if super().use(game):
            if game.player.effects['regeneration'] < 10 + (self.pow * .2):
                game.player.effects['regeneration'] = 10 + (self.pow * .2)


class BootsOfSwiftness(Artifact):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Boots of Swiftness'
        self.maxcooldown = 10
        self.pow = pow
        # self._needed = 4

    def draw(self, game):
        super().draw(game)
        pygame.draw.rect(game.screen, pygame.Color('blue'),
                         pygame.Rect(self.x, self.y, 5, 10))
        pygame.draw.rect(game.screen, pygame.Color('blue'),
                         pygame.Rect(self.x + 10, self.y, 5, 10))

    def use(self, game):
        if super().use(game):
            if game.player.effects['speed'] < 3 + (self.pow * .05):
                game.player.effects['speed'] = 3 +  (self.pow * .05)


class TotemOfShielding(Artifact):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Totem of Shielding'
        self.maxcooldown = 15
        self.pow = pow
        # self._needed = 10

    def draw(self, game):
        super().draw(game)
        pygame.draw.rect(game.screen, pygame.Color('blue'),
                         pygame.Rect(self.x + 5, self.y + 5, 10, 15))

    def use(self, game):
        if super().use(game):
            if game.player.effects['resistance'] < 10 + (self.pow * .01):
                game.player.effects['resistance'] = 10 + (self.pow * .01)
            game.player.hp += 3


class SoulHealer(Artifact):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Soul Healer'
        self.maxcooldown = 10
        self.pow = pow
        self._needed = 50
        self._gives_kill = 1

    def draw(self, game):
        super().draw(game)
        pygame.draw.rect(game.screen, pygame.Color('purple'),
                         pygame.Rect(self.x + 5, self.y + 5, 15, 15))

    def use(self, game):
        if super().use(game):
            game.player.hp += random.randint(10, 30) + (self.pow * .05)


class Harvester(Artifact):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Harvester'
        self.maxcooldown = 10
        self.pow = pow
        self._needed = 40
        self._enemies = []
        self._gives_kill = 1

    def draw(self, game):
        super().draw(game)
        pygame.draw.rect(game.screen, pygame.Color('blue'),
                         pygame.Rect(self.x + 5, self.y + 5, 10, 15))
        pygame.draw.rect(game.screen, pygame.Color('light blue'),
                         pygame.Rect(self.x + 7, self.y + 7, 6, 11))

    def _draw(self, game):
        pygame.draw.circle(game.screen, pygame.Color('light blue'), (game.player.rect.x, game.player.rect.y), 300)

    def use(self, game):
        if super().use(game):
            for enemy in game.enemies:
                if distance_to(game.player, enemy) < 300:
                    self._enemies.append(enemy)
            self._draw(game)
            pygame.display.update()
            self.wait(game, 2)
            for enemy in self._enemies:
                enemy.take_damage(30 + (self.pow * .3))
                enemy.knockback(50, game.player)
            self._enemies.clear()


class LightFeather(Artifact):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Light Feather'
        self.maxcooldown = 5
        self.pow = pow
        # self._needed = 10
        self._enemies = []

    def draw(self, game):
        super().draw(game)
        pygame.draw.circle(game.screen, pygame.Color(
            'white'), (self.x + 5, self.y + 10), 5)
        pygame.draw.circle(game.screen, pygame.Color(
            'blue'), (self.x + 10, self.y + 5), 5)
        pygame.draw.line(game.screen, pygame.Color('brown'),
                         (self.x - 3, self.y + 3), (self.x + 5, self.y + 5), 2)

    def use(self, game):
        if super().use(game):
            count = 0
            for enemy in game.enemies:
                if distance_to(game.player, enemy) < 10:
                    self._enemies.append(enemy)
                    count += 1
            for enemy in self._enemies:
                enemy.take_damage(5)
                enemy.knockback(50, game.player)
                enemy.give_unmoving(3 + (self.pow * .05), 'stunned')
            self._enemies.clear()


class IronHideAmulet(Artifact):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Iron Hide Amulet'
        self.maxcooldown = 15
        self.pow = pow
        # self._needed = 2

    def draw(self, game):
        super().draw(game)
        pygame.draw.rect(game.screen, pygame.Color('dark grey'),
                         pygame.Rect(self.x + 5, self.y + 5, 15, 15))
        pygame.draw.rect(game.screen, pygame.Color('green'),
                         pygame.Rect(self.x + 7, self.y + 7, 11, 11))

    def use(self, game):
        if super().use(game):
            if game.player.effects['resistance'] < 4 + (self.pow * 0.3):
                game.player.effects['resistance'] = 4 + (self.pow * 0.3)


class WindHorn(Artifact):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Wind Horn'
        self.maxcooldown = 5
        self.pow = pow
        # self._needed = 10

    def draw(self, game):
        super().draw(game)
        pygame.draw.line(game.screen, pygame.Color('light grey'),
                         (self.x, self.y + 15), (self.x + 3, self.y + 13), 1)
        pygame.draw.line(game.screen, pygame.Color('light grey'),
                         (self.x + 3, self.y + 13), (self.x + 9, self.y + 7), 3)
        pygame.draw.line(game.screen, pygame.Color('light grey'),
                         (self.x + 9, self.y + 7), (self.x + 13, self.y + 2), 5)

    def use(self, game):
        if super().use(game):
            to = []
            for enemy in game.enemies:
                if distance_to(game.player, enemy) < 350:
                    to.append(enemy)
            for enemy in to:
                enemy.knockback(400, game.player)
                if enemy.effects['slowness'] < 5 + (self.pow * .05):
                    enemy.effects['slowness'] = 5 + (self.pow * .05)
                if enemy.effects['weakness'] < 5 + (self.pow * .05):
                    enemy.effects['weakness'] = 5 + (self.pow * .05)


class GolemKit(Artifact):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Golem Kit'
        self.maxcooldown = 1
        self.pow = pow
        self._golem = None
        self._ready = True
        # self._needed = 1
        self.col = pygame.Color(250, 250, 250, 255)

    def draw(self, game):
        super().draw(game)
        # pygame.draw.line(game.screen, self.col, (self.x, self.y), (self.x + 15, self.y + 15), 3)
        pygame.draw.rect(game.screen, self.col,
                         pygame.Rect(self.x, self.y + 5, 15, 5))
        pygame.draw.rect(game.screen, self.col, pygame.Rect(
            self.x + 5, self.y + 10, 5, 5))
        pygame.draw.rect(game.screen, pygame.Color('orange'),
                         pygame.Rect(self.x + 5, self.y, 5, 5))

    def check_cooldown(self, game):
        super().check_cooldown(game)
        if (not self._ready) and self._golem and (self._golem.hp <= 0 or self._golem not in game.helpfuls):
            self._isdead()

    def _isdead(self):
        self.cooldown = 45
        self._ready = True

    def use(self, game):
        if self._ready and super().use(game):
            self._golem = dungeon_helpful.Golem(game.player.rect.x, game.player.rect.y, self.pow)
            game.helpfuls.append(self._golem)
            self._ready = False


class TastyBone(Artifact):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Tasty Bone'
        self.maxcooldown = 1
        self.pow = pow
        # self._needed = 1
        self._wolf = None
        self._ready = True

    def check_cooldown(self, game):
        super().check_cooldown(game)
        if (not self._ready) and self._wolf and (self._wolf.hp <= 0 or self._wolf not in game.helpfuls):
            self._isdead()

    def _isdead(self):
        self.cooldown = 30
        self._ready = True

    def draw(self, game):
        super().draw(game)
        pygame.draw.line(game.screen, pygame.Color('white'),
                         (self.x, self.y + 13), (self.x + 2, self.y + 15), 2)
        pygame.draw.line(game.screen, pygame.Color('white'),
                         (self.x + 13, self.y), (self.x + 15, self.y + 2), 2)
        pygame.draw.line(game.screen, pygame.Color(
            'white'), (self.x + 1, self.y + 14), (self.x + 14, self.y + 1), 2)

    def use(self, game):
        if self._ready and super().use(game):
            self._wolf = dungeon_helpful.Wolf(
                game.player.rect.x, game.player.rect.y, self.pow)
            game.helpfuls.append(self._wolf)
            self._ready = False


#Incoming complete rewrite of loot system
wloot = [i for i in Sword.__subclasses__()] + [i for i in Axe.__subclasses__()] + [i for i in Fist.__subclasses__()] + [i for i in Knife.__subclasses__()] + [i for i in Fist.__subclasses__()] + [i for i in Mallet.__subclasses__()] + [i for i in Bow.__subclasses__()] + [i for i in Crossbow.__subclasses__()]

cloot = [TNT(), Apple(), Bread(), Pork(), StrengthPotion(), SwiftnessPotion(), ShadowBrew(), CookedSalmon(
), SweetBrew(), '15 arrows', '25 arrows', '35 arrows', '5 arrows', '10 arrows', '20 arrows', '30 arrows']

arloot = [i for i in BaseArmor.__subclasses__()]

aloot = [i for i in Artifact.__subclasses__()]

sloot = arloot + aloot + cloot

everything = [i(0) for i in BaseArmor.__subclasses__()] + [i(0) for i in Artifact.__subclasses__()] + [i() for i in Consumable.__subclasses__()] + [i(0) for i in Bow.__subclasses__()] + [i(0) for i in Crossbow.__subclasses__()] + [i(0) for i in Sword.__subclasses__()] + [i(0) for i in Axe.__subclasses__()] + [i(0) for i in Knife.__subclasses__()] + [i(0) for i in Scythe.__subclasses__()] + [i(0) for i in Fist.__subclasses__()] + [i(0) for i in Mallet.__subclasses__()]
