import os
import sys
if os.path.dirname(__file__) not in sys.path:
    sys.path.insert(0, os.path.dirname(__file__))
if os.path.join(os.path.dirname(__file__), 'loader') not in sys.path:
    # just in case we try to run the game from this code, make sure sys.path is set up correctly
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'loader'))

if __name__ == '__main__':
    # dungeon_settings breaks if not initialized first
    import dungeon_settings
    dungeon_settings.load(dungeon_settings.BASEPATH)
from dungeon_settings import FONT_PATH, BASEPATH  # need the fonts
import dungeon_logger as logger
import pygame

__version__ = '1.5.3'

if True:  # not dungeon_settings.DO_FULL_SCREEN:
    # resizable window, but not full screen
    screen = pygame.display.set_mode((1000, 700), pygame.RESIZABLE)
# elif dungeon_settings.DO_FULL_SCREEN:
    # screen = pygame.display.set_mode((1470, 770), pygame.FULLSCREEN) #full screen window! (disable while testing, as crashes with fullscreen window are horrible

pygame.display.set_caption('PyDungeons ' + __version__)  # set the caption

pygame.init()  # why is pygame.init() after the rest of this...? It should be before the pygame.display calls... TODO: move it up

screen_color = pygame.Color('dark green')  # background color

logger.init()
logger.info('PyDungeons ' + __version__ + ' loading!')  # loading game

screen.fill(screen_color)
screen.blit(pygame.font.Font(FONT_PATH, 100).render('Loading...', 1, pygame.Color(
    'black')), (100, 100))  # loading screen while imports are loading
pygame.display.update()

import itertools
import traceback
import datetime
from pygame._sdl2 import messagebox
import time
import dungeon_text_input
import random
import logging
import dungeon_saving as saving
import threading
import dungeon_parser
import dungeon_server as dungeons_server
import dungeon_gui as dungeons_gui
import dungeon_misc
import dungeon_helpful
import dungeon_modloader
import dungeon_walls
import dungeon_weapons
import dungeon_chests
import dungeon_enemies
import dungeon_settings
import dungeon_player

spx = 100
spy = 100

handler = dungeons_gui.ScreenHandler(screen)  # make a handler so we don't have to pass it as an arg
dungeon_settings.start()  # start the music
dungeon_settings.initcursor()  # initialize the cursor

PATH = dungeon_settings.FONT_PATH  # keep a shorter version of the font path

stop_credits = False
stop_options = False
stop_controls = False
stop_menu = False  # stuff to help with the menus

button_save = None  # for old options screens
button_save2 = None


def dif(dif):
    if dif == 'Default':
        return 1
    elif dif == 'Adventure':
        return 2
    elif dif == 'Apocalypse':
        return 3
    else:
        logger.error(f'Difficulty {dif} does not exist.')
        return None


# dictionary of chest names -> chest types
chests = {'inventory': dungeon_chests.InventoryChest, 'armor': dungeon_chests.ArmorChest, 'silver': dungeon_chests.SilverChest, 'blue': dungeon_chests.SupplyChest,
          'norm': dungeon_chests.WeaponChest, 'gold': dungeon_chests.ConsumableChest, 'emerald': dungeon_chests.EmeraldChest, 'obsidian': dungeon_chests.ObsidianChest}


# Finally doesn't use Tkinter anymore!
def text__input(title, prompt):
    # name = input('NAME>')
    return dungeon_text_input.gettextinput((200, 100), screen, fillcolor=screen_color, accepttext='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -_+', fontsize=50, other_text='World Name: ', doupdate=True)


def textinput(game, prompt):  # text input using dungeon_text_input
    return dungeon_text_input.gettextinput((10, game.screen.get_height() - 30), game.screen, whilerunfunc=(game.update_while_chat, ()), other_text=prompt, fillcolor=game.screen_color, doupdate=False, passtext=True)


def stop_play(*args):  # function to quit the game with exit code 0
    logger.info('Window has closed.')
    logger.info('Stopping!')
    logger.stop()
    pygame.quit()
    sys.exit(0)


class Game:
    # the game object that is created when a world is loaded
    def __init__(self, spx, spy, using_save, name='New World', filename='New World'):
        # chest loot pool
        self.chests_pool = ['inventory', 'inventory', 'inventory', 'inventory', 'inventory', 'obsidian', 'armor', 'armor', 'armor', 'armor', 'silver', 'silver', 'blue', 'blue', 'norm', 'norm', 'norm', 'norm', 'norm', 'norm',
                            'norm', 'gold', 'gold', 'gold', 'gold', 'emerald', 'emerald', 'blue', 'gold', 'emerald', 'norm', 'norm', 'obsidian', 'obsidian', 'obsidian', 'emerald', 'obsidian', 'emerald', 'gold', 'gold', 'norm', 'norm', 'norm']
        self.player = dungeon_player.Player(spx, spy, dif(
            dungeon_settings.DIFFICULTY))  # make the player
        self.pname = 'Player'  # player name TODO: make an option to change this
        if dungeon_settings.USE_MODS:  # MODS ARE BROKE! NEVER SET USE_MODS TO TRUE UNTIL THEY ARE FIXED!
            self.saving = dungeon_modloader.initmods(
                self, {'chests': chests, 'chests_pool': self.chests_pool, 'saving': saving})
        else:
            self.saving = saving  # use this anyway
        self.name, self.filename = name, filename  # keep track of the name of the world
        self.enemies = []
        self.screen = screen
        self.moving = {'up': 0, 'down': 0, 'left': 0,
                       'right': 0}  # which directions we are moving
        self.enemy_delay = 0
        self.chest_delay = 0
        self.chests = []
        self.arrows = []
        self.walls = []
        self.helpfuls = []
        self.other = []
        self.spawners = []
        self.pending_messages = []  # chat messages currently being displayed
        self.pending_timer = time.time()
        self.hasquit = False
        self.button_resume = self.button_quit = None
        self.savedelay = time.time()
        self.version = __version__
        self.screen_color = screen_color
        self.difficulty = dungeon_settings.DIFFICULTY
        if dungeon_settings.RUN_PDPY_SERVER:
            self.pdpyserv = dungeons_server.PDPYServer(
                28135, self)  # create the PDPY server
        if dungeon_settings.RUN_PDPY_SERVER:
            threading.Thread(target=self.pdpyserv.run,
                             daemon=True).start()  # run the PDPY server
        if not using_save:  # new world? make stuff for the difficulty
            if self.dif == 1:
                self.add_enemy()
                self.spawn_chest()
                self.spawn_chest()
            elif self.dif == 2:
                self.add_enemy()
                self.spawn_chest()
            elif self.dif == 3:
                self.add_enemy()
                self.add_enemy()
                self.spawn_chest()
            # self.walls = dungeon_walls.genwalls() # dont work
        self.get_all = lambda: self.spawners + self.enemies + self.chests + self.arrows + \
            self.walls + self.helpfuls + \
            self.other  # function to get all objects that are non-player

    @property
    def dif(self):
        return dif(self.difficulty)

    # function that runs while chat is being entered
    def update_while_chat(self, events, text, pos):
        if self.hasquit:  # don't update if game is quit
            return
        if (time.time() - self.savedelay) >= (60 * dungeon_settings.MINUTES_PER_SAVE):  # save the world
            saving.save_world(self, self.name, self.filename)
            self.message(f'World saved at {time.time()}.')
            logger.info(f'World saved at {time.time()}.')
            self.savedelay = time.time()
        # self.screen.fill(self.screen_color)

        self.enemy_delay += 1  # spawn enemies
        if self.enemy_delay > 1000 + random.randint(-20, 20) - (self.player.difficulty * 7) - ((1-self.dif) * 5):
            self.add_enemy()
            self.enemy_delay = 0

        self.chest_delay += 1  # spawn chests
        if self.chest_delay > 600 + random.randint(-20, 20) - ((self.player.difficulty * 7) // 2) - ((1-self.dif) * 5):
            self.spawn_chest()
            self.chest_delay = 0

        for event in events:  # take screenshots
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F2:
                name = 'screenshot_' + str(datetime.datetime.now()).replace(
                    '/', '_').replace(':', '_').replace('-', '_').replace('.', '_') + '.png'
                pygame.image.save(screen, os.path.join(
                    BASEPATH, 'screenshots', name))
                self.message('Screenshot saved as ' + name)

        self.screen.blit(text, pos)  # draw the pending chat text

        self.objects_render()  # draw every object (player, enemies, etc.) + cooldowns

    def play(self, func=None):  # a tick of the game
        if self.hasquit:  # don't play if game has quit!
            return
        if (time.time() - self.savedelay) >= (60 * dungeon_settings.MINUTES_PER_SAVE):  # autosave world
            saving.save_world(self, self.name, self.filename)
            self.message(f'World saved at {time.time()}.')
            logger.info(f'World saved at {time.time()}.')
            self.savedelay = time.time()
        do_quit = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()  # quit game
                do_quit = False
                logger.info('Window has closed.')
                logger.info('Stopping!')
                logger.stop()
                sys.exit(0)
            # a lot of keybinds (functions are explained in player module)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.moving['left'] = 1
                if event.key == pygame.K_d:
                    self.moving['right'] = 1
                if event.key == pygame.K_s:
                    self.moving['down'] = 1
                if event.key == pygame.K_w:
                    self.moving['up'] = 1
                if event.key == pygame.K_UP:
                    self.player.nextweapon()
                if event.key == pygame.K_p:
                    self.player.delete_weapon()
                if event.key == pygame.K_o:
                    self.player.delete_range()
                if event.key == pygame.K_i:
                    self.player.delete_armor(self)
                if event.key == pygame.K_1:
                    self.player.enchantw(self)
                if event.key == pygame.K_2:
                    self.player.enchantr(self)
                if event.key == pygame.K_3:
                    self.player.enchanta(self)
                if event.key == pygame.K_RIGHT:
                    self.player.nextrange()
                if event.key == pygame.K_DOWN:
                    self.player.nextc()
                if event.key == pygame.K_LEFT:
                    self.player.nextarmor(self)
                if event.key == pygame.K_u:
                    self.player.special2(self)
                if event.key == pygame.K_4:
                    self.player.na(1)
                if event.key == pygame.K_5:
                    self.player.na(2)
                if event.key == pygame.K_6:
                    self.player.na(3)
                if event.key == pygame.K_7:
                    self.player.usea(1, self)
                if event.key == pygame.K_8:
                    self.player.usea(2, self)
                if event.key == pygame.K_9:
                    self.player.usea(3, self)
                if event.key == pygame.K_F2:  # take a screenshot
                    name = 'screenshot_' + str(datetime.datetime.now()).replace(
                        '/', '_').replace(':', '_').replace('-', '_').replace('.', '_') + '.png'
                    pygame.image.save(screen, os.path.join(
                        BASEPATH, 'screenshots', name))
                    self.message('Screenshot saved as ' + name)
                if event.key == pygame.K_t:
                    t = textinput(self, '')
                    dungeon_parser.parse(
                        self, t)  # just parse the chat in a different module
                if event.key == pygame.K_ESCAPE:  # pause game
                    do_quit = self.pausemenu()
            if event.type == pygame.KEYUP:  # stop moving if move keys are released
                if event.key == pygame.K_a:
                    self.moving['left'] = 0
                if event.key == pygame.K_d:
                    self.moving['right'] = 0
                if event.key == pygame.K_s:
                    self.moving['down'] = 0
                if event.key == pygame.K_w:
                    self.moving['up'] = 0

        if self.moving['left'] == 1:  # move player, scroll objects
            if self.player.rect.x > 100:
                self.player.move(self, x=-3)
            else:
                self.scroll(x=3 + self.player.increase())
        if self.moving['right'] == 1:
            if self.player.rect.x < self.screen.get_width() - 100:
                self.player.move(self, x=3)
            else:
                self.scroll(x=-3 - self.player.increase())
        if self.moving['down'] == 1:
            if self.player.rect.y < self.screen.get_height() - 100:
                self.player.move(self, y=3)
            else:
                self.scroll(y=-3 - self.player.increase())
        if self.moving['up'] == 1:
            if self.player.rect.y > 100:
                self.player.move(self, y=-3)
            else:
                self.scroll(y=3 + self.player.increase())

        # leftclick=melee
        if pygame.mouse.get_pressed()[0] == 1 and self.player.cooldown <= 0:
            self.player.attack(self)
        # rightclick=ranged (dunno why i called it special)
        elif pygame.mouse.get_pressed()[2] == 1 and self.player.rcooldown <= 0:
            self.player.special(self)

        self.screen.fill(self.screen_color)  # clear the screen

        self.enemy_delay += 1  # spawn enemies
        if self.enemy_delay > 500 + random.randint(-20, 20) - (self.player.difficulty * 7) - ((self.dif-1) * 5):
            self.add_enemy()
            self.enemy_delay = 0

        self.chest_delay += 1  # spawn chests
        if self.chest_delay > 600 + random.randint(-20, 20) - ((self.player.difficulty * 7) // 2) - ((self.dif-1) * 5):
            self.spawn_chest()
            self.chest_delay = 0

        if func:
            # when artifacts are being used (explanations in weapons module)
            func(self)

        self.objects_render()  # draw everything

        # uh, why is do_quit False when you quit? that's kinda weird...
        return not do_quit

    def add_enemy(self):
        if random.randint(0, 99) == 0:  # make a spawner
            self.spawners.append(random.choice(dungeon_enemies.spawners)(random.randint(
                0, self.screen.get_width()), random.randint(0, self.screen.get_height())))
        else:
            num = random.randrange(0, 100)
            num += (1 - self.dif) * 5  # harder enemies in harder difficulties
            if num in range(60):  # easy enemy (60% chance)
                self.enemies.append(random.choice(dungeon_enemies.easy)(random.randint(
                    0, self.screen.get_width()), random.randint(0, self.screen.get_height())))
            elif num in range(60, 90):  # medium enemy (30% chance)
                self.enemies.append(random.choice(dungeon_enemies.medium)(random.randint(
                    0, self.screen.get_width()), random.randint(0, self.screen.get_height())))
            elif num in range(90, 98):  # hard enemy (8% chance)
                self.enemies.append(random.choice(dungeon_enemies.hard)(random.randint(
                    0, self.screen.get_width()), random.randint(0, self.screen.get_height())))
            else:
                if random.randint(0, 10) == 0:  # boss enemy (0.1% chance)
                    self.enemies.append(random.choice(dungeon_enemies.boss)(random.randint(
                        0, self.screen.get_width()), random.randint(0, self.screen.get_height())))
                else:  # very hard enemy (1.9% chance)
                    self.enemies.append(random.choice(dungeon_enemies.very_hard)(random.randint(
                        0, self.screen.get_width()), random.randint(0, self.screen.get_height())))
            if self.dif == 2:
                self.enemies[-1].hp = self.enemies[-1].hpmax = self.enemies[-1].hpmax + 10
            elif self.dif == 3:
                self.enemies[-1].hp = self.enemies[-1].hpmax = self.enemies[-1].hpmax + 20

    def objects_render(self):

        wcooldown_rect = pygame.Rect(
            5, self.screen.get_height() - 35, int(self.player.cooldown * 50), 30)
        pygame.draw.rect(self.screen, pygame.Color('red'),
                         wcooldown_rect)  # cooldown of weapon

        rcooldown_rect = pygame.Rect(
            5, self.screen.get_height() - 70, int(self.player.rcooldown * 50), 30)
        pygame.draw.rect(self.screen, pygame.Color('red'),
                         rcooldown_rect)  # cooldown of bow

        level_rect = pygame.Rect(
            (self.screen.get_height() // 2) - 80, 15, int(self.player.level_prog * 200), 5)
        pygame.draw.rect(self.screen, pygame.Color(
            'green'), level_rect)  # level progress

        self.player.render(self)  # draw the player

        # helpfuls, enemies, chests, arrows, walls, other, spawners (shouldn't need an explanation)

        for helpful in self.helpfuls:
            helpful.render(self)

        for enemy in self.enemies:
            enemy.render(self)

        for chest in self.chests:
            chest.render(self)

        for arrow in self.arrows:
            arrow.render(self)

        for wall in self.walls:
            wall.render(self)

        for other in self.other:
            other.render(self)

        for spawner in self.spawners:
            spawner.render(self)

        if time.time() - self.pending_timer >= 4:  # get rid of the most recent chat message
            self.pending_timer = time.time()
            if self.pending_messages:
                self.pending_messages.pop(0)

        # draw all the chat messages
        for index, messag in enumerate(self.pending_messages):
            # self.screen.blit(self.pending_messages[messag][0], ((self.screen.get_width()) - self.pending_messages[messag][1], (messag + 1) * 20))
            self.screen.blit(messag, (0, (index + 5) * 20))

        pygame.display.update()  # update screen

    # draws objects, but does not tick them (=enemy AI, arrow moving, etc.)
    def objects_draw(self, update=True):

        wcooldown_rect = pygame.Rect(
            5, self.screen.get_height() - 35, int(self.player.cooldown), 30)
        pygame.draw.rect(self.screen, pygame.Color('red'),
                         wcooldown_rect)  # cooldown of weapon

        rcooldown_rect = pygame.Rect(
            5, self.screen.get_height() - 70, int(self.player.rcooldown), 30)
        pygame.draw.rect(self.screen, pygame.Color('red'),
                         rcooldown_rect)  # cooldown of bow

        level_rect = pygame.Rect(
            (self.screen.get_height() // 2) - 80, 15, int(self.player.level_prog * 200), 5)
        pygame.draw.rect(self.screen, pygame.Color(
            'green'), level_rect)  # level progress

        self.player.draw(self)

        for helpful in self.helpfuls:
            helpful.draw(self)

        for enemy in self.enemies:
            enemy.draw(self)

        for chest in self.chests:
            chest.draw(self)

        for arrow in self.arrows:
            arrow.draw(self)

        for other in self.other:
            other.draw(self)

        for wall in self.walls:
            wall.draw(self)

        for spawner in self.spawners:
            spawner.draw(self)

        if time.time() - self.pending_timer >= 1:
            self.pending_timer = time.time()

        for index, messag in enumerate(self.pending_messages):
            # self.screen.blit(self.pending_messages[messag][0], ((self.screen.get_width()) - self.pending_messages[messag][1], (messag + 1) * 20))
            self.screen.blit(messag, (0, (index + 5) * 20))

        if update:
            pygame.display.update()  # i think update is always True, though

    def loop(self):  # loop the game
        while True:
            do_quit = self.play()
            if do_quit:
                if dungeon_settings.RUN_PDPY_SERVER:
                    self.pdpyserv.stop()  # stop the PDPY server if game has quit
                raise UnicodeError  # play() function catches exception and quits the game (since a UnicodeError will never actually happen lol)

    def message(self, message, x_offset=0):  # send a chat message
        self.pending_timer = time.time()
        self.pending_messages.append(pygame.font.SysFont(
            '', 20).render(message, 1, pygame.Color('black')))

    def spawn_chest(self):
        if random.randint(0, 25) == 0:
            self.other.append(dungeon_misc.EmeraldPot(random.randint(0, self.screen.get_width(
            )), random.randint(0, self.screen.get_height())))  # emerald pot
        else:
            choice = random.choice(self.chests_pool)
            self.chests.append(chests[choice](random.randint(0, self.screen.get_width(
            )), random.randint(0, self.screen.get_height())))  # random chest from the pool

    def killall(self):  # kill all the enemies
        for enemy in self.enemies:
            enemy.rect.x = enemy.rect.y = 10000
        self.enemies.clear()

    def pausemenu(self):  # pause menu (i don't think this needs an explanation... just quits if you hit the `close` button, returns (essentialy) if you resume, and quits if you hit `save and quit` (saves are automatic when you quit)
        self.button_resume = dungeons_gui.Button(pygame.Rect(100, 100, self.screen.get_width(
        ) - 200, 200), 'light gray', 'Resume Game', self.loop, 100, PATH)
        self.button_quit = dungeons_gui.Button(pygame.Rect(100, 400, self.screen.get_width(
        ) - 200, 200), 'light gray', 'Save and Quit', self.quit, 100, PATH)
        while True:
            events = pygame.event.get()
            self.button_resume.update(events)
            self.button_quit.update(events)
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    logger.info('Window has closed.')
                    logger.info('Stopping!')
                    logger.stop()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.loop()
                if event.type == pygame.VIDEORESIZE:
                    self.button_resume.update_(
                        100, 100, self.screen.get_width() - 200, 200, 100)
                    self.button_quit.update_(
                        100, 400, self.screen.get_width() - 200, 200, 100)
            pygame.display.update()

    def quit(self):
        self.hasquit = True  # quit game
        self.button_resume.destroy()
        self.button_quit.destroy()
        self.button_resume = self.button_quit = None
        if dungeon_settings.RUN_PDPY_SERVER:
            self.pdpyserv.stop()  # stop the PDPY server
        raise UnicodeError  # triggers an except to return to main menu

    def scroll(self, x=0, y=0):
        all = self.get_all()
        for object in all:
            if hasattr(object, 'rect') and object.rect and not hasattr(object, 'xrect'):
                object.rect = object.rect.move(x, y)  # normal movement
            elif hasattr(object, 'rect') and object.rect:
                object.move_xy(x, y)  # arrows must be moved specially
            if hasattr(object, 'drect'):
                object.drect = object.drect.move(x, y)  # move the drect
            # don't move arrows, but move other things with x and y attributes
            if hasattr(object, 'x') and hasattr(object, 'y') and not hasattr(object, 'rect'):
                object.x += x
                object.y += y

# lots of short functions that just mean `BACK TO MAIN MENU!`


def stop():
    global stop_credits
    stop_credits = True


def back():
    global stop_options
    stop_options = True


def menu():
    global stop_controls
    stop_controls = True


def main_menu():
    global stop_menu
    stop_menu = True


def show_credits():
    global stop_credits
    text = [pygame.font.Font(PATH, 70).render('Coded by: VolcanicAsh999', 1, pygame.Color('black')),
            pygame.font.Font(PATH, 70).render(
                'Characters created by: VolcanicAsh999', 1, pygame.Color('black')),
            pygame.font.Font(PATH, 70).render(
                'Pretty much everything: VolcanicAsh999', 1, pygame.Color('black')),
            pygame.font.Font(PATH, 70).render('Inspired by: Minecraft Dungeons', 1, pygame.Color('black'))]  # it was all me... lol
    button_back = dungeons_gui.Button(pygame.Rect((50), (screen.get_height(
    ) - 100), 300, 80), 'light gray', 'Back', stop, 60, PATH)  # brings you back to main menu
    while True:
        events = pygame.event.get()
        screen.fill(screen_color)
        button_back.update(events)
        for line in range(len(text)):
            # show the credits
            screen.blit(
                text[line], (10, ((screen.get_height() // len(text)) * line) + 50))
        for event in events:
            if event.type == pygame.QUIT:  # quit
                logger.info('Window has closed.')
                logger.info('Stopping!')
                logger.stop()
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.VIDEORESIZE:
                button_back.update_(50, screen.get_height() - 100, 300, 80, 60)
        pygame.display.update()
        if stop_credits:
            stop_credits = False
            main()

# old functions


def toggle_save():
    global button_save
    dungeon_settings.RSAVE = not dungeon_settings.RSAVE
    button_save.set_text(
        'Read Save (' + ('on' if dungeon_settings.RSAVE else 'off') + ')')


def toggle_save2():
    global button_save2
    dungeon_settings.WSAVE = not dungeon_settings.WSAVE
    button_save2.set_text(
        'Write Save (' + ('on' if dungeon_settings.WSAVE else 'off') + ')')

# thingy to reset game


def reset():
    game = Game(spx, spy, False, 'q', 'q')
    saving.save_world(game)
    del game


def show_options():  # no options
    global stop_options, button_save, button_save2
    button_back = dungeons_gui.Button(pygame.Rect((screen.get_width(
    ) // 2 - 150), (screen.get_height() - 200), 300, 80), 'light gray', 'Back', back, 60, PATH)
    button_sneak = dungeons_gui.Button(pygame.Rect((screen.get_width(
    ) // 2 - 150), (screen.get_height() - 300), 300, 80), screen_color, 'Coming Soon!', lambda: ..., 60, PATH)
    while True:
        events = pygame.event.get()
        screen.fill(screen_color)
        button_back.update(events)
        button_sneak.update(events)
        for event in events:
            if event.type == pygame.QUIT:
                logger.info('Window has closed.')
                logger.info('Stopping!')
                logger.stop()
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.VIDEORESIZE:
                button_back.update_(
                    (screen.get_width() // 2 - 150), (screen.get_height() - 200), 300, 80, 60)
                button_sneak.update_(
                    (screen.get_width() // 2 - 150), (screen.get_height() - 300), 300, 80, 60)
        pygame.display.update()
        if stop_options:
            stop_options = False
            main()


def show_controls():
    global stop_controls
    button_back = dungeons_gui.Button(pygame.Rect((screen.get_width(
    ) // 2 - 150), (screen.get_height() - 90), 300, 80), 'light gray', 'Back', menu, 60, PATH)

    def construct(text):
        return pygame.font.SysFont(PATH, 40).render(text, 1, pygame.Color('black'))

    def centerx(x, surf):
        return x - (surf.get_width() // 2)
    text = [construct('WASD: Move'),
            construct('Left Arrow: Toggle Armor'),
            construct('Right Arrow: Toggle Melee Weapon'),
            construct('Up Arrow: Toggle Ranged Weapon'),
            construct('Down Arrow: Toggle Consumable'),
            construct('1, 2, 3: Enchant Melee, Ranged Weapon, Armor'),
            construct('4, 5, 6: Toggle Artifact'),
            construct('7, 8, 9: Use Artifact'),
            construct('I, O, P: Salvage Armor, Ranged, Melee Weapon'),
            construct('U: Use Consumable'),
            construct('Left Click: Use Melee Weapon'),
            construct('Right Click: Use Range Weapon')]  # construct the text
    while True:
        events = pygame.event.get()
        screen.fill(screen_color)
        button_back.update(events)
        index = 0
        for y in range(0, 12):
            screen.blit(text[index], (centerx(
                screen.get_width() // 2, text[index]), (y * 55) + 5))  # draw the controls text
            index += 1
        for event in events:
            if event.type == pygame.QUIT:
                logger.info('Window has closed.')
                logger.info('Stopping!')
                logger.stop()
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.VIDEORESIZE:
                button_back.update_(
                    (screen.get_width() // 2 - 150), (screen.get_height() - 90), 300, 80, 60)
        pygame.display.update()
        if stop_controls:
            stop_controls = False  # return
            main()


def play(filename):
    global spx, spy, saving
    font = pygame.font.Font(dungeon_settings.FONT_PATH, 300)
    screen.fill(screen_color)
    # log info about world
    logger.info('World selected: ' + saving.worldname(filename))
    logger.info('Loading world...')
    screen.blit(font.render('Loading...', 1, pygame.Color('black')),
                (100, 300))  # loading screen
    pygame.display.update()
    game = Game(spx, spy, dungeon_settings.RSAVE,
                saving.worldname(filename), filename)  # make a game
    saving = game.saving
    globals().update({'game': game})  # why...?
    if dungeon_settings.RSAVE:
        # log that world is being made
        logger.info(f'Loading world {saving.worldname(filename)} from save...')
        saving.load_world(game, filename)  # load world
    try:
        # log that world has been loaded
        logger.info(f'World {saving.worldname(filename)} succesfully loaded!')
        game.loop()  # play the game
    except UnicodeError:  # game quit
        if dungeon_settings.WSAVE:  # save the game
            logger.info('World closed: ' + saving.worldname(filename))
            logger.info(f'Saving World {saving.worldname(filename)}...')
            saving.save_world(game, saving.worldname(filename), filename)
            logger.info(
                f'World {saving.worldname(filename)} succesfully saved!')
        del game
        main()
    except Exception as e:  # there was an actual error
        error = e
        # attempt to save (if the error didn't have to do with saving the game)
        if dungeon_settings.WSAVE:
            try:
                saving.save_world(game, saving.worldname(filename), filename)
            except Exception as e:
                logger.fatal_with_no_quit('Error saving world ' + saving.worldname(
                    filename) + ', save may be corrupted - ' + e.args[0])
        del game
        traceback.print_exc()  # print the exception message
        answer = messagebox('Sorry',
                            'Sorry, an error has occurred and the game has crashed.',
                            info=True,
                            buttons=('Ok', 'Quit'),
                            return_button=0,
                            escape_button=1,
                            )  # sorry, the game has crashed...
        logger.fatal_with_no_quit(error.args[0])
        if answer == 0:
            main()
        elif answer == 1:  # quit game
            logger.info('Window has closed.')
            logger.info('Stopping!')
            logger.stop()
            pygame.quit()
            sys.exit(0)


def new_world():
    global spx, spy
    logger.info('Creating new world.')  # make a new world
    # still haven't made a decent GUI for world creation
    name = text__input('World Name', 'Enter World Name')
    if name in ['', None]:
        return
    logger.info('Creating the world, name is ' + name)
    game = Game(spx, spy, False, name, name)
    saving.save_world(game, name, name)
    del game
    logger.info(f'World created with name {name}.')  # make the world
    play(name)  # play it


def changename(filename):
    new = textinput('New Name', 'Enter a new name for the world:')
    saving.changename(filename, new)


def edit_world(filename):  # change various things about the world (just the name for now, actually)
    button_back = dungeons_gui.Button(pygame.Rect(
        50, (screen.get_height() - 90), 300, 80), 'light gray', 'Back', startgame, 60, PATH)
    button_edit_name = dungeons_gui.Button(pygame.Rect(screen.get_width(
    ) - 350, (screen.get_height() - 90), 300, 80), 'light gray', 'Change Name', changename, 60, PATH, args=(filename,))
    while True:
        events = pygame.event.get()
        screen.fill(screen_color)
        button_back.update(events)
        button_edit_name.update(events)
        for event in events:
            if event.type == pygame.QUIT:
                logger.info('Window has closed.')
                logger.info('Stopping!')
                logger.stop()
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.VIDEORESIZE:
                button_back.update_(
                    50, (screen.get_height() - 90), 300, 80, 60)
                button_edit_name.update_(
                    screen.get_width() - 350, (screen.get_height() - 90), 300, 80, 60)
        pygame.display.update()


def startgame():
    global stop_menu
    # load the world selection screen
    logger.info('Going to World Selection screen.')

    def scroll_menu(y_change):
        for button in [(button_back, 1), (button_new, 1)] + list(worldbuttons.values()):
            button[0].rect.y -= y_change
    button_back = dungeons_gui.Button(pygame.Rect(
        50, (screen.get_height() - 90), 300, 80), 'light gray', 'Back', main_menu, 60, PATH)
    button_new = dungeons_gui.Button(pygame.Rect(screen.get_width(
    ) - 350, (screen.get_height() - 90), 300, 80), 'light gray', 'New World', new_world, 60, PATH)
    worldbuttons = {}
    for index, name in enumerate(saving.listworldnames()):
        filename = saving.worlddata(name)
        worldbuttons[index] = (dungeons_gui.Button(pygame.Rect(20, (screen.get_height() - (90 * (index + 2))), screen.get_width(
        ) - 40, 80), 'light gray', f'Play World {name}', play, 60, args=(filename,), font='default'), filename)
    scrollbar = None
    if len(worldbuttons.values()) > 7:
        scrollbar = dungeons_gui.ScrollBar((screen.get_width(
        ) - 50, 50), 700, scroll_menu, pygame.Color('green'), do_update_every_motion=True)
        # you have too many worlds
        logger.warn('Too many worlds are present to be on the screen!')
    # this is probably a needlessly complicated way of getting a list of worlds
    while True:
        events = pygame.event.get()
        screen.fill(screen_color)
        for button in worldbuttons.values():
            button[0].update(events)
        if scrollbar:
            scrollbar.update(events)
        pygame.draw.rect(screen, pygame.Color('green'),
                         pygame.Rect(0, 0, screen.get_width(), 50))
        pygame.draw.rect(screen, pygame.Color('green'), pygame.Rect(
            0, screen.get_height() - 50, screen.get_width(), 50))
        button_back.update(events)
        button_new.update(events)
        for event in events:
            if event.type == pygame.QUIT:
                logger.info('Window has closed.')
                logger.info('Stopping!')
                logger.stop()
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.VIDEORESIZE:
                button_back.update_(
                    50, (screen.get_height() - 90), 300, 80, 60)
                button_new.update_(screen.get_width() - 350,
                                   (screen.get_height() - 90), 300, 80, 60)
                for index, name in enumerate(worldbuttons.values()):
                    worldbuttons[index][0].update_(20, (screen.get_height(
                    ) - (90 * (index + 2))), screen.get_width() - 40, 80, 60)  # show all the worlds
        pygame.display.update()
        if stop_menu:
            stop_menu = False
            main()


def gen_splashtexts(text=None):  # make the pygame.font.Font objects using the splash text
    if not text:
        text = random.choice(dungeon_settings.SPLASH_SCREEN_TEXT)
    # splash = pygame.font.SysFont(text, 100).render(text, 1, (0, 0, 0, 255))
    # fontsize = (splash.get_width() // len(text)) + 10
    # fontsize = round((1.5/splash.get_width()) * 20 * 700)
    fontsize = dungeon_settings.SPLASH_SCREEN_SIZE[text]
    splash_text = pygame.font.SysFont(text, fontsize).render(
        text, 1, pygame.Color('yellow'))
    splash_text = pygame.transform.scale2x(
        pygame.transform.rotate(splash_text, 30))
    # x = screen.get_width() - splash_text.get_width() - 30
    # y = 450
    x = 30
    y = 70
    texts = []
    for i in range(-10, 10):
        for j in range(3):
            texts.append(pygame.transform.scale(
                splash_text, (splash_text.get_width() + (i * 2), splash_text.get_height() + (i * 2))))
    for i in range(10, -10, -1):
        for j in range(3):
            texts.append(pygame.transform.scale(
                splash_text, (splash_text.get_width() + (i * 2), splash_text.get_height() + (i * 2))))
    texts = itertools.cycle(iter(texts))
    return (text, texts, x, y)


def change_difficulty():
    if dungeon_settings.DIFFICULTY == 'Default':
        dungeon_settings.DIFFICULTY = 'Adventure'
    elif dungeon_settings.DIFFICULTY == 'Adventure':
        dungeon_settings.DIFFICULTY = 'Apocalypse'
    elif dungeon_settings.DIFFICULTY == 'Apocalypse':
        dungeon_settings.DIFFICULTY = 'Default'
    else:
        logger.error(
            f'Difficulty {dungeon_settings.DIFFICULTY} does not exist.')
    logger.info(f'Difficulty changed to {dungeon_settings.DIFFICULTY}.')


def main(options=None):
    
    button_start = dungeons_gui.Button(pygame.Rect(50, (screen.get_height(
    ) // 2) - 200, screen.get_width() - 100, 400), 'light gray', 'Start Game', startgame, 200, PATH)
    button_end = dungeons_gui.Button(pygame.Rect(50, (screen.get_height(
    ) - 100), 300, 80), 'light gray', 'Quit', stop_play, 60, PATH)
    button_credits = dungeons_gui.Button(pygame.Rect((screen.get_width(
    ) - 350), (screen.get_height() - 100), 300, 80), 'light gray', 'Credits', show_credits, 60, PATH)
    button_options = dungeons_gui.Button(pygame.Rect(((screen.get_width(
    ) // 2) - 150), (screen.get_height() - 100), 300, 80), 'light gray', 'Options', show_options, 60, PATH)
    button_controls = dungeons_gui.Button(pygame.Rect((screen.get_width(
    ) // 2) - 150, 10, 300, 80), 'light gray', 'Controls', show_controls, 60, PATH)
    button_difficulty = dungeons_gui.Button(pygame.Rect((screen.get_width(
    ) - 350), 10, 300, 80), 'light gray', 'Default', change_difficulty, 60, PATH)
    text, texts, x, y = gen_splashtexts()  # get the splash text
    try:
        while True:
            events = pygame.event.get()
            screen.fill(screen_color)
            button_start.update(events)
            button_end.update(events)
            button_credits.update(events)
            button_options.update(events)
            button_controls.update(events)
            button_difficulty.update(events)
            screen.blit(next(texts), (x, y))
            if button_difficulty.text != dungeon_settings.DIFFICULTY:
                button_difficulty.set_text(dungeon_settings.DIFFICULTY)
            for event in events:
                if event.type == pygame.QUIT:
                    logger.info('Window has closed.')
                    logger.info('Stopping!')
                    logger.stop()
                    pygame.quit()
                    sys.exit(0)
                elif event.type == pygame.VIDEORESIZE:
                    screen.fill(screen_color)
                    text, texts, x, y = gen_splashtexts(text)
                    button_start.update_(
                        50, (screen.get_height() // 2) - 200, screen.get_width() - 100, 400, 200)
                    button_end.update_(
                        50, (screen.get_height() - 100), 300, 80, 60)
                    button_credits.update_(
                        (screen.get_width() - 350), (screen.get_height() - 100), 300, 80, 60)
                    button_options.update_(
                        (screen.get_width() // 2) - 150, (screen.get_height() - 100), 300, 80, 60)
                    button_controls.update_(
                        (screen.get_width() // 2) - 150, 10, 300, 80, 60)
                    button_difficulty.update_(
                        (screen.get_width() - 350), 10, 300, 80, 60)
                    # logger.info('Window has been resized to width=' + str(event.width) + ', height=' + str(event.height))  # apparently this dont work which is weird (not important though)
            pygame.display.update()
    except Exception as e:
        pygame.quit()
        logger.fatal_with_no_quit(
            'Unrecognized exception ' + str(e.args[0]))  # unrecognized error!
        logger.stop()
        sys.exit('Unrecognized exception ' + str(e.args[0]))


if __name__ == '__main__':
    def main_():
        # see, it says `starting game` and `loading PyDungeons {__version__}` twice
        logger.info('Starting Game.')
        main()
    main_()
