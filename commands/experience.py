if args[0] == 'set':
    amount = int(args[1])
    if args[2] == 'levels':
        player.level = amount
    elif args[2] == 'points':
        player.level_prog = amount/20
    else:
        message('Invalid usage.')
        raise Exception
elif args[0] == 'add':
    amount = int(args[1])
    if args[2] == 'levels':
        player.level += amount
    elif args[2] == 'points':
        player.level_prog += amount/20
    else:
        message('Invalid usage.')
        raise Exception
else:
    message('Invalid usage.')
    raise Exception
message('Succesfully gave ' + str(args[1]) + ' experience ' + args[2] + ' to ' + game.pname + '.')
