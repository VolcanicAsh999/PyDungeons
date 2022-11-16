name = ''.join(args)
for i in dir(weapons):
    if i.lower() == name.lower():
        player.weapons.append(getattr(weapons, i)())
        break
message('Item given - ' + i)
