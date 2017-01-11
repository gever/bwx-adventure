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

out_of_village = game.new_location(
  "out_of_Village",
  "Out of the village Nothing is happening!'")

village  = game.new_location(
  "Village",
"in the village it is loud ")

house  = game.new_location(
  "house",
"It is dark.")

game.new_connection("Glass Door", out_of_village, village, [IN, EAST], [OUT, WEST])

player = game.new_player(out_of_village)







game.run()
