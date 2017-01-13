#!/usr/bin/python

#
# Tutorial 3 shows how to add Animals, Robots, and Pets to your game.
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

# Now lets add an Animal.  Animals are characters in the game that act
# all on their own.  You can add verbs or phrases to them to make them
# respond to basic commands
bat = Animal("bat")
bat.set_location(office)

# custom verbs available when the bat is present.
# SayOnSelf triggers when the bat is the noun, for example: "swat bat"
bat.add_verb(SayOnSelf("The bat flaps frantically up out of your reach.", "swat"))

# we can also restrict the movement of any actor using set_allowed_locations.
# the following line will prevent the bat from going anywhere besides the
# office and the vestibule:
bat.set_allowed_locations([office, vestibule])

# Now lets add a Robot.  Robots are characters in the game that only
# act when you tell them to.  Robots can do anything the player can do.
# You tell them to act by typing their name, a colon, and the command
# want them to perform.  For example:
# > Robby: take key
# > Robby: go in
# > Robby: look
robby = Robot("Robby")
robby.set_location(sidewalk)

# custom phrases available when Robby is present.
# for example: "hi Robby"
robby.add_phrase("hi Robby",
                 Say("Robby sighs metalically and says, \"hello, my name is Robby.\"."))

# Now lets add a Pet.  Pets are like Animals because they move around
# and do things on their own, but they are also like Robots, because
# you can tell them to do anything a player can do.
# try these commands on the cat:
# > tell cat follow
# > pet cat
# > tell cat bark
# > tell cat stay
cat = Pet("cat")
cat.set_location(sidewalk)

# custom verbs available when the cat is present.
# SayOnSelf triggers when the cat is the noun.
# For example: "pet cat"
cat.add_verb(SayOnSelf("The cat purrs.", "pet"))

# SayOnNoun triggers when you tell the cat to do something: e.g. "tell cat lick yourself
cat.add_verb(SayOnNoun("The cat beings to groom itself.", "yourself", "lick"))

# command the cat and have an object appear
def cat_bark(self, actor, noun, words):
  actor.location.add_object(Object("hairball", "gooey hairball"))
  actor.output("The cat barks and coughs and something splats on the floor.")
  return True
cat.add_verb(Verb(cat_bark, 'bark'))

# custom phrases available when the cat is present.
# for example: "hi cat"
cat.add_phrase("hi cat", Say("The cat looks at you disinterestedly."))

# add all the actors we created above to the game
game.add_actor(player)
game.add_actor(bat)
game.add_actor(robby)
game.add_actor(cat)

# and let's add a test to check the code we wrote above:
test_script = Script("test",
"""
> hi Robby
> go in
> s
> n
> tell cat follow
> hi cat
> pet cat
> tell cat bark
> look
> swat bat
> end
""")
player.add_script(test_script)

game.run()

