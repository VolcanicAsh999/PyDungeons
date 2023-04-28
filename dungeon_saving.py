import dungeon_weapons as dw
import dungeon_arrows as da
import dungeon_enemies as de
import dungeon_chests as dc
import dungeon_walls as dwa
import dungeon_misc as dm
import dungeon_helpful as dh
import json
import os

data = {'spawners': {de.ZombieSpawner: 1, de.SkeletonSpawner: 2, de.SpiderSpawner: 3, de.CreeperSpawner: 4}, 'other': {dm.EmeraldPot: 1, dm.EvokerSpikes: 2, dm.TNT: 3, dm.ThrownPotion: 4, dm.PoisonCloud: 5, dm.GeomancerColumn: 6, dm.WraithFlames: 7, dm.IceBlock: 8}, 'helpfuls': {dh.Golem: 1, dh.Wolf: 2, dh.Bat: 3}, 'chests': {dc.WeaponChest: 1, dc.ConsumableChest: 2, dc.EmeraldChest: 3, dc.ObsidianChest: 4, dc.SupplyChest: 5, dc.SilverChest: 6, dc.ArmorChest: 7, dc.PlayerLootChest: 8, dc.InventoryChest: 9}, 'arrows': {da.Arrow: 1, da.SlowArrow: 2, da.PoisonArrow: 3, da.FlamingArrow: 4, da.ExplodingArrow: 5, da.ImplodingArrow: 6, da.SpeedWhenHurtArrow: 7, dm.ThrowingPotion: 8, da.Bolt: 9, dm.ConjuredProjectile: 10}, 'enemies': {de.Zombie: 1,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 de.Husk: 2, de.Drowned: 3, de.PlantZombie: 4, de.SpeedyZombie: 5, de.Necromancer: 6, de.Slime: 7, de.Skeleton: 8, de.Stray: 9, de.MossSkeleton: 10, de.FlamingSkeleton: 11, de.Pillager: 12, de.Vindicator: 13, de.Evoker: 14, de.Vex: 15, de.Creeper: 16, de.Spider: 17, de.Enchanter: 18, de.Geomancer: 19, de.RoyalGuard: 20, de.ArmoredZombie: 21, de.BabyZombie: 22, de.ChickenJockey: 23, de.ChickenJockeyTower: 24, de.CaveSpider: 25, de.Witch: 26, de.SkeletonHorse: 27, de.SkeletonHorseman: 28, de.Enderman: 29, de.Wraith: 30, de.SkeletonVanguard: 31, de.NamelessOne: 32, de.RedstoneGolem: 33, de.RedstoneMonstrosity: 34, de.RedstoneCube: 35, de.ConjuredSlime: 36, de.TheCauldron: 37, de.Iceologer: 38, de.Piglin: 39, de.PiglinSword: 40, de.PiglinBrute: 41}}
data2 = {c: {a: b for b, a in data[c].items()} for c in data.keys()}

path = os.path.join(os.environ.get('APPDATA'), '.pydungeons', 'saves')
if not os.path.exists(path):
    os.makedirs(path)


def reload():
    global data, data2
    data2 = {c: {a: b for b, a in data[c].items()} for c in data.keys()}


def nextChest():
    return len(data['chests'].keys()) + 1


def nextArrow():
    return len(data['arrows'].keys()) + 1


def nextEnemy():
    return len(data['enemies'].keys()) + 1


def nextHelpful():
    return len(data['helpfuls'].keys()) + 1


def nextOther():
    return len(data['other'].keys()) + 1


def nextSpawner():
    return len(data['spawners'].keys()) + 1


def remdups(l):  # helper function
    l2 = []
    for i in l:
        if i in l2:
            continue
        l2.append(i)
    return l2


def listworlds():
    return [file for file in os.listdir(path) if file.endswith('.json')]


def listworldnames():
    ret = []
    for file in os.listdir(path):
        with open(os.path.join(path, file)) as f:
            data = json.loads(f.read())
        ret.append(data['Name'])
    return ret


def worlddata(name):
    worlds = listworlds()
    ret = None
    for world in worlds:
        world_ = open(os.path.join(path, world))
        data = json.loads(world_.read())
        if data['Name'] == name:
            ret = world
        world_.close()
    return ret


def worldname(filename):
    worlds = listworlds()
    ret = None
    if not filename.endswith('.json'):
        filename += '.json'
    for world in worlds:
        if world.lower() == filename.lower():
            world_ = open(os.path.join(path, world))
            data = json.loads(world_.read())
            ret = data['Name']
            world_.close()
    return ret


def changename(filename, newname):
    with open(os.path.join(path, filename)) as file:
        data = json.loads(file.read())
    data['Name'] = newname
    with open(os.path.join(path, filename), mode='w') as file:
        json.dump(data, filename)


def save_world(game, name, filename):
    p = game.player
    load_text = {'Player': None,
                 'Enemies': [],
                 'Chests': [],
                 'Arrows': [],
                 'Walls': [],
                 'Helpfuls': [],
                 'Others': [],
                 'Spawners': [],
                 'Name': name,
                 'Version': getattr(game, 'version', '1.0.0')}
    load_text['Player'] = {'x': p.rect.x, 'y': p.rect.y, 'arrows': p.arrows, 'emeralds': p.emeralds,
                           'kills': p.kills, 'has': [], 'level': p.level, 'prog': p.level_prog,
                           'index': [p.indexarmor, p.indexweapon, p.indexrange, p.indexc, p.ia1, p.ia2, p.ia3],
                           'cooldowns': [p.cooldown, p.rcooldown], 'weapons': [], 'ranges': [],
                           'armors': [], 'consumables': [], 'artifacts': [],
                           'effects': p.effects, 'hp': p.hp, 'difficulty': p.difficulty
                           }
    for arrow in game.arrows:
        if type(arrow) == dm.ThrowingPotion:
            load_text['Arrows'] += [{'x': arrow.x, 'y': arrow.y, 'type': 8,
                                     'start': arrow.start, 'finish': arrow.target, 'effect': arrow.effect}]
        elif type(arrow) == dm.ConjuredProjectile:
            load_text['Arrows'] += [{'x': arrow.x, 'y': arrow.y, 'type': 10}]
        else:
            load_text['Arrows'] += [{'x': arrow.x, 'y': arrow.y, 'chain': arrow.ischain, 'damage': arrow.damage, 'knockback': arrow.knockback,
                                     'type': data['arrows'][type(arrow)], 'start': arrow.start, 'finish': arrow.target}]
    for wall in game.walls:
        load_text['Walls'] += [{'x': wall.rect.x, 'y': wall.rect.y}]
    for enemy in game.enemies:
        d = {'x': enemy.rect.x, 'y': enemy.rect.y, 'hp': enemy.hp,
             'effects': enemy.effects, 'type': data['enemies'][type(enemy)]}
        if type(enemy) == de.Slime:
            d['size'] = enemy.size
        load_text['Enemies'] += [d]
    for chest in game.chests:
        load_text['Chests'] += [{'x': chest.rect.x,
                                 'y': chest.rect.y, 'type': data['chests'][type(chest)]}]
    for helpful in game.helpfuls:
        if type(helpful) == dh.Bat:
            continue
        load_text['Helpfuls'] += [{'x': helpful.rect.x, 'y': helpful.rect.y,
                                   'type': data['helpfuls'][type(helpful)], 'hp': helpful.hp, 'effects': helpful.effects}]
    for other in game.other:
        load_text['Others'] += [other.get_save_data()]
        load_text['Others'][-1]['type'] = data['other'][type(other)]
    for spawner in game.spawners:
        load_text['Spawners'] += [{'x': spawner.rect.x, 'y': spawner.rect.y,
                                   'spawndelay': spawner.spawndelay, 'type': data['spawners'][type(spawner)]}]
    for weapon in p.weapons:
        if weapon == None:
            continue
        load_text['Player']['weapons'] += [{'Name': weapon.name, 'bonus': weapon._bonus, 'cooldown': weapon.cooldown, 'num': weapon.num,
                                           'damage': weapon.damage, 'reach': weapon.reach, 'knockback': weapon.knockback, 'spent': weapon._spent,
                                            'speed': weapon._speed, 'enchant': weapon._enchant}]
    for rang in p.ranges:
        if rang == None:
            continue
        load_text['Player']['ranges'] += [{'Name': rang.name, 'bonus': rang._bonus, 'cooldown': rang.cooldown,
                                           'damage': rang.arrow['damage'], 'knockback': rang.arrow['knockback'],
                                           'name': rang.arrow['name'], 'type': data['arrows'][rang.arrow['type']],
                                           'spent': rang._spent, 'enchant': rang._enchant, 'speed': rang._speed,
                                           'num': rang.numshoot, 'stack': rang._amount_chained}]
    for armor in p.armors:
        if armor == None:
            continue
        load_text['Player']['armors'] += [{'Name': armor.name, 'bonus': armor._bonus, 'speed': armor._speed,
                                           'spent': armor._spent, 'enchant': armor._enchant, 'protect': armor.protect}]
    for cons in p.consumables:
        if cons == None:
            continue
        load_text['Player']['consumables'] += [{'Name': cons.name}]
    for art in p.artifacts:
        if art == None:
            continue
        load_text['Player']['artifacts'] += [
            {'Name': art.name, 'cooldown': art.cooldown}]
    for obj in p._has:
        load_text['Player']['has'] += [{'Name': obj.name}]
    load_text['Player']['has'] = remdups(load_text['Player']['has'])

    if not filename.endswith('.json'):
        filename += '.json'

    with open(os.path.join(path, filename), mode='w') as file:
        json.dump(load_text, file)


def load_world(game, filename):
    if not filename.endswith('.json'):
        filename += '.json'
    if not os.path.exists(os.path.join(path, filename)):
        return
    p = game.player
    with open(os.path.join(path, filename)) as file:
        load_text = json.loads(file.read())
    game.version = load_text['Version'] if 'Version' in load_text.keys(
    ) else '1.0.0'
    pd = load_text['Player']
    p.rect.x, p.rect.y = pd['x'], pd['y']
    p.arrows, p.emeralds, p.kills = pd['arrows'], pd['emeralds'], pd['kills']
    p.level, p.level_prog = pd['level'], pd['prog']
    p.indexarmor, p.indexweapon, p.indexrange, p.indexc, p.ia1, p.ia2, p.ia3 = pd['index']
    p.cooldown, p.rcooldown = pd['cooldowns']
    for obj in pd['has']:
        item = None
        for thing in dw.wloot['common'] + dw.wloot['uncommon'] + dw.wloot['rare'] + dw.wloot['epic'] + dw.wloot['legendary'] + dw.sloot:
            if (type(thing) != str) and thing.name == obj['Name']:
                p._has.append(thing)
    for cons in pd['consumables']:
        if cons == None:
            continue
        item = None
        for thing in dw.cloot:
            if (type(thing) != str) and thing.name == cons['Name']:
                item = type(thing)()
                break
        p.consumables.append(item)
    for art in pd['artifacts']:
        if art == None:
            continue
        item = None
        for thing in dw.aloot:
            if thing.name == art['Name']:
                item = type(thing)()
                break
        item.cooldown = art['cooldown']
        p.artifacts.append(item)
    for armor in pd['armors']:
        if armor == None:
            continue
        item = None
        for thing in dw.arloot['common'] + dw.arloot['uncommon'] + dw.arloot['rare']:
            if thing.name == armor['Name']:
                item = type(thing)()
                break
        item._bonus = armor['bonus']
        item._spent, item._enchant = armor['spent'], armor['enchant']
        item._speed = armor['speed']
        item.protect = armor['protect']
        item.update_descript()
        p.armors.append(item)
    for rang in pd['ranges']:
        if rang == None:
            continue
        item = None
        for thing in dw.wloot['common'] + dw.wloot['uncommon'] + dw.wloot['rare'] + dw.wloot['epic'] + dw.wloot['legendary']:
            if thing.name == rang['Name']:
                item = type(thing)()
                break
        item._bonus = rang['bonus']
        item.cooldown, item.arrow['damage'], item.arrow['knockback'], item.arrow['type'], item.arrow[
            'name'] = rang['cooldown'], rang['damage'], rang['knockback'], data2['arrows'][rang['type']], rang['name']
        item._spent, item._enchant = rang['spent'], rang['enchant']
        item._speed = rang['speed']
        item.numshoot = rang['num']
        item._amount_chained = rang['stack'] if 'stack' in rang else 0
        item.update_descript()
        p.ranges.append(item)
    for weapon in pd['weapons']:
        if weapon == None:
            continue
        item = None
        for thing in dw.wloot['common'] + dw.wloot['uncommon'] + dw.wloot['rare'] + dw.wloot['epic'] + dw.wloot['legendary']:
            if thing.name == weapon['Name']:
                item = type(thing)()
                break
        item._bonus = weapon['bonus']
        item.cooldown, item.num, item.damage, item.reach, item.knockback = weapon[
            'cooldown'], weapon['num'], weapon['damage'], weapon['reach'], weapon['knockback']
        item._spent, item._enchant = weapon['spent'], weapon['enchant']
        item._speed = weapon['speed']
        item.update_descript()
        p.weapons.append(item)
    p.effects = pd['effects']
    p.hp = pd['hp']
    p.difficulty = pd['difficulty']
    for arrow in load_text['Arrows']:
        if arrow['type'] == 8:
            game.arrows.append(data2['arrows'][8](
                arrow['start'], arrow['finish'], None, arrow['effect']))
            game.arrows[-1].x = arrow['x']
            game.arrows[-1].y = arrow['y']
        elif arrow['type'] == 9:
            game.arrows.append(data2['arrows'][9](
                arrow['start'], arrow['finish'], None))
        elif arrow['type'] == 10:
            game.arrows.append(data2['arrows'][10](arrow['x'], arrow['y']))
        else:
            game.arrows.append(data2['arrows'][arrow['type']](arrow['start'], arrow['finish'], arrow['damage'],
                               arrow['knockback'], de.HitBox(arrow['start'][0], arrow['start'][1]), chain=arrow['chain']))
            game.arrows[-1].x = arrow['x']
            game.arrows[-1].y = arrow['y']
    for enemy in load_text['Enemies']:
        enem = data2['enemies'][enemy['type']](enemy['x'], enemy['y'])
        enem.hp = enemy['hp']
        enem.effects = enemy['effects']
        if type(enem) == de.Slime and 'size' in enemy:
            enem.size = enemy['size']
        game.enemies.append(enem)
    for chest in load_text['Chests']:
        ches = data2['chests'][chest['type']](chest['x'], chest['y'])
        game.chests.append(ches)
    for helpful in load_text['Helpfuls']:
        helpfu = data2['helpfuls'][helpful['type']](helpful['x'], helpful['y'])
        helpfu.hp = helpful['hp']
        helpfu.effects.update(helpful['effects'])
        game.helpfuls.append(helpfu)
    for other in load_text['Others']:
        othe = data2['other'][other['type']](other['x'], other['y'], other)
        game.other.append(othe)
    for spawner in load_text['Spawners']:
        spawne = data2['spawners'][spawner['type']](spawner['x'], spawner['y'])
        spawne.spawndelay = spawner['spawndelay']
        game.spawners.append(spawne)
    walls = dwa.genfromlist(
        load_text['Walls'] if 'Walls' in load_text.keys() else [])
    game.walls = walls
    p.nextweapon(amount=0)
    p.nextrange(amount=0)
    p.nextarmor(game, amount=0)
    p.nextc(amount=0)
    p.na(1, amount=0)
    p.na(2, amount=0)
    p.na(3, amount=0)
    return load_text['Name']
