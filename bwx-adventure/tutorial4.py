#!/usr/bin/python

#
# Tutorial 4 shows how to add Food and Drink to your game.
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
"""A nicely organized office."
There is a door to the north.""")

game.new_connection("Glass Door", sidewalk, vestibule, [IN, EAST], [OUT, WEST])
game.new_connection("Office Door", vestibule, office, [IN, SOUTH], [OUT, NORTH])

key = sidewalk.new_object("key", "a small tarnished key")

player = game.new_player(sidewalk)

#
# We have a special class of Object called "Food" that lets you easily create
# things that can be eaten.
#   - the first argument is the name of the object containing or holding the food
#   - the second argument is a description of the food
#   - the third argument is any kind of Verb that you want to execute
#     when the food is consumed
# Try using the "eat" command on the donut created below.
# Try using the eat command a second time and see what happens.
#
office.add_object(Food("donut",
                       "a chocolate covered donut with pink sprinkles",
                       Say("yummy!")))

#
# In the example above, there was nothing left behind when the donut was eaten,
# let's fill in an optional fourth argument to describe something that is left behind
# after the food is eaten, in this case a plate, a greenish greasy plate:
#
office.add_object(Food("plate of food",
                       "a plate of green eggs and ham",
                       Say("You like them!"),
                       Object("plate", "a greenish greasy plate")))

#
# Drink is another special class just like Food, but for things you can drink.
#                                               
office.add_object(Drink("glass of water",
                        "a glass of water, half full",
                        Say("You feel refreshed, and strangely optimistic."),
                        Object("glass", "an empty glass")))


# and let's add a test to check the code we wrote above:
test_script = Script("test",
"""
> in
> s
> eat donut
> eat donut
> examine plate of food
> examine glass of water
> drink plate of food
> eat plate of food
> eat plate of food
> examine plate
> drink glass of water
> examine glass
> drink glass
> end
""")
player.add_script(test_script)

game.run()

