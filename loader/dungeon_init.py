import dungeon_saving as saving
import dungeon_chests
import sys

def restart(module):
    """sys.modules[module.__name__] = module
    for name, val in list(sys.modules.items()):
        if hasattr(val, 'saving') and val.saving == module:
            val.saving = module"""
    for name, mod in list(sys.modules.items()):
        if hasattr(module, name):
            module.name = mod

def init(module, globs):
    for chest in module.chests.chests:
        globs['chests'][chest.id] = chest
        globs['chests_pool'].extend([chest.id] * chest.amount)
        saving.data['chests'][chest] = saving.nextChest()
        setattr(dungeon_chests, chest.__name__, chest)
    restart(dungeon_chests)
    saving.reload()
    return saving
