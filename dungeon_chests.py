import pygame
import dungeon_weapons
import dungeon_settings
import random

UPGRADES = ([-1] * 10 +
            [0] * 30 +
            [1] * 5)


class Chest:
    color = pygame.Color('brown')  # central color
    outlinecolor = pygame.Color('brown')  # outline color

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 35)
        self.emeralds = None  # how many emeralds this chest drops

    def render(self, game):
        if pygame.sprite.collide_rect(game.player, self):
            game.chests.remove(self)
            self.rect.x = 10000
            self.rect.y = 10000
            loot = self.gen_loot(game.player)
            if loot == None: return
            loot2 = []
            for i in loot:
                try:loot2.append(i(max(game.player.power + random.choice(UPGRADES), 1)))
                except TypeError:loot2.append(i)
            game.player.getloot(loot2, self.emeralds, game)
            dungeon_settings.chest_loot.play()  # play the chest looting sound
        self.draw(game)  # draw chest

    def draw(self, game):
        pygame.draw.rect(game.screen, self.outlinecolor,
                         pygame.Rect(self.rect.x - 1, self.rect.y - 1, 52, 37))
        pygame.draw.rect(game.screen, self.color, self.rect)

    def gen_loot(self, player):
        return self.loot  # get loot (can get overwritten)


class PlayerLootChest:
    def __init__(self, x, y, player=None):
        self.rect = pygame.Rect(x, y, 100, 70)
        self.color = pygame.Color('brown')
        if player:
            self.data = {'w': player.weapons[1:],
                         'r': player.ranges[1:],
                         'a': player.artifacts[1:],
                         'c': player.consumables[1:],
                         'ar': player.armors[1:]}
        else:
            self.data = {'w': [], 'r': [], 'a': [], 'c': [], 'ar': []}

    def render(self, game):
        if pygame.sprite.collide_rect(game.player, self):
            p = game.player
            p.weapons += self.data['w']
            p.ranges += self.data['r']
            p.artifacts += self.data['a']
            p.consumables += self.data['c']
            p.armors += self.data['ar']
            dungeon_settings.chest_loot.play()
            self.rect.x = self.rect.y = 10000
            game.chests.remove(self)
        self.draw(game)

    def draw(self, game):
        pygame.draw.rect(game.screen, self.color, self.rect)


class WeaponChest(Chest):
    outlinecolor = pygame.Color('white')

    def gen_loot(self, player):
        return [random.choice(dungeon_weapons.wloot)]


class ConsumableChest(Chest):
    outlinecolor = pygame.Color('yellow')

    def gen_loot(self, player):
        return [random.choice(dungeon_weapons.cloot)
                for i in range(random.randint(2, 5))]  # get some consumables


class InventoryChest(Chest):
    outlinecolor = pygame.Color('black')

    def gen_loot(self, player):
        return [random.choice(['10 arrows', '15 arrows', '20 arrows']),
                dungeon_weapons.Bread()]  # bread and arrows lol


class EmeraldChest(Chest):
    outlinecolor = pygame.Color('green')

    def __init__(self, x, y):
        super().__init__(x, y)
        self.emeralds = (13, 26)
        self.loot = 'emerald'  # just gives emeralds


class ObsidianChest(Chest):
    color = pygame.Color('black')
    outlinecolor = pygame.Color('light blue')

    def gen_loot(self, player):
        return [random.choice(dungeon_weapons.aloot)
                for i in range(random.randint(1, 2))]  # get 1 or 2 artifacts


class SupplyChest(Chest):
    outlinecolor = pygame.Color('blue')

    def gen_loot(self, player):
        return [random.choice(dungeon_weapons.cloot)
                for i in range(random.randint(1, 3))] + \
                ['emerald' for i in range(random.choice([0, 2]))]

    def __init__(self, x, y):
        super().__init__(x, y)
        self.emeralds = (7, 14)


class SilverChest(Chest):
    outlinecolor = pygame.Color('light grey')

    def __init__(self, x, y):
        super().__init__(x, y)
        self.loot = [random.choice(dungeon_weapons.sloot)
                     for i in range(random.randint(2, 4))]


class ArmorChest(Chest):
    outlinecolor = pygame.Color('red')

    def gen_loot(self, player):
        return [random.choice(dungeon_weapons.arloot)]
