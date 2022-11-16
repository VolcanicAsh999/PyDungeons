name = ''.join(args)
if args[-1] == 'reversed':
    name = ''.join(args[:-1])
    for i in [player.weapons[0]] + player.weapons[-1:0:-1]: #get a reversed list
        if i == None: continue
        if i.name.lower() == name.lower():
            player.weapons.remove(i)
            player.nextweapon(amount=0)
            break
    
else:
    for i in player.weapons:
        if i == None: continue
        if i.name.lower() == name.lower():
            player.weapons.remove(i)
            player.nextweapon(amount=0)
            break
message('Item taken - ' + i.name)
