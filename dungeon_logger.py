import os
import datetime
import sys

_file = None
LOG_PATH = None
CRASH_REPORT_PATH = None
_is_init = False


def gettime():
    x = datetime.datetime.now()
    return str(x)


def getpath():
    m = 0

    def getname():
        x = datetime.datetime.now()
        return str(x.date())
    a = getname()
    while os.path.exists(os.path.join(LOG_PATH, a + ('' if m == 0 else ('-' + str(m)))) + '.log'):
        m += 1
    return os.path.join(LOG_PATH, getname() + ('' if m == 0 else ('-' + str(m)))) + '.log'


def init():
    global _file, LOG_PATH, CRASH_REPORT_PATH, _is_init
    if _is_init:
        return
    _is_init = True
    from dungeon_settings import LOG_PATH, CRASH_REPORT_PATH
    _file = open(getpath(), 'w')


def is_init():
    return _is_init


def stop():
    global _file, _is_init
    if not _is_init:
        return
    _is_init = False
    _file.close()


def _get(msg, src, lvl):
    text = f'[{gettime()}] [{src}/{lvl}] {msg}'
    return text


def _get_crash():
    return getpath().replace(LOG_PATH, CRASH_REPORT_PATH).replace('.log', '.txt')


def _show(msg):
    print(msg, file=sys.stderr)
    print(msg, file=_file)


def debug(msg, src='main'):
    text = _get(msg, src, 'DEBUG')
    _show(text)


def info(msg, src='main'):
    text = _get(msg, src, 'INFO')
    _show(text)


def warn(msg, src='main'):
    text = _get(msg, src, 'WARN')
    _show(text)


def error(msg, src='main'):
    text = _get(msg, src, 'ERROR')
    _show(text)


def critical(msg, src='main'):
    text = _get(msg, src, 'CRITICAL')
    _show(text)


def fatal(msg, src='main'):
    text = _get(msg, src, 'FATAL')
    _show(text)
    do_error(msg, src)
    sys.exit(msg)


def fatal_with_no_quit(msg, src='main'):
    text = _get(msg, src, 'FATAL')
    _show(text)
    do_error(msg, src)


def do_error(msg, src):
    with open(_get_crash(), 'w') as f:
        f.write(msg)
        import traceback
        traceback.print_exc()
        traceback.print_exc(file=f)


def chat(msg, player):
    fmsg = '[{2}] [client/CHAT] <{1}> {0}'.format(msg, player, gettime())
    _show(fmsg)
