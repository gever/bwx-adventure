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
cat.set_allowed_locations([sidewalk])

player = game.new_player(sidewalk)

#
# Lets put a deadly object on the sidewalk:
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

#
# Now lets add an unbeatable foe, better to just to leave this guy alone!
#
# We use the add_phrase() method to link the Die verb to the phrase "wake bear".
# Now any actor that utters that phrase near the bear will be killed.
# 
# See what happens if you do:
# > wake bear
#
bear = Animal("sleeping bear")
bear.set_location(vestibule)
bear.set_allowed_locations([vestibule])
game.add_actor(bear)
bear.add_phrase("wake bear",
                Die("mauled viciously by the angry bear who then falls back asleep."))  

#
# Let's try a more complex example now that involves fighting.
# We create a function, "fight_dragon" that checks if we have the shield or not.
# If we do have the shield then we can kill the dragon, if not he will kill us.
# The fight_dragon() function uses the Actor.terminate() method to kill whichever
# actor loses the battle.
# We use add_phrase to link the phrase "fight dragon" to the fight_dragon function.
# We add the phrase to the dragon so that it only works when the dragon is present.
#
dragon = Actor("tiny dragon")
dragon.set_location(office)
game.add_actor(dragon)
shield = vestibule.new_object("shield", "a shiny bronze sheild")
sword = office.new_object("sword", "a rusty old sword")
def fight_dragon(game, thing):
  if not "shield" in game.player.inventory:
    game.output("You try to stab the dragon with the sword, but it flames you.")
    player.terminate()
  else:
    game.output("Using the shield to avoid the dragon's flames you kill it with the sword.")
    dragon.terminate()

dragon.add_phrase("fight dragon", fight_dragon)
            
# add our player to the game
game.add_actor(player)

# add the cat to the game
game.add_actor(cat)

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
