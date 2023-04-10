import re
import dungeon_logger as logger
import os
import dungeon_settings, dungeon_weapons, dungeon_enemies, dungeon_chests, dungeon_helpful, dungeon_arrows

def message(game):
    def message_(what):
        logger.chat(what, '')
        game.message(what)
    return message_

def get_globals(game, args):
    return {'message': message(game), 'args': args, 'game': game, 'self': game.player, 'player': game.player, 'settings': dungeon_settings, 'weapons': dungeon_weapons, 'enemies': dungeon_enemies, 'chests': dungeon_chests, 'helpfuls': dungeon_helpful, 'arrows': dungeon_arrows}

def run_script(game, name, args):
    if '.' not in name: name += '.py'
    try:
        f = open(name)
    except OSError:
        try:
            f = open(os.path.join(dungeon_settings.SCRIPTS_PATH, name))
        except OSError:
            try:
                f = open(os.path.join(os.getcwd(), 'commands', name))
            except OSError:
                return 'Script ' + f + ' not found!'
    try:
        exec(f.read(-1), get_globals(game, args))
        f.close()
    except Exception as e:
        #logger.error('Exception running command - ' + str(e), 'CommandParser')
        try: f.close()
        except: pass
        return str(e)
    return 0

def parse(game, text):
    if text.startswith('/'):
        parsecmd(game, text[1:])
    else:
        if text != '':
            x = 0
            y = ''
            while x != 1:
                if len(text) < 300:
                    y += text
                    x = 1
                else:
                    y += text[:300] + '\n'
                    text = text[300:]
            p = y.split('\n')
            if len(p) == 1:
                game.message(f'<{game.pname}> {p[0]}')
            else:
                game.message(f'<{game.pname}> {p[0]}')
                for i in p[1:]:
                    game.message(f'              {i}')
            logger.chat(p[0], game.pname)

def parsecmd(game, cmd, stop=False):
    if re.match('^code ', cmd):
        cmd = cmd[5:]
        try:
            exec(cmd, get_globals(game, None), get_globals(game, None))
        except Exception as e:
            game.message('Error executing code - ' + str(e))
            logger.error('Error executing code - ' + str(e))
            return
    elif re.match('^script ', cmd):
        cmd = cmd[7:]
        a = cmd.split(' ')
        if len(a) == 1:
            cmd = a[0]
            args = []
        else:
            cmd = a[0]
            args = a[1:]
        try:
            logger.chat('/' + cmd + ' ' + ' '.join(args), game.pname)
            success = run_script(game, cmd, args)
            if success != 0:
                game.message(success)
                logger.error(success)
                return
        except Exception as e:
            game.message('Error executing script - ' + str(e))
            return
    elif not stop:
        parsecmd(game, 'script ' + cmd, stop=True)
