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
  "There is a guard to the east with a key chain and a dwarven dagger.")

vestibule = game.new_location(
  "Vestibule",
"""A small area at the bottom of a flight of stairs.
There is a glass door to the west.""")

game.new_connection("Glass Door", dungeon, vestibule, [IN, EAST], [OUT, WEST])

player = game.new_player(dungeon)

sharp_bone = dungeon.new_object("sharp bone", "a sharp bone lies in the corner to the left of you")

game.run()

