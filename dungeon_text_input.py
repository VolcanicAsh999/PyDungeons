import pygame
import string
import types
import os

# a library that is packaged with PygameGUI, copied to the PyDungeons project


def gettextinput(pos: tuple[int], screen: pygame.Surface, color: pygame.Color = pygame.Color('black'), accepttext: str = string.printable, fontname: str = 'default', fontsize: int = 20, whilerunfunc: tuple = ('function', 'args'), other_text: str = '> ', fillcolor: pygame.Color = None, doupdate=True, quitonesc=True, passtext=False, passevents=True):
    if os.path.exists(os.path.join(os.getcwd(), fontname)):
        font_obj = pygame.font.Font(
            os.path.join(os.getcwd(), fontname), fontsize)
    elif os.path.exists(fontname):
        font_obj = pygame.font.Font(fontname, fontsize)
    elif fontname != 'default':
        try:
            font_obj = pygame.font.SysFont(fontname, fontsize)
        except:
            font_obj = pygame.font.SysFont('Sans Mono', fontsize)
    else:
        font_obj = pygame.font.SysFont('Sans Mono', fontsize)
    run = True
    if (whilerunfunc == ('function', 'args')) or (type(whilerunfunc[0]) not in [types.FunctionType, types.BuiltinFunctionType, types.MethodType, types.BuiltinMethodType]) or (type(whilerunfunc[1]) not in [tuple, list, set]):
        whilerunfunc = (lambda *args: ..., ())
    text = ''
    while run:
        events = pygame.event.get()
        if fillcolor != None:
            screen.fill(fillcolor)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    if len(text) > 0:
                        text = text[:-1]
                elif event.key == pygame.K_RETURN:
                    return text
                elif event.key == pygame.K_SPACE:
                    text += ' '
                elif event.key == pygame.K_ESCAPE and quitonesc:
                    return ''
                else:
                    if hasattr(event, 'unicode') and event.unicode and event.unicode in accepttext:
                        text += event.unicode
        if passtext:
            if passevents:
                whilerunfunc[0](*whilerunfunc[1], events,
                                font_obj.render(other_text + text, 1, color), pos)
            else:
                whilerunfunc[0](
                    *whilerunfunc[1], font_obj.render(other_text + text, 1, color), pos)
        else:
            if passevents:
                whilerunfunc[0](*whilerunfunc[1], events)
                screen.blit(font_obj.render(other_text + text, 1, color), pos)
            else:
                whilerunfunc[0](*whilerunfunc[1])
                screen.blit(font_obj.render(other_text + text, 1, color), pos)
        if doupdate:
            pygame.display.update()


def getnuminput(*args, **kwargs):
    kwargs.update({'accepttext': string.digits})
    return gettextinput(*args, **kwargs)
