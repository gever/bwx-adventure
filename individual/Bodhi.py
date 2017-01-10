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

street = game.new_location(
  "street",
  "There is a large wood door to the east. The sign says 'Come In!'")
cellar = game.new_location(
  "cellar",
"""A small area at the bottom of a flight of stairs.
There is a wood door to the west.""")
Torture_Room = game.new_location(
  "Torture Room",
"""A small area at the bottom of a flight of stairs.
There is a pot of hot water with electric eels swimming in it.""")

game.new_connection(""wood door""),street,cellar, [IN, EAST], [OUT, WEST]

player = game.new_player(street)

game.run()
