#!/user/bin/python
# vim: et sw=2 ts=2 sts=2
#
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from bwx_adventure.advent import *
from bwx_adventure.advent import Game, Location, Connection, Object, Animal, Robot, Pet, Player
from bwx_adventure.advent import NORTH, SOUTH, EAST, WEST, UP, DOWN, RIGHT, LEFT, IN, OUT, FORWARD, BACK, NORTH_WEST, NORTH_EAST, SOUTH_WEST, SOUTH_EAST, NOT_DIRECTION

game = Game("Lucky Day")

sidewalk = game.new_location(
  "Sidewalk",
  "There is a large glass door to the east. The sign says 'Come In!'")

vestibule = game.new_location(
  "Vestibule",
"""A small area at the bottom of a flight of stairs.
There is a glass door to the west. There is a house to the north.""")

game.new_connection("Glass Door", sidewalk, vestibule, [IN, EAST], [OUT, WEST])

player = game.new_player(sidewalk)

house = game.new_location ("House",
                           """You are now in a house. There is a exit to the south. There is a hole in the floor with a ladder leading down.""")

game.new_connection ("Door to house", vestibule, house, [IN, NORTH], [OUT, SOUTH])

cave = game.new_location ("Cave",
                          """You are in a very dark cave. You can not see how to get out. You are stuck.""") 

game.new_connection("hole in floor", house, cave, [DOWN], [NOT_DIRECTION])






game.run()

