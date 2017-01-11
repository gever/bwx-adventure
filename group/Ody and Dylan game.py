#!/user/bin/python
# vim: et sw=2 ts=2 sts=2
#
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from bwx_adventure.advent import *
from bwx_adventure.advent import Game, Location, Connection, Object, Animal, Robot, Pet, Player
from bwx_adventure.advent import NORTH, SOUTH, EAST, WEST, UP, DOWN, RIGHT, LEFT, IN, OUT, FORWARD, BACK, NORTH_WEST, NORTH_EAST, SOUTH_WEST, SOUTH_EAST, NOT_DIRECTION

game = Game("Shadows")

dungeon = game.new_location(
  "Dark Dungeon Cell",
  "There is a guard just outside your cell with a key chain and a dwarven dagger.")

corridor = game.new_location(
  "Corridor",
"""You are in long corridor, there is a large wooden door to the west.""")

game.new_connection("Glass Door", dungeon, vestibule, [IN, EAST], [OUT, WEST])

player = game.new_player(dungeon)

guard = Animal("guard")
guard.set_location(dungeon)
guard.set_allowed_locations([dungeon])



key_chain = Object("key chain", "a rusty ring of old keys")
dagger = Object("dwarven dagger", "a polished dwarven dagger")
guard.add_to_inventory(key_chain)
guard.add_to_inventory(dagger)                

sharp_bone = dungeon.new_object("sharp bone", "a sharp bone lies in the corner to the left of you")

def kill_guard(game, thing):
  if not "sharp_bone" in game.player.inventory:
    game.output("You try to attack the guard with your bare hands, but he wacks you with the bunt of his blade.")
    player.terminate()
  else:
    game.output("You stab the guard from behind at the base of his neck, and he drops to the ground dead.")

    guard.terminate()
    guard.act_drop1(player,key_chain)
    guard.act_drop1(player,dagger)
 
game.run()

