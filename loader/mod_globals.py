import sys, os; sys.path.append(os.path.dirname(__file__))
import dungeon_enemies, dungeon_weapons, dungeon_arrows, dungeon_chests

Sword = dungeon_weapons.Sword
Axe = dungeon_weapons.Axe
Scythe = dungeon_weapons.Scythe
Knife = dungeon_weapons.Knife
Mallet = dungeon_weapons.Mallet
Fist = dungeon_weapons.Fist

Consumable = dungeon_weapons.Consumable
Artifact = dungeon_weapons.Artifact
BaseArmor = dungeon_weapons.BaseArmor

Crossbow = dungeon_weapons.Crossbow
Bow = dungeon_weapons.Bow

Enemy = dungeon_enemies.BaseEnemy

Arrow = dungeon_arrows.Arrow

Chest = dungeon_chests.Chest

del sys, os, dungeon_enemies, dungeon_weapons, dungeon_arrows, dungeon_chests
