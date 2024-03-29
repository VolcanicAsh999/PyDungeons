import dungeon_resloader
import os
import pygame
import threading
import time
import random
import dungeon_logger as logger
import string

pygame.mixer.pre_init()
pygame.init()

RUN_PDPY_SERVER = False  # uses extra resources, wip

USE_MODS = False  # leave false, wip

RSAVE = True
WSAVE = True

DO_FULL_SCREEN = False

FRIENDLY_MODE = True

DIFFICULTY = 'Default'

MINUTES_PER_SAVE = 3

USE_CUSTOM_CURSOR = True

BACKUP_CURSOR = pygame.cursors.tri_left

CURSOR = (
    "       XX       ",
    "       XX       ",
    "       XX       ",
    "       XX       ",
    "       XX       ",
    "       XX       ",
    "       XX       ",
    "XXXXXXXXXXXXXXXX",
    "XXXXXXXXxXXXXXXX",
    "       XX       ",
    "       XX       ",
    "       XX       ",
    "       XX       ",
    "       XX       ",
    "       XX       ",
    "       XX       ",
)

"""CURSOR = (
    "   XX   ",
    "   XX   ",
    "   XX   ",
    "XXXXXXXX",
    "XXXXxXXX",
    "   XX   ",
    "   XX   ",
    "   XX   ",
)"""


def initcursor():
    logger.info('Initializing the cursor...', 'ResourceLoader')
    if not USE_CUSTOM_CURSOR:
        pygame.mouse.set_cursor(BACKUP_CURSOR)
        logger.info('Using normal cursor!', 'ResourceLoader')
        return
    hotspot = None
    for y, line in enumerate(CURSOR):
        for x, char in enumerate(line):
            if char in ["x", ",", "O"]:
                hotspot = x, y
                break
        if hotspot is not None:
            break
    if hotspot is None:
        pygame.mouse.set_cursor(BACKUP_CURSOR)
        logger.error('Error setting cursor: no hotspot defined',
                     'ResourceLoader')
        logger.info('Using normal cursor!', 'ResourceLoader')
        return
    s2 = []
    for line in CURSOR:
        s2.append(line.replace("x", "X").replace(",", ".").replace("O", "o"))
    try:
        cursor, mask = pygame.cursors.compile(s2, "X", ".", "o")
        size = len(CURSOR[0]), len(CURSOR[1])
        pygame.mouse.set_cursor(size, hotspot, cursor, mask)
        logger.info('Using crosshair cursor!', 'ResourceLoader')
    except Exception as e:
        logger.error('Error setting cursor: ' + e.args[0], 'ResourceLoader')
        logger.info('Using normal cursor!', 'ResourceLoader')


SPLASH_SCREEN_TEXT = ['Hello!',
                      'Password12345 is a bad password',
                      'This text is so small you can\'t see it very well',
                      'gg',
                      ]
SPLASH_SCREEN_SIZE = {'Hello!': 35,
                      'gg': 50,
                      'Password12345 is a bad password': 20,
                      'This text is so small you can\'t see it very well': 10,
                      }

BASEPATH = os.path.join(os.environ.get('APPDATA'), '.pydungeons')

def load(basepath):
    global BASEPATH, RESOURCE_PATH, FONT_PATH, LOG_PATH, CRASH_REPORT_PATH, SCRIPTS_PATH, bg1, bg2, bg3, bg4, zombie_die, zombie_groan, chest_loot, bow_shoot, arrow_hit, weapon_swing, weapon_hit
    RESOURCE_PATH = os.path.join(BASEPATH, 'resources')
    FONT_PATH = os.path.join(RESOURCE_PATH, 'arfmoochikncheez.ttf')
    LOG_PATH = os.path.join(BASEPATH, 'logs')
    CRASH_REPORT_PATH = os.path.join(BASEPATH, 'crash-reports')
    SCRIPTS_PATH = os.path.join(BASEPATH, 'scripts')

    _warn = False
    if not os.path.exists(os.path.join(BASEPATH, 'logs')):
        os.makedirs(os.path.join(BASEPATH, 'logs'))
        _warn = True
    logger.init()
    if not os.path.exists(BASEPATH):
        os.makedirs(BASEPATH)
        logger.critical(
            'Base path is not available, creating it now...', 'ResourceLoader')
    if _warn:
        logger.critical(
            'Base path is not available, creating it now...', 'ResourceLoader')
        logger.error('Logs path is not available, creating it now...',
                     'ResourceLoader')
    if not os.path.exists(os.path.join(BASEPATH, 'resources')):
        os.makedirs(os.path.join(BASEPATH, 'resources'))
        logger.critical(
            'Resource path is not available, creating it now...', 'ResourceLoader')
    if not os.path.exists(os.path.join(BASEPATH, 'crash-reports')):
        os.makedirs(os.path.join(BASEPATH, 'crash-reports'))
        logger.error(
            'Crash reports path is not available, creating it now...', 'ResourceLoader')
    for i in ['screenshots', 'saves', 'mods', 'backups', 'scripts']:
        if not os.path.exists(os.path.join(BASEPATH, i)):
            logger.error(string.capwords(
                i) + ' path is not available, creating it now...', 'ResourceLoader')
            os.makedirs(os.path.join(BASEPATH, i))
    dungeon_resloader.check()

    bg1 = None  # pygame.mixer.Sound(os.path.join(RESOURCE_PATH, '1.wav'))
    bg2 = None  # pygame.mixer.Sound(os.path.join(RESOURCE_PATH, '2.wav'))
    bg3 = None  # pygame.mixer.Sound(os.path.join(RESOURCE_PATH, '3.wav'))
    bg4 = None  # pygame.mixer.Sound(os.path.join(RESOURCE_PATH, '4.wav'))

    zombie_groan = pygame.mixer.Sound(
        os.path.join(RESOURCE_PATH, 'zombie_groan.ogg'))
    zombie_die = pygame.mixer.Sound(
        os.path.join(RESOURCE_PATH, 'zombie_death.ogg'))

    chest_loot = pygame.mixer.Sound(os.path.join(RESOURCE_PATH, 'chestloot.wav'))

    bow_shoot = pygame.mixer.Sound(os.path.join(RESOURCE_PATH, 'bow_shoot.ogg'))
    arrow_hit = pygame.mixer.Sound(os.path.join(RESOURCE_PATH, 'arrow_hit.ogg'))

    weapon_swing = pygame.mixer.Sound(
        os.path.join(RESOURCE_PATH, 'weapon_swing.ogg'))
    weapon_hit = pygame.mixer.Sound(os.path.join(RESOURCE_PATH, 'weapon_hit.ogg'))


def bgsound():
    bgsounds = [bg1, bg2, bg3, bg4]
    for sound in bgsounds:
        sound.set_volume(70/100)
    random.shuffle(bgsounds)
    while True:
        for bg in bgsounds:
            bg.play()
            time.sleep(bg.get_length())
        random.shuffle(bgsounds)


def start():
    if bg1 and bg2 and bg3 and bg4:
        music_thread = threading.Thread(target=bgsound, daemon=True)
        logger.info('Starting music thread...', 'ResourceLoader')
        music_thread.start()
        logger.info('Music thread succesfully started!', 'ResourceLoader')
    else:
        logger.error('Music missing, music thread not starting...',
                     'ResourceLoader')
