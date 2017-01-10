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

forest = game.new_location(
  "Forest",
  "A lush green forest stands before you with tall trees")

up_tree = game.new_location(
  "Up Tree",
"""You are now up a tree and overlooking a big forest and you are in the middle of it""")

river = game.new_location(
  "River",
"""You are next to a river. There is a shovel next to the river""")

shovel = river.new_object("shovel", "a steel shovel")
 
  
game.new_connection("Glass Door", forest, up_tree, [UP], [DOWN])
game.new_connection("Glass Door", forest, river, [EAST], [WEST])
player = game.new_player(forest)

game.run()
