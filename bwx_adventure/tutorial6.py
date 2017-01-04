#!/usr/bin/python

#
# Tutorial 6 shows how to trade objects between characters in your game.
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

player = game.new_player(sidewalk)

monkey = Animal("monkey")
monkey.set_location(sidewalk)
monkey.set_allowed_locations([sidewalk])

#
# create an object (a set of keys) and add it to the monkey's inventory
#
keys = Object("keys", "a rusty old ring of skeleton keys")
monkey.add_to_inventory(keys)

#
# create an object that the monkey will trade the keys for (a banana),
# and put it on the sidewalk
#
banana = Food("banana", "a nice ripe banana",
              Say("mmmmm, banana!"),
              Object("banana peel", "a very slippery banana peel"))
sidewalk.add_object(banana)

#
# we use the add_trade() method to set up an actor to trade one item for another
# The first argument is the thing that we give to the actor.
# The second argument is the thing that the actor gives back (it can be None)
# The third argument is a verb to execute when the trade happens
#
monkey.add_trade(banana, keys,
                 Say("The monkey takes the banana and drops a set of keys"))
#
# let's also set up a trade in the reverse direction, so we can trade back
# and forth with the monkey
#
monkey.add_trade(keys, banana,
                 Say("The monkey takes the keys and drops a banana"))


# add our players to the game
game.add_actor(player)
game.add_actor(monkey)

# and let's add a test to check the code we wrote above:
test_script = Script("test",
"""
> give monkey banana
> take keys
> i
> give monkey keys
> i
> look
> eat banana
> look
> give monkey banana
> end
""")
player.add_script(test_script)

game.run()
