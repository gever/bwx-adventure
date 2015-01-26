#!/usr/bin/python

#
# Tutorial 7 shows how to introduce mortality your game.
#

from advent import *
from advent_devtools import *


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

cat = Pet("cat")
cat.set_location(sidewalk)

player = game.new_player(sidewalk)

#
# Lets put a deadly object in the office:
# The object is a Drink and the arguments we pass to Drink() are:
#   - name of the object "vial"
#   - description of the object "a small vial of..."
#   - a verb to perform when the Drink is consumed, we use the Die() verb
#     which kills any actor that performs it, after printing out the text
#     provided to Die()
#   - an Object() to replace the vial after it is consumed, "empty vial"
#
# Try the following commands in this tutorial:
# > drink vial
# you will need to restart the game now :)
# > look
# > tell cat drink vial
# > look
# 
sidewalk.add_object(Drink("vial",
                          "a small vial of dark sinister looking liquid",
                          Die("choking violently and collapsing onto the floor..."),
                          Object("empty vial", "an empty vial with an acrid odor")))

            
# add our player to the game
game.add_actor(player)

# and let's add a test to check the code we wrote above:
test_script = Script("test",
"""
> look
> take vial
> give cat vial
> tell cat drink vial
> look
> end
""")
player.add_script(test_script)

game.run()
