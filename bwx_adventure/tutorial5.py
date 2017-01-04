#!/usr/bin/python

#
# Tutorial 5 shows how to add containers like cabinets to your game.
#

from advent import *

# import advent_devtools for helpers you can use when running locally (not in trinket.io)
import advent_devtools

# import random module for random numbers
import random

# We'll start out with our familiar brightworks entryway:

game = Game("Brightworks Adventure")

sidewalk = game.new_location(
  "Sidewalk",
  "There is a large glass door to the east. The sign says 'Come In!'")

vestibule = game.new_location(
  "Vestibule",
"""A small area at the bottom of a flight of stairs.
There is a glass door to the west and door to the south.""")

office = game.new_location(
  "Office",
"""A nicely organized office.
There is a door to the north.""")

game.new_connection("Glass Door", sidewalk, vestibule, [IN, EAST], [OUT, WEST])
game.new_connection("Office Door", vestibule, office, [IN, SOUTH], [OUT, NORTH])

key = sidewalk.new_object("key", "a small tarnished key")

player = game.new_player(sidewalk)

#
# Containers are objects that can hold other objects inside.
#
file_cabinet = office.add_object(Container("file cabinet",
                                           "a rusty old metal file cabinet"))

#
# Let's put something into the Container
#
file_cabinet.new_object("secret plan",
"""secret plans to convert Brightworks into a
military academy for cyber-warfare specialists""")

#
# Containers can also be locked.  Once they are unlocked they
# can be opened and the objects inside can be examined and taken.
# Locking Containers works the same as locking Locations or
# Connections.  You can use add_requirement([objects]) or can lock
# it explicitly and unlock with a custom verb.
#
file_cabinet.make_requirement(key)

# add our player to the game
game.add_actor(player)

# and let's add a test to check the code we wrote above:
test_script = Script("test",
"""
> go in
> s
> look
> open file cabinet
> n
> out
> take key
> in
> s
> examine file cabinet
> open file cabinet
> examine file cabinet
> examine secret plan
> take secret plan
> inventory
> look
> end
""")
player.add_script(test_script)

game.run()
