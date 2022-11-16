import os
if len(args) == 0:
    for i in os.listdir(os.path.join(os.getcwd(), 'commands')):
        if i.endswith('.py'):
            message('/' + i[:-3])
    for i in os.listdir(settings.SCRIPTS_PATH):
        if i.endswith('.py'):
            message('/' + i[:-3])
else:
    try:
        f = open(os.path.join(os.getcwd(), 'commands', args[0] + '.txt'))
    except OSError:
        try:
            f = open(os.path.join(settings.SCRIPTS_PATH, args[0] + '.txt'))
        except OSError:
            message('No documentation for command/script ' + args[0] + ' found!')
            raise Exception
    data = f.read(-1)
    for line in data.split('\n'):
        message(line)
