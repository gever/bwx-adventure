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



"in grocery store",
"A small area at the bottom of a flight of stairs.
"There is a glass door to the west.'"")



  
("There is a large glass door to the east. A sign_says_Come_In!")

outside_grocery_store = game.new_location(
  "outside grocery store",
  "There is a large glass door to the east. The sign says 'Come In!'")
in_grocery_store = game.new_location(
  
  
"""outside a deserted grocery store.""")



game.new_connection("Glass Door", in_grocery_store, outside_grocery_store, [IN, EAST], [OUT, WEST])

player = game.new_player(in_grocery_store)

game.run()
