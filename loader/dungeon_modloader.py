import importlib
import os
import sys
import dungeon_weapons, dungeon_enemies, dungeon_arrows, dungeon_chests, mod_globals
import dungeon_init

path = os.path.join(os.environ.get('APPDATA'), '.pydungeons', 'mods')
if not os.path.exists(path):
    os.makedirs(path)

def initmods(game, globs):
    sys.path.insert(0, path)
    sys.modules['dungeons.mod_globals'] = sys.modules['mod_globals'] = mod_globals
    mods = 0
    mods_names = []
    for name in os.listdir(path):
        module = importlib.import_module(name)
        """for (name, weapon) in module.weapons.weapons:
            setattr(dungeon_weapons, name, weapon)
        for (name, arrow) in module.arrows.arrows:
            setattr(dungeon_arrows, name, arrow)
        for (name, enemy) in module.enemies.enemies:
            setattr(dungeon_enemies, name, enemy)
        for (name, chest) in module.chests.chests:
            setattr(dungeon_chests, name, chest)"""
        globs['saving'] = dungeon_init.init(module, globs)
        mods += 1
        mods_names.append(name)
    if mods > 0:
        print('MODS:')
        for name in mods_names:
            print(name)
        print('-' * 100)
    return globs['saving']

def make_basic(name, overwrite=False):
    name = name.replace(' ', '_').replace(':', '_').replace('-', '_').replace('.', '_').replace('/', '_')
    if os.path.exists(os.path.join(path, name)) and not overwrite: return False
    os.makedirs(os.path.join(path, name), exist_ok=True)
    file = os.path.join(path, name)
    with open(os.path.join(file, '__init__.py'), 'w') as f:
        f.writelines(["import sys; sys.path.insert(0, '%s')\n" % (file.replace('\\', '\\\\')),
                      "import weapons\n",
                      "import arrows\n",
                      "import enemies\n",
                      "import chests\n",
                      "def init(globs):\n",
                      "\t1 # register things, e.g. globs['add_enemy'](enemies.MyEnemy, 'normal'); globs['chests']['mychest'] = chests.MyChest; globs['chests_pool'].extend('mychest', 'mychest', 'mychest'); globs['saving'].data['chests'][globs['saving'].nextChest()] = chests.MyChest\n",
                      "\tglobs['saving'].reload()\n"])
    with open(os.path.join(file, 'weapons.py'), 'w') as f:
        f.writelines(["from dungeons.mod_globals import (\n",
                      "Sword,\n",
                      "Axe,\n",
                      "Mallet,\n",
                      "Knife,\n",
                      "Scythe,\n",
                      "Fist,\n",
                      "Bow,\n",
                      "Crossbow,\n"
                      ")\n\n\n",
                      "weapons = [] # format: (name, weapon object)\n"])
    with open(os.path.join(file, 'arrows.py'), 'w') as f:
        f.writelines(["from dungeons.mod_globals import Arrow\n\n\n",
                      "arrows = [] # format: (name, arrow object)\n"])
    with open(os.path.join(file, 'enemies.py'), 'w') as f:
        f.writelines(["from dungeons.mod_globals import Enemy\n\n\n",
                      "enemies = [] # format: (name, enemy object)\n"])
    with open(os.path.join(file, 'chests.py'), 'w') as f:
        f.writelines(["import dungeon_chests\n\n\n",
                      "chests = [] # list of chests\n",
                      '"""example:\n"""'])
    return True
