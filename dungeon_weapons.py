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

    def __init__(self):
        self.damage = 0
        self.cooldown = 0
        self.reach = 0
        self.num = 0
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
            self.check()
            return 0
        elif spent == 2:
            self.apply_enchant(2, game)
            self.check()
            return 0
        elif spent == 3:
            self.apply_enchant(3, game)
            self.check()
            return 0
        else:
            self.apply_enchant(4, game)
            self.check()
            return spent - 4

    def check(self):
        if dungeon_settings.DIFFICULTY == 'Default':
            if self.damage > 35:
                self.damage = 35
            if self.knockback > 300:
                self.knockback = 300
            if self.reach > 400:
                self.reach = 400
            if self.num > 30:
                self.num = 30
            if self._speed > 20:
                self._speed = 20
        elif dungeon_settings.DIFFICULTY == 'Adventure':
            if self.damage > 50:
                self.damage = 50
            if self.knockback > 400:
                self.knockback = 400
            if self.reach > 500:
                self.reach = 500
            if self.num > 35:
                self.num = 35
            if self._speed > 25:
                self._speed = 25
        else:
            if self.damage > 70:
                self.damage = 70
            if self.knockback > 600:
                self.knockback = 600
            if self.reach > 600:
                self.reach = 600
            if self.num > 45:
                self.num = 45
            if self._speed > 30:
                self._speed = 30
        self.update_descript()

    def update_descript(self):
        self.descript = ['', '', '', '', '', '']
        self.descript[1] = f'Cooldown: {self.cooldown}'
        self.descript[4] = f'Damage: {self.damage}'
        self.descript[2] = f'Reach: {self.reach}'
        self.descript[0] = f'Knockback: {self.knockback}'
        self.descript[3] = f'Number: {self.num}'
        self.descript[5] = f'Speed increase: {self._speed}'
        if self._bonus:
            self.descript += self._bonus

    def apply_enchant(self, level, game):
        if level == 1:
            enchant = random.choice(
                ['cooldown - 1', 'num + 1', 'knockback + 5', 'reach + 5', 'damage + 1'])
            if enchant == 'cooldown - 1':
                self.cooldown -= 1
            elif enchant == 'num + 1':
                self.num += 1
            elif enchant == 'knockback + 5':
                self.knockback += 5
            elif enchant == 'reach + 5':
                self.reach += 5
            elif enchant == 'damage + 1':
                self.damage += 1
            if self.cooldown < 1:
                self.cooldown = 1
            game.message(
                f'You upgraded {self.name} with the level 1 enchantment {enchant}!')
        elif level == 2:
            enchant = random.choice(['Chains' if 'Chains' not in self._bonus else 'Speed I', 'Speed I', 'cooldown - 1',
                                    'num + 2', 'knockback + 10', 'reach + 5', 'damage + 2', 'cooldown - 2', 'damage + 3', 'reach + 10'])
            if enchant == 'Chains':
                self._bonus.append('Chains')
            elif enchant == 'cooldown - 1':
                self.cooldown -= 1
            elif enchant == 'Speed I':
                self.speed(1)
            elif enchant == 'num + 2':
                self.num += 2
            elif enchant == 'knockback + 10':
                self.knockback += 10
            elif enchant == 'reach + 5':
                self.reach += 5
            elif enchant == 'damage + 2':
                self.damage += 2
            elif enchant == 'cooldown - 2':
                self.cooldown -= 2
            elif enchant == 'damage + 3':
                self.damage += 3
            elif enchant == 'reach + 10':
                self.reach += 10
            if random.randint(0, 4) == 0:
                self.apply_enchant(1, game)
            if self.cooldown < 1:
                self.cooldown = 1
            game.message(
                f'You upgraded {self.name} with the level 2 enchantment {enchant}!')
        elif level == 3:
            enchant = random.choice(['Chains' if 'Chains' not in self._bonus else 'Speed II', 'Chains' if 'Chains' not in self._bonus else 'Speed II', 'Speed I', 'Relentless Combo' if 'Relentless Combo' not in self._bonus else 'Speed I',
                                    'cooldown - 2', 'damage + 3', 'reach + 10', 'reach + 15', 'cooldown - 3', 'damage + 4', 'knockback + 10', 'knockback + 20', 'num + 2', 'num + 3', 'damage + 5'])
            if enchant == 'cooldown - 3':
                self.cooldown -= 3
            elif enchant == 'Speed I':
                self.speed(1)
            elif enchant == 'Speed II':
                self.speed(2)
            elif enchant == 'Relentless Combo':
                self._bonus.append('Relentless Combo')
            elif enchant == 'Chains':
                self._bonus.append('Chains')
            elif enchant == 'num + 2':
                self.num += 2
            elif enchant == 'knockback + 10':
                self.knockback += 10
            elif enchant == 'reach + 15':
                self.reach += 15
            elif enchant == 'damage + 3':
                self.damage += 3
            elif enchant == 'cooldown - 2':
                self.cooldown -= 2
            elif enchant == 'damage + 4':
                self.damage += 4
            elif enchant == 'reach + 10':
                self.reach += 10
            elif enchant == 'knockback + 20':
                self.knockback += 20
            elif enchant == 'num + 3':
                self.num += 3
            elif enchant == 'damage + 5':
                self.damage += 5
            elif enchant == 'reach + 15':
                self.reach += 15
            if random.randint(0, 3) == 0:
                self.apply_enchant(random.randint(1, 2), game)
            if random.randint(0, 1) == 0:
                self.apply_enchant(2, game)
            if random.randint(0, 4) == 0:
                self.apply_enchant(3, game)
            if self.cooldown < 1:
                self.cooldown = 1
            game.message(
                f'You upgraded {self.name} with the level 3 enchantment {enchant}!')
        elif level == 4:
            enchant = random.choice(['Speed I', 'Speed II', 'Chains' if 'Chains' not in self._bonus else 'Speed II', 'Relentless Combo' if 'Relentless Combo' not in self._bonus else 'Speed II', 'cooldown - 3', 'cooldown - 4', 'cooldown - 5',
                                    'reach + 20', 'reach + 15', 'damage + 4', 'damage + 5', 'damage + 6', 'damage + 7', 'knockback + 15', 'knockback + 20', 'knockback + 25', 'num + 3', 'num + 4', 'Radiance' if 'Radiance' not in self._bonus else 'Speed III'])
            if enchant == 'cooldown - 3':
                self.cooldown -= 3
            elif enchant == 'Speed I':
                self.speed(1)
            elif enchant == 'Speed II':
                self.speed(2)
            elif enchant == 'Speed III':
                self.speed(3)
            elif enchant == 'Relentless Combo':
                self._bonus.append('Relentless Combo')
            elif enchant == 'Radiance':
                self._bonus.append('Radiance')
            elif enchant == 'Chains':
                self._bonus.append('Chains')
            elif enchant == 'cooldown - 4':
                self.cooldown -= 4
            elif enchant == 'cooldown - 5':
                self.cooldown -= 5
            elif enchant == 'reach + 20':
                self.reach += 20
            elif enchant == 'reach + 15':
                self.reach += 15
            elif enchant == 'damage + 4':
                self.damage += 4
            elif enchant == 'damage + 5':
                self.damage += 5
            elif enchant == 'damage + 6':
                self.damage += 6
            elif enchant == 'damage + 7':
                self.damage += 7
            elif enchant == 'knockback + 15':
                self.knockback += 15
            elif enchant == 'knockback + 20':
                self.knockback += 20
            elif enchant == 'knockback + 25':
                self.knockback += 25
            elif enchant == 'num + 3':
                self.num += 3
            elif enchant == 'num + 4':
                self.num += 4
            if random.randint(0, 3) != 0:
                self.apply_enchant(random.randint(2, 3), game)
            if random.randint(0, 2) != 0:
                self.apply_enchant(3, game)
            if random.randint(0, 2) == 0:
                self.apply_enchant(4, game)
            if self.cooldown < 1:
                self.cooldown = 1
            game.message(
                f'You upgraded {self.name} with the level 4 enchantment {enchant}!')

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

    def speed(self, amount):
        self._speed += amount

    def get_power(self):
        return (self.damage + (self.knockback // 10) + (self.reach // 5) + (self.num // 3) + (('Relentless Combo' in self._bonus) * 5)) + (('Radiance' in self._bonus) * 20)


class BaseRangeWeapon:
    def __repr__(self):
        return f'{self.name}(cooldown = {self.cooldown}, damage={self.arrow["damage"]}, knockback={self.arrow["knockback"]}, type={self.arrow["name"]}, speed={self._speed}, enchantments=[{", ".join(self._bonus)}])'

    def __init__(self):
        self.numshoot = 1
        self.arrow = {'type': dungeon_arrows.Arrow, 'damage': 2,
                      'knockback': 20, 'name': 'Normal Arrow'}
        self.cooldown = 5
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
        self.update_descript()

    def shoot(self, game, player, t):
        arrow = t((player.rect.x, player.rect.y), pygame.mouse.get_pos(), self.arrow['damage'] + self._is_increased, self.arrow['knockback'], player, chain=(
            'Chain Reaction' in self._bonus), chainstack=self._amount_chained, growing=('Growing' in self._bonus))
        game.arrows.append(arrow)
        dungeon_settings.bow_shoot.play()
        if 'Infinity' in self._bonus:
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
            self.check()
            return 0
        elif spent == 2:
            self.apply_enchant(2, game)
            self.check()
            return 0
        elif spent == 3:
            self.apply_enchant(3, game)
            self.check()
            return 0
        else:
            self.apply_enchant(4, game)
            self.check()
            return spent - 4

    def apply_enchant(self, level, game):
        if level == 1:
            enchant = random.choice(
                ['cooldown - 1', 'damage + 1', 'knockback + 5'])
            if enchant == 'cooldown - 1':
                self.cooldown -= 1
            elif enchant == 'damage + 1':
                self.arrow['damage'] += 1
            elif enchant == 'knockback + 5':
                self.arrow['knockback'] += 5
            if self.cooldown < 1:
                self.cooldown = 1
            game.message(
                f'You upgraded {self.name} with the level 1 enchantment {enchant}!')
        elif level == 2:
            enchant = random.choice(['cooldown - 1', 'cooldown - 2', 'damage + 1',
                                    'damage + 2', 'damage + 3', 'knockback + 5', 'knockback + 10', 'Speed I'])
            if enchant == 'cooldown - 1':
                self.cooldown -= 1
            elif enchant == 'cooldown - 2':
                self.cooldown -= 2
            elif enchant == 'damage + 1':
                self.arrow['damage'] += 1
            elif enchant == 'damage + 2':
                self.arrow['damage'] += 2
            elif enchant == 'damage + 3':
                self.arrow['damage'] += 3
            elif enchant == 'knockback + 5':
                self.arrow['knockback'] += 5
            elif enchant == 'knockback + 10':
                self.arrow['knockback'] = 10
            elif enchant == 'Speed I':
                self.speed(1)
            if random.randint(0, 4) == 0:
                self.apply_enchant(1, game)
            if self.cooldown < 1:
                self.cooldown = 1
            game.message(
                f'You upgraded {self.name} with the level 2 enchantment {enchant}!')
        elif level == 3:
            enchant = random.choice(['cooldown - 2', 'cooldown - 3', 'damage + 2', 'damage + 3', 'damage + 4', 'knockback + 15', 'Speed I', 'Speed II', 'Flame' if 'Flame' not in self._bonus else 'Speed III',
                                    'Growing' if 'Growing' not in self._bonus else 'Speed II', 'Chain Reaction' if 'Chain Reaction' not in self._bonus else 'Speed II'])
            if enchant == 'cooldown - 2':
                self.cooldown -= 2
            elif enchant == 'cooldown - 3':
                self.cooldown -= 3
            elif enchant == 'damage + 2':
                self.arrow['damage'] += 2
            elif enchant == 'damage + 3':
                self.arrow['damage'] += 3
            elif enchant == 'damage + 4':
                self.arrow['damage'] += 4
            elif enchant == 'knockback + 15':
                self.arrow['knockback'] += 15
            elif enchant == 'Speed I':
                self.speed(1)
            elif enchant == 'Speed II':
                self.speed(2)
            elif enchant == 'Chain Reaction':
                self._bonus.append('Chain Reaction')
                self.chain()
            elif enchant == 'Growing':
                self._bonus.append('Growing')
            elif enchant == 'Flame':
                self._bonus.append('Flame')
                self.arrow['type'] = dungeon_arrows.FlamingArrow
            if random.randint(0, 3) == 0:
                self.apply_enchant(random.randint(1, 2), game)
            if random.randint(0, 1) == 0:
                self.apply_enchant(2, game)
            if random.randint(0, 4) == 0:
                self.apply_enchant(3, game)
            if self.cooldown < 1:
                self.cooldown = 1
            game.message(
                f'You upgraded {self.name} with the level 3 enchantment {enchant}!')
        elif level == 4:
            enchant = random.choice(['Infinity' if 'Infinity' not in self._bonus else 'damage + 6', 'cooldown - 4', 'damage + 4', 'damage + 5', 'knockback + 15', 'knockback + 20', 'Speed II', 'Speed III',
                                    'Flame' if 'Flame' not in self._bonus else 'Speed III', 'Chain Reaction' if 'Chain Reaction' not in self._bonus else 'Speed III', 'Growing' if 'Growing' not in self._bonus else 'Speed III'])
            if enchant == 'cooldown - 4':
                self.cooldown -= 4
            elif enchant == 'Infinity':
                self._bonus.append('Infinity')
            elif enchant == 'damage + 4':
                self.arrow['damage'] += 4
            elif enchant == 'damage + 5':
                self.arrow['damage'] += 5
            elif enchant == 'knockback + 15':
                self.arrow['knockback'] += 15
            elif enchant == 'knockback + 20':
                self.arrow['knockback'] += 20
            elif enchant == 'Speed II':
                self.speed(2)
            elif enchant == 'Speed III':
                self.speed(3)
            elif enchant == 'Chain Reaction':
                self._bonus.append('Chain Reaction')
                self.chain()
            elif enchant == 'Growing':
                self._bonus.append('Growing')
            elif enchant == 'Flame':
                self._bonus.append('Flame')
                self.arrow['type'] = dungeon_arrows.FlamingArrow
            if random.randint(0, 3) != 0:
                self.apply_enchant(random.randint(2, 3), game)
            if random.randint(0, 2) != 0:
                self.apply_enchant(3, game)
            if random.randint(0, 2) == 0:
                self.apply_enchant(4, game)
            if self.cooldown < 1:
                self.cooldown = 1
            game.message(
                f'You upgraded {self.name} with the level 4 enchantment {enchant}!')

    def speed(self, amount):
        self._speed += amount

    def chain(self):
        if self._amount_chained == 0:
            self._amount_chained = 1
        else:
            self._amount_chained += 0.1

    def check(self):
        if dungeon_settings.DIFFICULTY == 'Default':
            if self.arrow['damage'] > 20:
                self.arrow['damage'] = 20
            if self.arrow['knockback'] > 100:
                self.arrow['knockback'] = 100
            if self._speed > 25:
                self._speed = 25
        elif dungeon_settings.DIFFICULTY == 'Adventure':
            if self.arrow['damage'] > 30:
                self.arrow['damage'] = 30
            if self.arrow['knockback'] > 150:
                self.arrow['knockback'] = 150
            if self._speed > 30:
                self._speed = 30
        else:
            if self.arrow['damage'] > 40:
                self.arrow['damage'] = 40
            if self.arrow['knockback'] > 200:
                self.arrow['knockback'] = 200
            if self._speed > 35:
                self._speed = 35
        self.update_descript()

    def update_descript(self):
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
        return (self.arrow['damage'] + (self.cooldown // 2) + (('Chain Reaction' in self._bonus) * 4) + (('Infinity' in self._bonus) * 2)) + (('Growing' in self._bonus) * 3) + (('Flame' in self._bonus) * 5)


class Consumable:
    def __repr__(self):
        return f'{self.name}()'

    def __init__(self):
        super().__init__()
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

    def __init__(self):
        super().__init__()
        self.name = 'Artifact'
        self.x = 0
        self.y = 0
        self.cooldown = 0
        self.maxcooldown = 1
        self._needed = 0
        self.pow = 0
        self._last = time.time()

    def render(self, x, y, game):
        self.x = x
        self.y = y
        self.draw(game)

    def draw(self, game):
        t = pygame.font.SysFont('', 20).render(
            self.name, 1, pygame.Color('black'))
        game.screen.blit(t, (self.x, self.y))

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
        return f'{self.name}(protection={self.protect}, speed={self._speed}, enchantments=[{", ".join(self._bonus)}]'

    def __init__(self):
        super().__init__()
        self.name = 'Armor'
        self.protect = 0
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

    def render(self, x, y, game):
        self.x = x
        self.y = y
        if game.player.hp < 10 and 'Final Shout' in self._bonus:
            # self._bonus.remove('Final Shout')
            for artifact in game.player.artifacts:
                if artifact is None:
                    continue
                if type(artifact) == Beacon:
                    continue  # don't use the beacon with final shout
                temp = artifact.cooldown
                artifact.cooldown = 0
                artifact.use(game)
                artifact.cooldown = temp
            game.message(f'{game.pname} used their Final Shout!')
        if 'Frenzied' in self._bonus and game.player.hp < 20 and not self._didboost:
            self._didboost = True
            game.player.attack_speed += 1
        elif 'Frenzied' in self._bonus and self._didboost and game.player.hp >= 20:
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
        self.descript = ['', '']
        self.descript[0] = f'Armor protection: {self.protect}'
        self.descript[1] = f'Speed bonus: {self._speed}'
        if self._bonus:
            self.descript += self._bonus

    def check(self):
        if dungeon_settings.DIFFICULTY == 'Default':
            if self.protect > 20:
                self.protect = 20
            if self._speed > 35:
                self._speed = 35
        elif dungeon_settings.DIFFICULTY == 'Adventure':
            if self.protect > 25:
                self.protect = 25
            if self._speed > 40:
                self._speed = 40
        else:
            if self.protect > 35:
                self.protect = 35
            if self._speed > 50:
                self._speed = 50
        self.update_descript()

    def salvage(self, player):
        player.emeralds += random.randint(3, 7) + self._enchant
        player.level += self._spent

    def enchant(self, spent, game):
        self._spent += spent
        if spent == 1:
            self.apply_enchant(1, game)
            self.check()
            return 0
        elif spent == 2:
            self.apply_enchant(2, game)
            self.check()
            return 0
        elif spent == 3:
            self.apply_enchant(3, game)
            self.check()
            return 0
        else:
            self.apply_enchant(4, game)
            self.check()
            return spent - 4

    def apply_enchant(self, level, game):
        if level == 1:
            enchant = random.choice(
                ['protect + 1', 'protect + 2', 'Speed I', 'Speed I', 'Speed II'])
            if enchant == 'protect + 1':
                self.protect += 1
            elif enchant == 'protect + 2':
                self.protect += 2
            elif enchant == 'Speed I':
                self.speed(1)
            elif enchant == 'Speed II':
                self.speed(2)
            game.message(
                f'You upgraded {self.name} with the level 1 enchantment {enchant}!')
        elif level == 2:
            enchant = random.choice(['protect + 1', 'protect + 2', 'protect + 2',
                                    'Speed I', 'Speed II', 'Speed II', 'Speed III', 'Frenzied'])
            if enchant == 'protect + 1':
                self.protect += 1
            elif enchant == 'protect + 2':
                self.protect += 2
            elif enchant == 'Speed I':
                self.speed(1)
            elif enchant == 'Speed II':
                self.speed(2)
            elif enchant == 'Speed III':
                self.speed(3)
            elif enchant == 'Frenzied':
                self._bonus.append('Frenzied')
            if random.randint(0, 4) == 0:
                self.apply_enchant(1, game)
            game.message(
                f'You upgraded {self.name} with the level 2 enchantment {enchant}!')
        elif level == 3:
            enchant = random.choice(['protect + 2', 'protect + 3', 'Speed II', 'Speed III', 'Speed III',
                                    'Frenzied' if 'Frenzied' not in self._bonus else 'Speed III', 'Final Shout' if 'Final Shout' not in self._bonus else 'Speed III'])
            if enchant == 'protect + 2':
                self.protect += 2
            elif enchant == 'protect + 3':
                self.protect += 3
            elif enchant == 'Speed II':
                self.speed(2)
            elif enchant == 'Speed III':
                self.speed(3)
            elif enchant == 'Final Shout':
                self._bonus.append('Final Shout')
            elif enchant == 'Frenzied':
                self._bonus.append('Frenzied')
            if random.randint(0, 3) == 0:
                self.apply_enchant(random.randint(1, 2), game)
            if random.randint(0, 1) == 0:
                self.apply_enchant(2, game)
            if random.randint(0, 4) == 0:
                self.apply_enchant(3, game)
            game.message(
                f'You upgraded {self.name} with the level 3 enchantment {enchant}!')
        elif level == 4:
            enchant = random.choice(['protect + 3', 'protect + 4', 'protect + 4', 'protect + 5', 'Speed III', 'Speed III', 'Speed IV', 'Frenzied' if 'Frenzied' not in self._bonus else 'Speed IV',
                                    'Frenzied' if 'Frenzied' not in self._bonus else 'Speed V', 'Final Shout' if 'Final Shout' not in self._bonus else 'Speed V'])
            if enchant == 'protect + 3':
                self.protect += 3
            elif enchant == 'protect + 4':
                self.protect += 4
            elif enchant == 'protect + 5':
                self.protect += 5
            elif enchant == 'Speed III':
                self.speed(3)
            elif enchant == 'Speed IV':
                self.speed(4)
            elif enchant == 'Speed V':
                self.speed(5)
            elif enchant == 'Final Shout':
                self._bonus.append('Final Shout')
            elif enchant == 'Frenzied':
                self._bonus.append('Frenzied')
            if random.randint(0, 3) != 0:
                self.apply_enchant(random.randint(2, 3), game)
            if random.randint(0, 2) != 0:
                self.apply_enchant(3, game)
            if random.randint(0, 2) == 0:
                self.apply_enchant(4, game)
            game.message(
                f'You upgraded {self.name} with the level 4 enchantment {enchant}!')

    def speed(self, amount):
        self._speed += amount

    def _protect(self):
        return int(round(self.protect + random.choice([-0.5, -0.4, -0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5])))

    def get_power(self):
        return ((self.protect // 2) + (('Final Shout' in self._bonus) * 3)) + (('Frenzied' in self._bonus) * 2)

    def do_special(self, player, enemy, game):
        pass

    def equip(self, game):
        pass

    def remove(self, game):
        pass


class Sword(BaseMeleeWeapon):
    def __init__(self):
        super().__init__()
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
    def __init__(self):
        super().__init__()
        self.name = 'Axe'
        self.handlecolor = pygame.Color('brown')
        self.bladecolor = pygame.Color('brown')

    def draw(self, game):
        pygame.draw.line(game.screen, self.handlecolor,
                         (self.x, self.y), (self.x + 15, self.y - 15), 3)
        pygame.draw.polygon(game.screen, self.bladecolor, [(
            self.x + 15, self.y - 15), (self.x + 10, self.y - 15), (self.x + 15, self.y - 20)])


class Mallet(BaseMeleeWeapon):
    def __init__(self):
        super().__init__()
        self.name = 'Mallet'
        self.handlecolor = pygame.Color('brown')
        self.blockcolor = pygame.Color('brown')

    def draw(self, game):
        pygame.draw.line(game.screen, self.handlecolor,
                         (self.x, self.y), (self.x + 15, self.y - 15), 3)
        pygame.draw.polygon(game.screen, self.blockcolor, [(
            self.x + 10, self.y - 20), (self.x + 15, self.y - 25), (self.x + 20, self.y - 15), (self.x + 15, self.y - 10)])


class Fist(BaseMeleeWeapon):
    def __init__(self):
        super().__init__()
        self.name = 'Fist'
        self.fistcolor = pygame.Color('brown')

    def draw(self, game):
        pygame.draw.line(game.screen, self.fistcolor,
                         (self.x, self.y), (self.x, self.y), 4)


class Knife(BaseMeleeWeapon):
    def __init__(self):
        super().__init__()
        self.name = 'Knife'
        self.bladecolor = pygame.Color('brown')
        self.handlecolor = pygame.Color('brown')

    def draw(self, game):
        pygame.draw.line(game.screen, self.bladecolor,
                         (self.x + 6, self.y - 6), (self.x + 20, self.y - 20), 3)
        pygame.draw.line(game.screen, self.handlecolor,
                         (self.x, self.y), (self.x + 5, self.y - 5), 3)


class Scythe(BaseMeleeWeapon):
    def __init__(self):
        super().__init__()
        self.name = 'Scythe'
        self.bladecolor = pygame.Color('brown')
        self.handlecolor = pygame.Color('brown')

    def draw(self, game):
        pygame.draw.line(game.screen, self.handlecolor,
                         (self.x, self.y), (self.x + 20, self.y - 20), 3)
        pygame.draw.line(game.screen, self.bladecolor, (self.x +
                         20, self.y - 20), (self.x + 13, self.y - 18), 3)


class Bow(BaseRangeWeapon):
    def __init__(self):
        super().__init__()
        self.name = 'Bow'
        self.bowcolor = pygame.Color('brown')
        self.stringcolor = pygame.Color('light grey')

    def draw(self, game):
        pygame.draw.lines(game.screen, self.bowcolor, False, [
                          (self.x - 5, self.y + 5), (self.x, self.y + 5), (self.x + 5, self.y), (self.x + 5, self.y - 5)], 2)
        pygame.draw.line(game.screen, self.stringcolor,
                         (self.x - 5, self.y + 5), (self.x + 5, self.y - 5))


class Crossbow(BaseRangeWeapon):
    def __init__(self):
        super().__init__()
        self.name = 'Crossbow'
        self.bowcolor = pygame.Color('brown')
        self.stringcolor = pygame.Color('light grey')
        self.arrow['damage'] = 3
        self.arrow['knockback'] = 15
        self.cooldown = 6

    def draw(self, game):
        pygame.draw.line(game.screen, self.bowcolor,
                         (self.x, self.y), (self.x - 10, self.y - 10), 2)
        pygame.draw.line(game.screen, self.bowcolor,
                         (self.x - 10, self.y), (self.x, self.y - 10), 2)
        pygame.draw.lines(game.screen, self.stringcolor, False, [
                          (self.x - 10, self.y), (self.x - 10, self.y - 5), (self.x - 5, self.y - 10), (self.x, self.y - 10)])


class WoodSword(Sword):
    def __init__(self):
        super().__init__()
        self.name = 'Wood Sword'
        self.knockback = 15
        self.cooldown = 9
        self.reach = 70
        self.num = 1
        self.damage = 3
        self.update_descript()


class StoneSword(Sword):
    def __init__(self):
        super().__init__()
        self.name = 'Stone Sword'
        self.knockback = 20
        self.cooldown = 9
        self.reach = 75
        self.num = 2
        self.damage = 4
        self.bladecolor = pygame.Color('dark grey')
        self.update_descript()


class IronSword(Sword):
    def __init__(self):
        super().__init__()
        self.name = 'Iron Sword'
        self.knockback = 20
        self.cooldown = 9
        self.reach = 80
        self.num = 3
        self.damage = 6
        self.bladecolor = pygame.Color('light grey')
        self.update_descript()


class GoldenSword(Sword):
    def __init__(self):
        super().__init__()
        self.name = 'Golden Sword'
        self.knockback = 13
        self.cooldown = 5
        self.reach = 70
        self.num = 2
        self.damage = 4
        self.bladecolor = pygame.Color('gold')
        self.update_descript()


class DiamondSword(Sword):
    def __init__(self):
        super().__init__()
        self.name = 'Diamond Sword'
        self.knockback = 24
        self.cooldown = 8
        self.reach = 80
        self.num = 3
        self.damage = 7
        self.bladecolor = pygame.Color('light blue')
        self._speed = 1
        self.update_descript()


class SpeedySword(Sword):
    def __init__(self):
        super().__init__()
        self.name = 'Speedy Sword'
        self.knockback = 20
        self.cooldown = 5
        self.reach = 80
        self.num = 5
        self.damage = 10
        self.bladecolor = pygame.Color('red')
        self._speed = 4
        self.update_descript()


class WoodAxe(Axe):
    def __init__(self):
        super().__init__()
        self.name = 'Wood Axe'
        self.knockback = 15
        self.cooldown = 13
        self.reach = 80
        self.num = 1
        self.damage = 5
        self.update_descript()


class IronAxe(Axe):
    def __init__(self):
        super().__init__()
        self.name = 'Iron Axe'
        self.knockback = 18
        self.cooldown = 12
        self.reach = 83
        self.num = 2
        self.damage = 7
        self.bladecolor = pygame.Color('grey')
        self.update_descript()


class GoldenAxe(Axe):
    def __init__(self):
        super().__init__()
        self.name = 'Golden Axe'
        self.knockback = 13
        self.cooldown = 10
        self.reach = 70
        self.num = 1
        self.damage = 5
        self.update_descript()
        self.bladecolor = pygame.Color('gold')


class WeightedAxe(Axe):
    def __init__(self):
        super().__init__()
        self.name = 'Weighted Axe'
        self.knockback = 50
        self.cooldown = 16
        self.reach = 80
        self.num = 8
        self.damage = 15
        self.bladecolor = pygame.Color('dark grey')
        self._speed = -1
        self.update_descript()


class CursedAxe(Axe):
    def __init__(self):
        super().__init__()
        self.name = 'Cursed Axe'
        self.knockback = 40
        self.cooldown = 10
        self.reach = 90
        self.num = 2
        self.damage = 5
        self.bladecolor = pygame.Color('grey')
        self.handlecolor = pygame.Color('purple')
        self.update_descript()

    def attack(self, enemy, player, damage, knockback):
        super().attack(enemy, player, damage, knockback)
        if enemy.effects['poison'] < 20:
            enemy.effects['poison'] = 20


class IronMallet(Mallet):
    def __init__(self):
        super().__init__()
        self.name = 'Iron Mallet'
        self.blockcolor = pygame.Color('grey')
        self.knockback = 25
        self.cooldown = 13
        self.reach = 80
        self.num = 2
        self.damage = 7
        self.update_descript()


class BigMallet(Mallet):
    def __init__(self):
        super().__init__()
        self.name = 'Big Mallet'
        self.blockcolor = pygame.Color('light blue')
        self.knockback = 28
        self.cooldown = 7
        self.reach = 130
        self.num = 10
        self.damage = 1
        self.update_descript()


class HerosMallet(Mallet):
    def __init__(self):
        super().__init__()
        self.name = 'Hero\'s Mallet'
        self.blockcolor = pygame.Color('dark blue')
        self.knockback = 27
        self.cooldown = 12
        self.reach = 87
        self.num = 3
        self.damage = 10
        self.update_descript()


class XPGatherer(Mallet):
    def __init__(self):
        super().__init__()
        self.name = 'XP Gatherer'
        self.blockcolor = pygame.Color('green')
        self.knockback = 20
        self.cooldown = 15
        self.reach = 80
        self.num = 1
        self.damage = 20
        self.update_descript()

    def attack(self, enemy, player, damage, knockback):
        super().attack(enemy, player, damage, knockback)
        player.get_xp(0.07)


class GravityHammer(Mallet):
    def __init__(self):
        super().__init__()
        self.name = 'Gravity Hammer'
        self.blockcolor = pygame.Color('purple')
        self.knockback = 50
        self.cooldown = 14
        self.reach = 90
        self.num = 7
        self.damage = 15
        self._speed = -1
        self.update_descript()


class KillFist(Fist):
    def __init__(self):
        super().__init__()
        self.name = 'Kill Fist'
        self.fistcolor = pygame.Color('black')
        self.knockback = 20
        self.cooldown = 5
        self.reach = 80
        self.num = 2
        self.damage = 1
        self._bonus = ['Relentless Combo']
        self.update_descript()


class SoulFists(Fist):
    def __init__(self):
        super().__init__()
        self.name = 'Soul Fists'
        self.fistcolor = pygame.Color('yellow')
        self.knockback = 30
        self.cooldown = 4
        self.reach = 90
        self.num = 1
        self.damage = 2
        self._kills = 2
        self._bonus = ['Relentless Combo']
        self.update_descript()

    def attack(self, enemy, player, damage, knockback):
        if random.randint(0, 3) == 0 and damage < 30:
            super().attack(enemy, player, 30, knockback)
        else:
            super().attack(enemy, player, damage, knockback)


class GaleKnife(Knife):
    def __init__(self):
        super().__init__()
        self.name = 'Gale Knife'
        self.bladecolor = pygame.Color('light blue')
        self.knockback = 20
        self.cooldown = 9
        self.reach = 80
        self.num = 1
        self.damage = 4
        self.update_descript()

    def attack(self, enemy, player, damage, knockback):
        super().attack(enemy, player, damage, knockback)

        if enemy.hp <= 0:
            if player.effects['speed'] < 15:
                player.effects['speed'] = 15


class TempestKnife(Knife):
    def __init__(self):
        super().__init__()
        self.name = 'Resolute Tempest Knife'
        self.bladecolor = pygame.Color('light blue')
        self.knockback = 20
        self.cooldown = 9
        self.reach = 70
        self.num = 2
        self.damage = 5
        self.update_descript()

    def attack(self, enemy, player, damage, knockback):
        if enemy.hp < enemy.hpmax:
            enemy.take_damage(2)

        super().attack(enemy, player, damage, knockback)


class FangsOfFrost(Knife):
    def __init__(self):
        super().__init__()
        self.name = 'Fangs of Frost'
        self.bladecolor = pygame.Color('light blue')
        self.knockback = 10
        self.cooldown = 5
        self.reach = 60
        self.num = 1
        self.damage = 5
        self.update_descript()

    def attack(self, enemy, player, damage, knockback):
        super().attack(enemy, player, damage, knockback)
        enemy.give_unmoving(10)


class DarkKatana(Knife):
    def __init__(self):
        super().__init__()
        self.name = 'Dark Katana'
        self.bladecolor = pygame.Color('purple')
        self.handlecolor = pygame.Color('black')
        self.knockback = 10
        self.cooldown = 6
        self.reach = 60
        self.num = 1
        self.damage = 20
        self._speed = 1
        self.update_descript()


class EternalKnife(Knife):
    def __init__(self):
        super().__init__()
        self.name = 'Eternal Knife'
        self.bladecolor = pygame.Color('purple')
        self.handlecolor = pygame.Color('black')
        self.knockback = 20
        self.cooldown = 5
        self.reach = 80
        self.num = 2
        self.damage = 10
        self._kills = 2
        self.update_descript()


class JailorScythe(Scythe):
    def __init__(self):
        super().__init__()
        self.name = 'Jailor\'s Scythe'
        self.bladecolor = pygame.Color('white')
        self.handlecolor = pygame.Color('purple')
        self.knockback = 10
        self.cooldown = 6
        self.reach = 100
        self.num = 2
        self.damage = 6
        self.update_descript()

    def attack(self, enemy, player, damage, knockback):
        super().attack(enemy, player, damage, knockback)
        if enemy.effects['slowness'] < 120:
            enemy.effects['slowness'] = 120


class GraveBane(Scythe):
    def __init__(self):
        super().__init__()
        self.name = 'Grave Bane'
        self.bladecolor = pygame.Color('yellow')
        self.handlecolor = pygame.Color('yellow')
        self.knockback = 50
        self.cooldown = 5
        self.reach = 120
        self.num = 3
        self.damage = 18
        self.update_descript()


class PurpleStorm(Bow):
    def __init__(self):
        super().__init__()
        self.name = 'Purple Storm'
        self.bowcolor = pygame.Color('purple')
        self.cooldown = 1
        self.arrow['damage'] = 3
        self.update_descript()


class InfinityBow(Bow):
    def __init__(self):
        super().__init__()
        self.name = 'Infinity Bow'
        self.bowcolor = pygame.Color('black')
        self._bonus.append('Infinity')
        self.update_descript()


class FlameBow(Bow):
    def __init__(self):
        super().__init__()
        self.name = 'Flame Bow'
        self.bowcolor = pygame.Color('red')
        self.stringcolor = pygame.Color('red')
        self.cooldown = 4
        self.arrow['type'] = dungeon_arrows.FlamingArrow
        self.arrow['name'] = 'Flaming Arrow'
        self.update_descript()


class PoisonBow(Bow):
    def __init__(self):
        super().__init__()
        self.name = 'Poison Bow'
        self.bowcolor = pygame.Color('green')
        self.arrow['type'] = dungeon_arrows.PoisonArrow
        self.arrow['knockback'] = 25
        self.arrow['name'] = 'Poison Arrow'
        self.update_descript()


class Sabrewing(Bow):
    def __init__(self):
        super().__init__()
        self.name = 'Sabrewing'
        self.stringcolor = pygame.Color('light grey')
        self.bowcolor = pygame.Color('gold')
        self.cooldown = 8
        self.update_descript()

    def shoot(self, game, player, t):
        super().shoot(game, player, t)
        if game.player.effects['regeneration'] < 10:
            game.player.effects['regeneration'] = 10


class Longbow(Bow):
    def __init__(self):
        super().__init__()
        self.name = 'Longbow'
        self.arrow['damage'] = 4
        self.arrow['knockback'] = 30
        self.update_descript()


class BurstGaleBow(Bow):
    def __init__(self):
        super().__init__()
        self.name = 'Burst Gale Bow'
        self.arrow['type'] = dungeon_arrows.SpeedWhenHurtArrow
        self.update_descript()


class SlowCrossbow(Crossbow):
    def __init__(self):
        super().__init__()
        self.name = 'Slow Crossbow'
        self.bowcolor = pygame.Color('dark grey')
        self.cooldown = 7
        self.arrow['type'] = dungeon_arrows.SlowArrow
        self.arrow['name'] = 'Slow Arrow'
        self.update_descript()


class ExplodingCrossbow(Crossbow):
    def __init__(self):
        super().__init__()
        self.name = 'Exploding Crossbow'
        self.bowcolor = pygame.Color('white')
        self.cooldown = 8
        self.arrow['type'] = dungeon_arrows.ExplodingArrow
        self.arrow['name'] = 'Exploding Arrow'
        self.update_descript()


class ChainCrossbow(Crossbow):
    def __init__(self):
        super().__init__()
        self.name = 'Chain Crossbow'
        self.bowcolor = pygame.Color('gray')
        self.cooldown = 6
        self._bonus.append('Chain Reaction')
        self.update_descript()


class ImplodingCrossbow(Crossbow):
    def __init__(self):
        super().__init__()
        self.name = 'Imploding Crossbow'
        self.bowcolor = pygame.Color('red')
        self.cooldown = 7
        self.arrow['type'] = dungeon_arrows.ImplodingArrow
        self.arrow['name'] = 'Imploding Arrow'
        self.update_descript()


class HeavyCrossbow(Crossbow):
    def __init__(self):
        super().__init__()
        self.name = 'Heavy Crossbow'
        self.cooldown = 10
        self.arrow['damage'] = 10
        self.arrow['knockback'] = 50
        self._speed = -1
        self.update_descript()


class Voidcaller(Crossbow):
    def __init__(self):
        super().__init__()
        self.name = 'Voidcaller'
        self.cooldown = 7
        self.arrow['damage'] = 7
        self._kills = 2
        self.update_descript()


class ButterflyCrossbow(Crossbow):
    def __init__(self):
        super().__init__()
        self.name = 'Butterfly Crossbow'
        self.cooldown = 3
        self.arrow['damage'] = 4
        self._speed = 1
        self.update_descript()


class HarpCrossbow(Crossbow):
    def __init__(self):
        super().__init__()
        self.name = 'Harp Crossbow'
        self.cooldown = 2
        self.bowcolor = pygame.Color('gold')
        self.arrow['knockback'] = 20
        self.arrow['damage'] = 6
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
    def __init__(self):
        super().__init__()
        self.name = 'Leather Armor'
        self.protect = 0.5
        self.color = pygame.Color('brown')
        self.update_descript()


class ChainArmor(BaseArmor):
    def __init__(self):
        super().__init__()
        self.name = 'Chain Armor'
        self.protect = 1.5
        self.color = pygame.Color('light grey')
        self.update_descript()


class ReinforcedMail(BaseArmor):
    def __init__(self):
        super().__init__()
        self.name = 'Reinforced Mail'
        self.protect = 2
        self.color = pygame.Color('grey')
        self._speed = -1
        self.update_descript()


class HunterArmor(BaseArmor):
    def __init__(self):
        super().__init__()
        self.name = 'Hunter\'s Armor'
        self.protect = 3
        self.color = pygame.Color('tan')
        self.update_descript()


class HeroArmor(BaseArmor):
    def __init__(self):
        super().__init__()
        self.name = 'Hero\'s Armor'
        self.protect = 3
        self.color = pygame.Color('yellow')
        self.update_descript()

    def render(self, x, y, game):
        super().render(x, y, game)
        if game.player.effects['regeneration'] < 3:
            game.player.effects['regeneration'] = 3


class SoulRobe(BaseArmor):
    def __init__(self):
        super().__init__()
        self.name = 'Soul Robe'
        self.protect = 1
        self.color = pygame.Color('dark grey')
        self._kills = 1
        self.update_descript()


class SplendidRobe(BaseArmor):
    def __init__(self):
        super().__init__()
        self.name = 'Splendid Robe'
        self.protect = 2
        self.color = pygame.Color('purple')
        self.update_descript()

    def render(self, x, y, game):
        super().render(x, y, game)
        if game.player.effects['strength'] < 3:
            game.player.effects['strength'] = 3


class MysteryArmor(BaseArmor):
    def __init__(self):
        super().__init__()
        self.name = 'Mystery Armor'
        self.protect = 2
        self.color = pygame.Color('light grey')
        self.update_descript()

    def render(self, x, y, game):
        super().render(x, y, game)
        if game.player.range:
            game.player.range._is_increased = 1

    def do_special(self, player, enemy, game):
        if random.randint(0, 10) == 0:
            player.rect.x = random.randint(0, game.screen.get_width())
            player.rect.y = random.randint(0, game.screen.get_height())


class SpelunkerArmor(BaseArmor):
    def __init__(self):
        super().__init__()
        self.name = 'Spelunker Armor'
        self.protect = 2
        self.color = pygame.Color('orange')
        self._bat = None
        self.update_descript()

    def equip(self, game):
        self._bat = dungeon_helpful.Bat(game.player.rect.x, game.player.rect.y)
        game.helpfuls.append(self._bat)

    def remove(self, game):
        self._bat._nowdie = True


class FoxArmor(BaseArmor):
    def __init__(self):
        super().__init__()
        self.name = 'Fox Armor'
        self.protect = 10
        self.color = pygame.Color('orange')
        self.update_descript()

    def _protect(self):
        if random.randint(1, 10) == 1:
            return 1000000
        return int(round(self.protect + random.choice([-0.5, -0.4, -0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5])))


class FrostBite(BaseArmor):
    def __init__(self):
        super().__init__()
        self.name = 'Frost Bite'
        self.protect = 3
        self.color = pygame.Color('light blue')
        self.update_descript()

    def render(self, x, y, game):
        super().render(x, y, game)
        if game.player.range and game.player.range._is_increased < 2:
            game.player.range._is_increased = 2


class MetalArmor(BaseArmor):
    def __init__(self):
        super().__init__()
        self.name = 'Full Metal Armor'
        self.protect = 5
        self.color = pygame.Color('grey')
        self._speed = -1
        self.update_descript()


class SpiderArmor(BaseArmor):
    def __init__(self):
        super().__init__()
        self.name = 'Spider Armor'
        self.protect = 3
        self.color = pygame.Color('black')
        self._speed = 1
        self.update_descript()


class MercenaryArmor(BaseArmor):
    def __init__(self):
        super().__init__()
        self.name = 'Mercenary Armor'
        self.protect = 2
        self.color = pygame.Color('red')
        self.update_descript()


class DeathCapMushroom(Artifact):
    def __init__(self):
        super().__init__()
        self.name = 'Death Cap Mushroom'
        self.maxcooldown = 20
        self.pow = 4

    def draw(self, game):
        super().draw(game)
        pygame.draw.rect(game.screen, pygame.Color('tan'),
                         pygame.Rect(self.x + 12, self.y + 20, 6, 13))
        pygame.draw.circle(game.screen, pygame.Color(
            'purple'), (self.x + 15, self.y + 15), 8)

    def use(self, game):
        if super().use(game):
            if game.player.effects['strength'] < 10:
                game.player.effects['strength'] = 10
            if game.player.effects['speed'] < 10:
                game.player.effects['speed'] = 10
            if game.player.effects['resistance'] < 10:
                game.player.effects['resistance'] = 10


class FlameQuiver(Artifact):
    def __init__(self):
        super().__init__()
        self.name = 'Flame Quiver'
        self.maxcooldown = 4
        self.pow = 6

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
    def __init__(self):
        super().__init__()
        self.name = 'Exploding Quiver'
        self.maxcooldown = 3
        self._arrow = dungeon_arrows.ExplodingArrow
        self.pow = 5

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
    def __init__(self):
        super().__init__()
        self.name = 'Corrupted Beacon'
        self.maxcooldown = 3
        self.pow = 10
        self.using = False
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
                                    enemy.take_damage(3)
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
                                    enemy.take_damage(3)
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
                                    enemy.take_damage(3)
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
                                    enemy.take_damage(3)
                                    did = True
                game.player.kills -= 1
            self.cooldown = self.maxcooldown


class LightningRod(Artifact):
    def __init__(self):
        super().__init__()
        self.name = 'Lightning Rod'
        self.maxcooldown = 5
        self.pow = 7
        self._needed = 5
        self._enemies = []

    def draw(self, game):
        super().draw(game)
        pygame.draw.line(game.screen, pygame.Color('yellow'),
                         (self.x, self.y + 20), (self.x + 20, self.y), 2)
        pygame.draw.rect(game.screen, pygame.Color('white'),
                         pygame.Rect(self.x - 1, self.y + 19, 2, 2))

    def _draw(self, game):
        for enemy in self._enemies:
            pygame.draw.line(game.screen, pygame.Color('yellow'), (enemy.rect.x + 15, enemy.rect.y + 20),
                             (enemy.rect.x + 15 + random.randint(-10, 10), enemy.rect.y - random.randint(250, 300)))

    def use(self, game):
        if super().use(game):
            for enemy in game.enemies:
                if math.sqrt(pow(game.player.rect.x - enemy.rect.x, 2) + pow(game.player.rect.y - enemy.rect.y, 2)) < 100:
                    self._enemies.append(enemy)
                    pygame.draw.line(game.screen, pygame.Color('yellow'), (enemy.rect.x + 15, enemy.rect.y + 20),
                                     (enemy.rect.x + 15 + random.randint(-10, 10), enemy.rect.y - random.randint(250, 300)))
            pygame.display.update()

            self.wait(game, 2)
            for enemy in self._enemies:
                enemy.take_damage(15)
                if enemy.effects['fire'] < 10:
                    enemy.effects['fire'] = 10
            self._enemies.clear()


class GongWeakening(Artifact):
    def __init__(self):
        super().__init__()
        self.name = 'Gong of Weakening'
        self.maxcooldown = 20
        self.pow = 8
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
                    if enemy.effects['weakness'] < 20:
                        enemy.effects['weakness'] = 20
                    if enemy.effects['poison'] < 10:
                        enemy.effects['poison'] = 10


class ShockPowder(Artifact):
    def __init__(self):
        super().__init__()
        self.name = 'Shock Powder'
        self.maxcooldown = 10
        self.pow = 4
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
                if distance_to(game.player, enemy) < 400:
                    enemy.take_damage(10)
                    enemy.knockback(50, game.player)
                    if game.player.effects['speed'] < 35:
                        game.player.effects['speed'] += 5


class TotemRegeneration(Artifact):
    def __init__(self):
        super().__init__()
        self.name = 'Totem of Regeneration'
        self.maxcooldown = 10
        self.pow = 3
        # self._needed = 3

    def draw(self, game):
        super().draw(game)
        pygame.draw.rect(game.screen, pygame.Color('brown'),
                         pygame.Rect(self.x + 5, self.y + 5, 10, 15))
        pygame.draw.circle(game.screen, pygame.Color(
            'red'), (self.x + 10, self.y + 12), 5)

    def use(self, game):
        if super().use(game):
            if game.player.effects['regeneration'] < 20:
                game.player.effects['regeneration'] = 20


class BootsOfSwiftness(Artifact):
    def __init__(self):
        super().__init__()
        self.name = 'Boots of Swiftness'
        self.maxcooldown = 10
        self.pow = 3
        # self._needed = 4

    def draw(self, game):
        super().draw(game)
        pygame.draw.rect(game.screen, pygame.Color('blue'),
                         pygame.Rect(self.x, self.y, 5, 10))
        pygame.draw.rect(game.screen, pygame.Color('blue'),
                         pygame.Rect(self.x + 10, self.y, 5, 10))

    def use(self, game):
        if super().use(game):
            if game.player.effects['speed'] < 7:
                game.player.effects['speed'] = 7


class TotemOfShielding(Artifact):
    def __init__(self):
        super().__init__()
        self.name = 'Totem of Shielding'
        self.maxcooldown = 15
        self.pow = 2
        # self._needed = 10

    def draw(self, game):
        super().draw(game)
        pygame.draw.rect(game.screen, pygame.Color('blue'),
                         pygame.Rect(self.x + 5, self.y + 5, 10, 15))

    def use(self, game):
        if super().use(game):
            if game.player.effects['resistance'] < 10:
                game.player.effects['resistance'] = 10
            game.player.hp += 10


class SoulHealer(Artifact):
    def __init__(self):
        super().__init__()
        self.name = 'Soul Healer'
        self.maxcooldown = 10
        self.pow = 5
        self._needed = 5

    def draw(self, game):
        super().draw(game)
        pygame.draw.rect(game.screen, pygame.Color('purple'),
                         pygame.Rect(self.x + 5, self.y + 5, 15, 15))

    def use(self, game):
        if super().use(game):
            for i in range(random.randint(5, 20)):
                game.player.hp += random.randint(0, 3)


class Harvester(Artifact):
    def __init__(self):
        super().__init__()
        self.name = 'Harvester'
        self.maxcooldown = 10
        self.pow = 8
        self._needed = 7
        self._enemies = []

    def draw(self, game):
        super().draw(game)
        pygame.draw.rect(game.screen, pygame.Color('blue'),
                         pygame.Rect(self.x + 5, self.y + 5, 10, 15))
        pygame.draw.rect(game.screen, pygame.Color('light blue'),
                         pygame.Rect(self.x + 7, self.y + 7, 6, 11))

    def _draw(self, game):
        for enemy in self._enemies:
            pygame.draw.line(game.screen, pygame.Color(
                'light blue'), (game.player.rect.x, game.player.rect.y), (enemy.rect.x, enemy.rect.y))

    def use(self, game):
        if super().use(game):
            for enemy in game.enemies:
                if distance_to(game.player, enemy) < 150:
                    self._enemies.append(enemy)
            for enemy in self._enemies:
                if game.player.kills <= 1:
                    continue
                game.player.kills -= 2
                pygame.draw.line(game.screen, pygame.Color(
                    'light blue'), (game.player.rect.x, game.player.rect.y), (enemy.rect.x, enemy.rect.y))
            pygame.display.update()
            self.wait(game, 2)
            for enemy in self._enemies:
                enemy.take_damage(30)
                enemy.knockback(50, game.player)
                game.player.kills += 2
            self._enemies.clear()


class LightFeather(Artifact):
    def __init__(self):
        super().__init__()
        self.name = 'Light Feather'
        self.maxcooldown = 5
        self.pow = 7
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

    def _draw(self, game):
        for enemy in self._enemies:
            pygame.draw.circle(game.screen, pygame.Color(
                'white'), (enemy.rect.x, enemy.rect.y), 20)

    def use(self, game):
        if super().use(game):
            count = 0
            for enemy in game.enemies:
                if distance_to(game.player, enemy) < 150 and count < 5:
                    self._enemies.append(enemy)
                    count += 1
            for enemy in self._enemies:
                pygame.draw.circle(game.screen, pygame.Color(
                    'white'), (enemy.rect.x, enemy.rect.y), 20)
            pygame.display.update()
            self.wait(game, 3)
            for enemy in self._enemies:
                enemy.take_damage(5)
                enemy.knockback(10, game.player)
                if enemy.effects['slowness'] < 3:
                    enemy.effects['slowness'] = 3
            self._enemies.clear()


class IronHideAmulet(Artifact):
    def __init__(self):
        super().__init__()
        self.name = 'Iron Hide Amulet'
        self.maxcooldown = 15
        self.pow = 4
        # self._needed = 2

    def draw(self, game):
        super().draw(game)
        pygame.draw.rect(game.screen, pygame.Color('dark grey'),
                         pygame.Rect(self.x + 5, self.y + 5, 15, 15))
        pygame.draw.rect(game.screen, pygame.Color('green'),
                         pygame.Rect(self.x + 7, self.y + 7, 11, 11))

    def use(self, game):
        if super().use(game):
            if game.player.effects['resistance'] < 10:
                game.player.effects['resistance'] = 10


class WindHorn(Artifact):
    def __init__(self):
        super().__init__()
        self.name = 'Wind Horn'
        self.maxcooldown = 5
        self.pow = 6
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
                if distance_to(game.player, enemy) < 150:
                    to.append(enemy)
            for enemy in to:
                enemy.take_damage(5)
                enemy.knockback(30, game.player)
                if enemy.effects['slowness'] < 30:
                    enemy.effects['slowness'] = 30
                if enemy.effects['weakness'] < 30:
                    enemy.effects['weakness'] = 30


class GolemKit(Artifact):
    def __init__(self):
        super().__init__()
        self.name = 'Golem Kit'
        self.maxcooldown = 1
        self.pow = 15
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
            self._golem = dungeon_helpful.Golem(game.player.rect.x, game.player.rect.y)
            game.helpfuls.append(self._golem)
            self._ready = False


class TastyBone(Artifact):
    def __init__(self):
        super().__init__()
        self.name = 'Tasty Bone'
        self.maxcooldown = 1
        self.pow = 13
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
                game.player.rect.x, game.player.rect.y)
            game.helpfuls.append(self._wolf)
            self._ready = False


wloot = {'common': [Bow(), Crossbow(), SlowCrossbow(), BigMallet(), WoodSword(), WoodAxe(), GoldenSword(), GoldenAxe(), StoneSword(), IronSword(), IronAxe(), Longbow()], 'uncommon': [IronMallet(), ImplodingCrossbow(), ExplodingCrossbow(), ChainCrossbow(), BurstGaleBow(), GaleKnife(), KillFist(), DiamondSword(), HarpCrossbow(), ButterflyCrossbow(
), HeavyCrossbow(), Sabrewing()], 'rare': [WeightedAxe(), DarkKatana(), TempestKnife(), CursedAxe(), FangsOfFrost(), FlameBow(), PoisonBow()], 'epic': [EternalKnife(), Voidcaller(), GravityHammer(), SoulFists(), JailorScythe(), HerosMallet(), SpeedySword(), InfinityBow()], 'legendary': [XPGatherer(), PurpleStorm(), GraveBane()]}

cloot = [TNT(), Apple(), Bread(), Pork(), StrengthPotion(), SwiftnessPotion(), ShadowBrew(), CookedSalmon(
), SweetBrew(), '15 arrows', '25 arrows', '35 arrows', '5 arrows', '10 arrows', '20 arrows', '30 arrows']

arloot = {'common': [LeatherArmor(), ReinforcedMail(), ChainArmor(), SpiderArmor()], 'uncommon': [MercenaryArmor(), HunterArmor(
), HeroArmor(), MetalArmor(), FrostBite(), MysteryArmor()], 'rare': [SpelunkerArmor(), SplendidRobe(), SoulRobe(), HeroArmor(), FoxArmor()]}

aloot = [TastyBone(), GolemKit(), WindHorn(), IronHideAmulet(), LightFeather(), Harvester(), SoulHealer(), TotemOfShielding(), DeathCapMushroom(
), FlameQuiver(), ExplodingQuiver(), Beacon(), GongWeakening(), LightningRod(), ShockPowder(), TotemRegeneration(), BootsOfSwiftness()]

sloot = arloot['rare'] + arloot['common'] + arloot['uncommon'] + cloot + aloot

everything = [i() for i in BaseArmor.__subclasses__()] + [i() for i in Artifact.__subclasses__()] + [i() for i in Consumable.__subclasses__()] + [i() for i in Bow.__subclasses__()] + [i() for i in Crossbow.__subclasses__()] + [i()
                                                                                                                                                                                                                                   for i in Sword.__subclasses__()] + [i() for i in Axe.__subclasses__()] + [i() for i in Knife.__subclasses__()] + [i() for i in Scythe.__subclasses__()] + [i() for i in Fist.__subclasses__()] + [i() for i in Mallet.__subclasses__()]
