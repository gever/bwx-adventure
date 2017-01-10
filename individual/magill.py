#!/user/bin/python
# vim: et sw=2 ts=2 sts=2
#
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from bwx_adventure.advent import *
from bwx_adventure.advent import Game, Location, Connection, Object, Animal, Robot, Pet, Player
from bwx_adventure.advent import NORTH, SOUTH, EAST, WEST, UP, DOWN, RIGHT, LEFT, IN, OUT, FORWARD, BACK, NORTH_WEST, NORTH_EAST, SOUTH_WEST, SOUTH_EAST, NOT_DIRECTION

game = Game("blizard")

inside_the_house = game.new_location(
  "in the house",
  "ill be safe and warm in here! The door is to the east")

outside_the_house = game.new_location(
  "outside the house",
"""it is fine right here but the blizard lay to the west.""")
  
in_the_middle_of_the_blizard = game.new_location(
  "in the middle of the blizard",
"""its super cold out here I think i might freaze to death.""")
  
game.new_connection("Glass door", inside_the_house, outside_the_house, [IN, EAST], [OUT, WEST])

game.new_connection("Glass door", outside_the_house, in_the_middle_of_the_blizard, [IN, EAST], [OUT, WEST])
player = game.new_player(inside_the_house)

game.run()
