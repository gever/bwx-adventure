#!/user/bin/python
# vim: et sw=2 ts=2 sts=2
#
# This is the second tutorial for writing Interactive Fiction with the BWX Adventure Game Engine.
#
from advent import *
# for cloud9
from advent import Game, Location, Connection, Object, Animal, Robot, Pet, Player, Say
from advent import NORTH, SOUTH, EAST, WEST, UP, DOWN, RIGHT, LEFT, IN, OUT, FORWARD, BACK, NORTH_WEST, NORTH_EAST, SOUTH_WEST, SOUTH_EAST, NOT_DIRECTION

# import random module for random numbers
import random

# Let's start with the code from the first tutorial:

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

# Now let's add an inanimate object, a key by providing a single word name and a longer
# description.  We will create the key at the sidewalk

key = sidewalk.new_object("key", "a small tarnished key")

# we can make the key something you have to have to get into the Office
office.make_requirement(key)

# The builtin commands "take", "drop" and "i" or "inventory" will allow the player to
# take the key, drop the key or check if what is in their inventory.

# Let's add a special phrase.  We can attach this phrase to any object, location or actor,
# and the phrase will trigger only if that object or actor is present or at the given location.

key.add_phrase("rub key", game.say("You rub the key, but fail to shine it."))

# This uses the special function game.say, but you can define your own functions.
# Let's create a coin and flip it, resulting in heads or tails:

coin = sidewalk.new_object("coin", "a small coin");

# Functions in python are defined with 'def':

def flip_coin(game):
  if random.random() > 0.5:
    game.output("The coin shows heads.");
  else:
    game.output("The coin shows tails.");

# Phrase functions take a single argument 'game'.   The game argument can be used to access all
# parts of the game, including the player and it can be used to produce output.
# The 'if' statement controls execution of two blocks of code, the true block and the false block.
# After 'if' is an 'expression' which determines which block will run.  In this case the
# expression is random.random() > 0.5 which executes the random() function from the 'random
# module which returns a number betwee 0 and 1 (e.g. 0.523452).  It then compares the result
# to 0.5 (halfway in between) and either outputs a message that the coin shows heads or that it
# shows tails.

# Now we forgot an important part.  This function will run if the coin is present, but we
# want to make sure that the player has picked up the coin first.  Let's add that requirement.
# Normally we would change the above definition, but because this is a tutorial, we will just
# repeat it here with the corrected version (python will just overwrite the old version).

def flip_coin(game):
  if not "coin" in game.player.inventory:
    game.output("The coin is on the ground!")
    return
  if random.random() > 0.5:
    game.output("The coin shows heads.");
  else:
    game.output("The coin shows tails.");

# Note that we need to return after outputting the message "The coin is on the ground",
# otherwise we will continue on to show one the message about heads or tails which wouldn't
# make sense!

# Now let's add the phrase:

player.add_phrase("flip coin", flip_coin, [coin])

# We are adding the phrase to the player, so we call the function player.add_phrase.
# The first argument is the phrase that the user will type, the second argument is our
# flip_coin function.  The last argument is a list (in []) of requirements (other than the
# player) needed for this phrase to trigger.  In this case that is the coin itself. If you
# had, for example, a cauldron and a potion you might have the phrase "add potion to cauldron"
# which would require both the cauldron and the potion to trigger.

# Let's run the game.  See if you can get heads!

game.run()
