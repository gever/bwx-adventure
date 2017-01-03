#!/user/bin/python
# vim: et sw=2 ts=2 sts=2

from advent import *
#from advent import Game, Location, Connection, Object, Animal, Robot, Pet, Player
#from advent import NORTH, SOUTH, EAST, WEST, UP, DOWN, RIGHT, LEFT, IN, OUT, FORWARD, BACK, NORTH_WEST, NORTH_EAST, SOUTH_WEST, SOUTH_EAST, NOT_DIRECTION
game = Game("The Great Willow Wind Text Adventure")

in_front_of_office = game.new_location(
  "In Front of Yellow Building",
    """In front of you stands a bright yellow building which appears to be \
a part of a school.  The front door is wide open.  All you hear is the \
chirping of blackbirds.""")

vestibule = game.new_location(
  "Vestibule",
"""A small area at the bottom of a flight of stairs.
There are seven(!) doors.""")

game.new_connection("Open Office Door", in_front_of_office, vestibule, [IN, NORTH], [OUT, SOUTH])

player = game.new_player(in_front_of_office)

game.run()
