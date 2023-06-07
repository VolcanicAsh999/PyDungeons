import pygame
import random
import dungeon_arrows
import dungeon_misc
import dungeon_settings
import dungeon_helpful
import time
import math
from threading import Thread


class Help:
    def __init__(self, r):
        self.rect = r


def distance_to(target1, target2):
    return math.dist((target1.rect.x, target1.rect.y), (target2.rect.x, target2.rect.y))


class BaseMeleeWeapon:
    def __repr__(self):
        return f'{self.name}(damage={self.damage}, cooldown={self.cooldown}, reach={self.reach}, num={self.num}, knockback={self.knockback}, enchantments=[{", ".join(self._bonus)}], speed={self._speed})'

    def __init__(self, pow):
        self.damage = 0
        self.cooldown = 0
        self.reach = 0
        self.num = float('inf')
        self.knockback = 0
        self.descript = ''
        self.name = ''
        self.x = 0
        self.y = 0
        self._spent = 0
        self._enchant = 0
        self._speed = 0
        self._kills = 0
        self._bonus = []
        self._ = 1
        self.pow = 0

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
        self.draw(game)

    def draw(self, game):
        pass

    def salvage(self, player):
        player.emeralds += random.randint(3, 7) + self._enchant
        player.level += self._spent

    def enchant(self, spent, game):
        self._spent += spent
        if spent == 1:
            self.apply_enchant(1, game)
            return 0
        elif spent == 2:
            self.apply_enchant(2, game)
            return 0
        elif spent == 3:
            self.apply_enchant(3, game)
            return 0
        else:
            self.apply_enchant(4, game)
            return spent - 4

    def update_descript(self):
        if type(self.damage) == float:
            self.damage = random.choice([int(self.damage), int(self.damage) + 1])
        if self.damage < 1: self.damage = 1
        self.descript = ['', '', '', '', '', '']
        self.descript[1] = f'Cooldown: {self.cooldown}'
        self.descript[3] = f'Damage: {self.damage}'
        self.descript[2] = f'Reach: {self.reach}'
        self.descript[0] = f'Knockback: {self.knockback}'
        self.descript[4] = f'Speed increase: {self._speed}'
        if self._bonus:
            self.descript += self._bonus

    def apply_enchant(self, level, game):
        if level == 2:
            enchant = random.choice(['Chains'])
            if enchant == 'Chains':
                self._bonus.append('Chains')
        elif level == 3:
            enchant = random.choice(['Leeching I', 'Chains'])
            if enchant == 'Leeching I':
                self._bonus.append('Leeching I')
            elif enchant == 'Chains':
                self._bonus.append('Chains')
        elif level == 4:
            enchant = random.choice(['Leeching I', 'Leeching II', 'Radiance', 'Chains'])
            if enchant == 'Radiance':
                self._bonus.append('Radiance')
            elif enchant == 'Chains':
                self._bonus.append('Chains')
            elif enchant == 'Leeching I':
                self._bonus.append('Leeching I')
            elif enchant == 'Leeching II':
                if 'Leeching I' in self._bonus: self._bonus.remove('Leeching I')
                self._bonus.append('Leeching II')

    def attack(self, enemy, player, damage, knockback):
        enemy.take_damage(damage)
        enemy.knockback(knockback, player)
        dungeon_settings.weapon_hit.play()
        if 'Relentless Combo' in self._bonus:
            self._ += 1
            if self._ >= 5:
                self._ = 1
                self.damage += 1
                if self.damage > 30:
                    self.damage = 30
                else:
                    self.update_descript()
        if 'Radiance' in self._bonus and random.randint(0, 10) == 0:
            #for x in game.helpfuls:
            #    if distance_to(x, game.player) < 100:
            #        x.hp += 5
            player.hp += 5
        if 'Chains' in self._bonus:
            enemy.give_unmoving(5, 'chains')
        if 'Leeching I' in self._bonus:
            player.hp += round(damage / 5)
        elif 'Leeching II' in self._bonus:
            player.hp += round(damage / 3)

    def speed(self, amount):
        self._speed += amount

    def get_power(self):
        return self.pow
    

class BaseRangeWeapon:
    def __repr__(self):
        return f'{self.name}(cooldown = {self.cooldown}, damage={self.arrow["damage"]}, knockback={self.arrow["knockback"]}, type={self.arrow["name"]}, speed={self._speed}, enchantments=[{", ".join(self._bonus)}])'

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
        self.update_descript()

    def shoot(self, game, player, t):
        arrow = t((player.rect.x, player.rect.y), pygame.mouse.get_pos(), self.arrow['damage'] + self._is_increased, self.arrow['knockback'], player, chain=(
            'Chain Reaction' in self._bonus), chainstack=self._amount_chained, growing=('Growing' in self._bonus))
        game.arrows.append(arrow)
        dungeon_settings.bow_shoot.play()
        if 'Infinity' in self._bonus and random.randint(0, 1) == 0:
            game.player.arrows += 1

    def render(self, x, y, game):
        self.x = x
        self.y = y
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

    def enchant(self, spent, game):
        self._spent += spent
        if spent == 1:
            self.apply_enchant(1, game)
            return 0
        elif spent == 2:
            self.apply_enchant(2, game)
            return 0
        elif spent == 3:
            self.apply_enchant(3, game)
            return 0
        else:
            self.apply_enchant(4, game)
            return spent - 4

    def apply_enchant(self, level, game):
        if level == 3:
            enchant = random.choice(['Flame', 'Chain Reaction', 'Growing'])
            if enchant == 'Chain Reaction':
                self._bonus.append('Chain Reaction')
                self.chain()
            elif enchant == 'Growing':
                self._bonus.append('Growing')
            elif enchant == 'Flame':
                self._bonus.append('Flame')
        elif level == 4:
            enchant = random.choice(['Infinity', 'Chain Reaction', 'Growing', 'Flame'])
            if enchant == 'Infinity':
                self._bonus.append('Infinity')
            elif enchant == 'Chain Reaction':
                self._bonus.append('Chain Reaction')
                self.chain()
            elif enchant == 'Growing':
                self._bonus.append('Growing')
            elif enchant == 'Flame':
                self._bonus.append('Flame')
                self.arrow['type'] = dungeon_arrows.FlamingArrow

    def speed(self, amount):
        self._speed += amount

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
        self.descript[4] = f'Speed increase: {self._speed}'
        if self._bonus:
            self.descript += self._bonus

    def salvage(self, player):
        player.emeralds += random.randint(3, 7) + self._enchant
        player.level += self._spent

    def get_power(self):
        return self.pow
    

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


class BaseArmor:
    def __repr__(self):
        return f'{self.name}(protection={self.protect}, speed={self._speed}, hp={self.hp}, enchantments=[{", ".join(self._bonus)}]'

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
        self._didboost = False
        self.arrows = 0
        self.pow = pow

    def render(self, x, y, game):
        self.x = x
        self.y = y
        if game.player.hp < 10 and 'Final Shout' in self._bonus:
            # self._bonus.remove('Final Shout')
            for artifact in [game.player.a1, game.player.a2, game.player.a3]:
                if artifact is None:
                    continue
                temp = artifact.cooldown
                artifact.cooldown = 0
                artifact.use(game)
                artifact.cooldown = temp
        if 'Frenzied' in self._bonus and game.player.hp < 20 and not self._didboost:
            self._didboost = True
            game.player.attack_speed += 1
        elif 'Frenzied' in self._bonus and self._didboost and game.player.hp >= game.player.hpmax / 2:
            self._didboost = False
            game.player.attack_speed -= 1
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
        if type(self.hp) == float:
            self.hp = random.choice([int(self.hp), int(self.hp) + 1])
        self.descript = ['', '']
        self.descript[0] = f'Armor health: {self.hp}'
        self.descript[1] = f'Speed bonus: {self._speed}'
        if self._bonus:
            self.descript += self._bonus

    def salvage(self, player):
        player.emeralds += random.randint(3, 7) + self._enchant
        player.level += self._spent

    def enchant(self, spent, game):
        self._spent += spent
        if spent == 1:
            self.apply_enchant(1, game)
            return 0
        elif spent == 2:
            self.apply_enchant(2, game)
            return 0
        elif spent == 3:
            self.apply_enchant(3, game)
            return 0
        else:
            self.apply_enchant(4, game)
            return spent - 4

    def apply_enchant(self, level, game):
        if level == 2:
            enchant = random.choice(['Frenzied'])
            if enchant == 'Frenzied':
                self._bonus.append('Frenzied')
        elif level == 3:
            enchant = random.choice(['Final Shout', 'Frenzied'])
            if enchant == 'Final Shout':
                self._bonus.append('Final Shout')
            elif enchant == 'Frenzied':
                self._bonus.append('Frenzied')
        elif level == 4:
            enchant = random.choice(['Final Shout', 'Frenzied'])
            if enchant == 'Final Shout':
                self._bonus.append('Final Shout')
            elif enchant == 'Frenzied':
                self._bonus.append('Frenzied')

    def speed(self, amount):
        self._speed += amount

    def _protect(self, damage):
        return self.protect * damage

    def get_power(self):
        return self.pow

    def do_special(self, player, enemy, game):
        pass


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
        self.knockback = 15
        self.cooldown = .9
        self.reach = 20
        self.damage = pow
        self.update_descript()


class StoneSword(Sword):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Stone Sword'
        self.knockback = 20
        self.cooldown = .8
        self.reach = 25
        self.damage = pow * 1.05
        self.bladecolor = pygame.Color('dark grey')
        self.update_descript()


class IronSword(Sword):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Iron Sword'
        self.knockback = 20
        self.cooldown = .7
        self.reach = 25
        self.damage = pow * 1.08
        self.bladecolor = pygame.Color('light grey')
        self.update_descript()


class GoldenSword(Sword):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Golden Sword'
        self.knockback = 13
        self.cooldown = .8
        self.reach = 20
        self.damage = pow
        self.bladecolor = pygame.Color('gold')
        self.update_descript()


class DiamondSword(Sword):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Diamond Sword'
        self.knockback = 24
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
        self.knockback = 20
        self.cooldown = .4
        self.reach = 20
        self.damage = pow + 8
        self.bladecolor = pygame.Color('red')
        self._speed = 2
        self.update_descript()


class WoodAxe(Axe):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Wood Axe'
        self.knockback = 30
        self.cooldown = 1.2
        self.reach = 30
        self.damage = pow + 2
        self.update_descript()


class IronAxe(Axe):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Iron Axe'
        self.knockback = 35
        self.cooldown = 1.13
        self.reach = 30
        self.damage = 3 + (pow * 1.05)
        self.bladecolor = pygame.Color('grey')
        self.update_descript()


class GoldenAxe(Axe):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Golden Axe'
        self.knockback = 20
        self.cooldown = 1.18
        self.reach = 25
        self.damage = 2 + (pow * .1)
        self.update_descript()
        self.bladecolor = pygame.Color('gold')


class WeightedAxe(Axe):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Weighted Axe'
        self.knockback = 50
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
        self.knockback = 40
        self.cooldown = 1.22
        self.reach = 30
        self.damage = pow * 1.03
        self.bladecolor = pygame.Color('grey')
        self.handlecolor = pygame.Color('purple')
        self.update_descript()

    def attack(self, enemy, player, damage, knockback):
        super().attack(enemy, player, damage, knockback)
        if enemy.effects['poison'] < 5:
            enemy.effects['poison'] = 5


class IronMallet(Mallet):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Iron Mallet'
        self.blockcolor = pygame.Color('grey')
        self.knockback = 50
        self.cooldown = 1
        self.reach = 30
        self.damage = pow + 4
        self.update_descript()


class BigMallet(Mallet):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Big Mallet'
        self.blockcolor = pygame.Color('light blue')
        self.knockback = 150
        self.cooldown = 0.9
        self.reach = 60
        self.damage = 1 + (pow * .3)
        self.update_descript()


class HerosMallet(Mallet):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Hero\'s Mallet'
        self.blockcolor = pygame.Color('dark blue')
        self.knockback = 70
        self.cooldown = 1.06
        self.reach = 40
        self.damage = pow + 10
        self.update_descript()


class XPGatherer(Mallet):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'XP Gatherer'
        self.blockcolor = pygame.Color('green')
        self.knockback = 20
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
        self.update_descript()


class KillFist(Fist):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Kill Fist'
        self.fistcolor = pygame.Color('black')
        self.knockback = 2
        self.cooldown = .06
        self.reach = 10
        self.damage = 1 + (pow * .07)
        self.update_descript()


class SoulFists(Fist):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Soul Fists'
        self.fistcolor = pygame.Color('yellow')
        self.knockback = 3
        self.cooldown = .06
        self.reach = 15
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
        self.knockback = 20
        self.cooldown = 0.9
        self.reach = 30
        self.damage = 3 + (pow * .05)
        self.update_descript()

    def attack(self, enemy, player, damage, knockback):
        super().attack(enemy, player, damage, knockback)

        if enemy.hp <= 0:
            if player.effects['speed'] < 5:
                player.effects['speed'] = 5


class TempestKnife(Knife):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Tempest Knife'
        self.bladecolor = pygame.Color('light blue')
        self.knockback = 20
        self.cooldown = 0.9
        self.reach = 30
        self.damage = 3 + (pow * .05)
        self.update_descript()


class FangsOfFrost(Knife):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Fangs of Frost'
        self.bladecolor = pygame.Color('light blue')
        self.knockback = 10
        self.cooldown = 0.2
        self.reach = 15
        self.damage = 0.5 + (pow * .05)
        self.update_descript()

    def attack(self, enemy, player, damage, knockback):
        super().attack(enemy, player, damage, knockback)
        enemy.give_unmoving(3)


class DarkKatana(Knife):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Dark Katana'
        self.bladecolor = pygame.Color('purple')
        self.handlecolor = pygame.Color('black')
        self.knockback = 10
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
        self.knockback = 5
        self.cooldown = .07
        self.reach = 20
        self.damage = pow + 1
        self._kills = 2
        self.update_descript()


class JailorScythe(Scythe):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Jailor\'s Scythe'
        self.bladecolor = pygame.Color('white')
        self.handlecolor = pygame.Color('purple')
        self.knockback = 10
        self.cooldown = 0.8
        self.reach = 70
        self.damage = 6
        self.update_descript()

    def attack(self, enemy, player, damage, knockback):
        super().attack(enemy, player, damage, knockback)
        if random.randint(0, 10) == 0 and enemy.speed > 0:
            enemy.give_unmoving(3, 'chains')


class GraveBane(Scythe):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Grave Bane'
        self.bladecolor = pygame.Color('yellow')
        self.handlecolor = pygame.Color('yellow')
        self.knockback = 10
        self.cooldown = 0.76
        self.reach = 65
        self.damage = 10 + (pow * .3)
        self.update_descript()


class PurpleStorm(Bow):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Purple Storm'
        self.bowcolor = pygame.Color('purple')
        self.cooldown = .06
        self.arrow['damage'] = pow
        self.update_descript()


class InfinityBow(Bow):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Infinity Bow'
        self.bowcolor = pygame.Color('black')
        self._bonus.append('Infinity')
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


class ChainCrossbow(Crossbow):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Chain Crossbow'
        self.bowcolor = pygame.Color('gray')
        self.cooldown = .7
        self._bonus.append('Chain Reaction')
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


class LeatherArmor(BaseArmor):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Leather Armor'
        self.hp = pow
        self.color = pygame.Color('brown')
        self.update_descript()


class ChainArmor(BaseArmor):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Chain Armor'
        self.hp = pow + 2
        self.color = pygame.Color('light grey')
        self.update_descript()


class ReinforcedMail(BaseArmor):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Reinforced Mail'
        self.hp = pow * 1.13
        self.color = pygame.Color('grey')
        self._speed = -1
        self.protect = .65
        self.update_descript()


class HunterArmor(BaseArmor):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Hunter\'s Armor'
        self.hp = pow * .9
        self.arrows = 10
        self.color = pygame.Color('tan')
        self.update_descript()


class HeroArmor(BaseArmor):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Hero\'s Armor'
        self.hp = pow
        self.color = pygame.Color('yellow')
        self.update_descript()

    def render(self, x, y, game):
        super().render(x, y, game)
        if game.player.effects['regeneration'] < 3:
            game.player.effects['regeneration'] = 3


class SoulRobe(BaseArmor):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Soul Robe'
        self.hp = max(pow, pow - 5)
        self.color = pygame.Color('dark grey')
        self._kills = 1
        self.update_descript()


class SplendidRobe(BaseArmor):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Splendid Robe'
        self.hp = pow * .94
        self.color = pygame.Color('purple')
        self.update_descript()

    def render(self, x, y, game):
        super().render(x, y, game)
        if game.player.effects['strength'] < 3:
            game.player.effects['strength'] = 3


class MysteryArmor(BaseArmor):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Mystery Armor'
        self.hp = pow * round(random.uniform(.93, 1.07), 2)
        self.color = pygame.Color('light grey')
        # self.randomize_modifiers()  # coming soon
        self.update_descript()


class SpelunkerArmor(BaseArmor):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Spelunker Armor'
        self.hp = pow * .86
        self.color = pygame.Color('orange')
        self._bat = None
        self.update_descript()

    def equip(self, game):
        self._bat = dungeon_helpful.Bat(game.player.rect.x, game.player.rect.y)
        game.helpfuls.append(self._bat)

    def remove(self, game):
        self._bat._nowdie = True


class FoxArmor(BaseArmor):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Fox Armor'
        self.hp = pow
        self.color = pygame.Color('orange')
        self.update_descript()

    def _protect(self, damage):
        if random.randint(1, 10) < 4:
            return 0
        return damage


class FrostBite(BaseArmor):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Frost Bite'
        self.hp = pow - 1
        self.color = pygame.Color('light blue')
        self.update_descript()

    def render(self, x, y, game):
        super().render(x, y, game)
        if game.player.range and game.player.range._is_increased < 2:
            game.player.range._is_increased = 2


class MetalArmor(BaseArmor):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Full Metal Armor'
        self.hp = pow * 1.14
        self.color = pygame.Color('grey')
        self._speed = -1
        self.protect = .65
        self.update_descript()

    def _protect(self, damage):
        if random.randint(1, 10) < 4:
            return 0
        return damage * .65


class SpiderArmor(BaseArmor):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Spider Armor'
        self.hp = pow * 1.08
        self.color = pygame.Color('black')
        self._speed = 1
        self.update_descript()


class MercenaryArmor(BaseArmor):
    def __init__(self, pow):
        super().__init__(pow)
        self.name = 'Mercenary Armor'
        self.hp = pow + 3
        self.color = pygame.Color('red')
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
        pygame.draw.lines(game.screen, pygame.Color('yellow'), [(x - 5, y - 100), (x + 5, y - 80), (x, y - 60), (x + 20, y - 40), (x + 10, y - 20), (x - 5, y), (x + 5, y + 20)], 3)

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
            self._golem = dungeon_helpful.Golem(game.player.rect.x, game.player.rect.y, pow)
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
