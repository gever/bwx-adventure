#!/usr/bin/python
# vim: et sw=2 ts=2 sts=2

from advent import *
# for cloud9
from advent import Game, Location, Connection, Object, Animal, Robot, Pet, Player, Verb, Say, SayOnNoun, SayOnSelf
from advent import NORTH, SOUTH, EAST, WEST, UP, DOWN, RIGHT, LEFT, IN, OUT, FORWARD, BACK, NORTH_WEST, NORTH_EAST, SOUTH_WEST, SOUTH_EAST, NOT_DIRECTION

# comment this line out to skip the devtools for environments like trinket
import advent_devtools

# Set up the game you are going to build on.
# my_game is a top-level container for everything in the game.
game = Game("Brightworks Adventure")

# Create some interesting locations. Locations need a name
# and a description of any doorways or connections to the room, like this:
# variable_name = Location('The Name", "The description")
# The triple quotes (""") below are a way to make multi-line strings in Python.
# The final argument is which word to use in the location title in place of "in"
# in the phrase "You are in the..."
sidewalk = Location(
"Sidewalk",
"""There is a large glass door to the east.
The sign says 'Come In!'
""", "on")

# Custom messages can contain lists of strings and functions which return strings.
vestibule = Location(
"Vestibule", 
["A small area at the bottom of a flight of stairs.\n",
  game.if_flag('switch_on', "There is a switch next to a lit bulb.\n",
    "There is a switch next to an unlit bulb.\n"),
"Up the stars you see the reception desk."])

# You can also create a function to provide the description.
def reception_description(self):
  return [
      "Behind an opening in the wall you see ",
      game.if_flag("switch_on", "a lit", "an unlit", vestibule),
""" room.
You see a score board and a message box with a needle for messages.
There is a locked sliding door to the south, and an intersection to the north."""]

reception = Location("Reception Desk", reception_description)

intersection = Location("Intersection",
"""A boring intersection. There is a passageway to the
north that leads to the shop. To the east is the elevator
landing, to the west is the guest lounge, and to the
south is the reception desk. There is nothing to do here.
""", "at")

elevator = Location("Elevator",
"""The elevator is turned off, but the door is open.
The controls on the elevator do not seem to work.
To the west is an intersection.
""")

# "\n" makes a new line in a Python string.
secret_lab = Location("Secret Laboratory", "This place is spooky. It's dark and \nthere are cobwebs everywhere. There must \nbe a light switch somewhere.")

# Let's add the locations to your game.
game.add_location(sidewalk)
game.add_location(vestibule)
game.add_location(reception)
game.add_location(intersection)
game.add_location(elevator)

# You can also add a simple location with the convience function 'new_location'.
# "\n" makes a new line in a Python string.
game.new_location(
"Secret Laboratory", "This place is spooky. It's dark and \nthere are cobwebs everywhere. There must \nbe a light switch somewhere.")

# Create connections between the different places. Each connection
# needs a name, the two locations to connect, and the two directions
# you can go to get in and out of the space.
# example: variable = Connection("The Connection Name", location_a, location_b, direction_a, direction_b)
#
# You can have more than one way of using a connection by combining them in a list.
# In Python, [] brackets make a list.
# example: new_connection = Connection("The Connection Name", location_a, location_b, [direction_a, other_direction_a], [direction_b, other_direction_b])
big_door = Connection("Big Door", sidewalk, vestibule, [IN, WEST], [OUT, EAST])
# You can omit the 2nd direction and it will just be the opposite of the 1st
stairs = Connection("Stairs", vestibule, reception, UP)
steps_to_reception = Connection("A Few Steps", reception, intersection, NORTH)

# Now add the connections to the game too.
game.add_connection(big_door)
game.add_connection(stairs)
game.add_connection(steps_to_reception)

# You can also create and add a connection with a single convenience function that allows
# you to omit the name of the connection.  This is the preferred way to add connections:
game.connect(intersection, elevator, EAST)

# Create some objects to put in your game. You need a name and
# a description for the object you are making.
# example: something = Object("Object Name", "A description for the object")
# If you add True as the last argument, then it's an item that can't be taken.
elev_key = Object("key", "small tarnished brass key")

sidewalk.add_object(elev_key)

pebble = sidewalk.add_object(Object("pebble", "round pebble"))
sidewalk.add_object(Object("Gary the garden gnome",
  "a small figure liberated from a nearby garden."))


# You can make rooms require things, like keys, before a player can enter them.
elevator.make_requirement(elev_key)
elevator.make_requirement(pebble)

# Add a verb applicable at this location.
sidewalk.add_verb(Say('The door makes a hollow sound.', 'knock'))

# "scream" is an example of a custom verb defined by a Python
# function. "def" defines a function in Python.
def scream(self, actor, noun, words):
  all_words = [noun] + words
  print "You hear a scream '%s'." % ' '.join(all_words)
  return True

sidewalk.add_verb(Verb(scream, 'scream'))

# Add an animal to roam around.  Animals act autonomously (on their own).
cat = Animal("cat")
cat.set_location(sidewalk)

# custom verbs available when the cat is present.
# say_on_self triggers when the cat is the noun: e.g. "pet cat"
cat.add_verb(SayOnSelf("The cat purrs.", "pet"))
cat.add_verb(SayOnSelf("Don't do that, PETA will get you!", "eat"));
cat.add_verb(SayOnSelf("The cat escapes and bites you. Ouch!", "kill"));

# say_on_noun triggers when you tell the cat to do something: e.g. "tell cat lick yourself"
cat.add_verb(SayOnNoun("The cat beings to groom itself.", "yourself", "lick"))

# Add a robot.  Robots can take commands to perform actions.
robby = Robot("Robby")
robby.set_location(sidewalk)

# Add a Pet.  Pets are like Animals because they can act autonomously,
# but they also are like Robots in that they can take commands to
# perform actions.
fido = Pet("Fido")
fido.set_location(sidewalk)

# Make the player.
hero = Player()

# Add the actors to the game. Players, animals, robots, and pets are
# all kinds of actors.
game.add_actor(hero)
game.add_actor(cat)
game.add_actor(robby)
game.add_actor(fido)

# add a custom actor verb (in this case for the hero)
def throw(self, actor, noun, words):
  if noun and actor.get_verb('drop').act(actor, noun, words):
     print 'The %s bounces and falls to the floor' % noun
     return True
  else:
     print 'You hurt your arm.'
     return False

hero.add_verb(Verb(throw, 'throw'))

# add a custom object verb
# this works for 'hit pebble' as well as 'hit XXX with pebble'
def useless_hit_with_object(self, actor, noun, words):
  if not noun or noun == self.name:
    self.game.output("Hitting the " + self.name + " was ineffective.")
  else:
    self.game.output("The " + self.name + " bounces off the " + noun + " with no visible effect.")
  return True

pebble.add_verb(Verb(useless_hit_with_object, "hit"))

# Commands are looked up first by the full phrase, then by Verb first on indirect object,
# then object then actor.  This catchall for 'hit' is used if no other handler is found.
hero.add_verb(Say("Such violence is appalling.", "hit"))

# The code starting here is for saving games and data that can be shared.
# Don't worry if this doesn't make sense yet.

# Create unique player and session names for non-logged/saved sessions.
player = 'player' + str(time.time())
session = 'session' + str(time.time())

# Create shared data.
# NOTE: you must either set the server with share.set_host(...) or place the host information
# in a file 'share.info' in the local directory.  The host must be a webdis host using basic
# authentication.  Talk to your collaborator to get this information.
share = Share()
share.set_adventure("bwx-adventure")
share.set_player(player)
share.set_session(session)
share.start()

# custom verb to record things at all locations
# Data can be store
#   GLOBAL: available to everyone
#   ADVENTURE: available to everyone playing a particular adventure
#   PlAYER: available to the specific palyer in the specific adventure
#   SESSION: available to the specific palyer in the specific adventure in the specific session
def scribble(self, actor, noun, words):
  if not noun or words:
    print "You can only scrible a single word."
    return False
  share.put(share.ADVENTURE, 'crumb.' + actor.location.name, noun.strip())
  return True

hero.add_verb(Verb(scribble, 'scribble'))

# custom verb to see things that have been scribbled
def peek(self, actor, noun, words):
  v = share.get(share.ADVENTURE, 'crumb.' + actor.location.name)
  if not v:
    print 'Nothing here.'
    return False
  print 'Someone scribbled "%s" here.' % v
  return True

hero.add_verb(Verb(peek, 'peek'))

# custom verb to count
def more(self, actor, noun, words):
  loc_name = "_".join(actor.location.name.split(' '))
  share.increment(share.ADVENTURE, 'count.' + loc_name)
  print 'The count is %s!' % share.get(share.ADVENTURE, 'count.' + loc_name)
  return True

def fewer(self, actor, noun, words):
  loc_name = "_".join(actor.location.name.split(' '))
  share.decrement(share.ADVENTURE, 'count.' + loc_name)
  print 'The count is %s!' % share.get(share.ADVENTURE, 'count.' + loc_name)
  return True

def reset(self, actor, noun, words):
  loc_name = "_".join(actor.location.name.split(' '))
  share.delete(share.ADVENTURE, 'count.' + loc_name)
  print 'The count is reset!'
  return True

hero.add_verb(Verb(more, 'more'))
hero.add_verb(Verb(fewer, 'fewer'))
hero.add_verb(Verb(reset, 'reset'))

# custom verb to change state of a location
def flip(self, actor, noun, words):
  if (noun and noun != "switch") or words:
    return False
  if self.flag('switch_on'):
    self.unset_flag('switch_on')
  else:
    self.set_flag('switch_on')
  print "You flip the switch."
  return True

vestibule.add_verb(Verb(flip, 'flip'))

# add a custom description to an object
def describe_candle(self):
  if "lit" in self.vars:
    return "a lit candle"
  else:
    return "an unlit candle"

candle = sidewalk.new_object("candle", describe_candle)

# custom verbs to change state of an object
def light(self, actor, noun, words):
  if (noun and noun != "candle") or words:
    return False
  if self.flag('lit'):
    self.game.output("The candle is already lit.")
  else:
    self.set_flag('lit')
    self.game.output("You light the candle.")
  return True

candle.add_verb(Verb(light, "light"))

def blow_out(self, actor, noun, words):
  if (noun and noun != "candle") or words:
    return False
  if not self.flag('lit'):
    self.game.output("The candle is not lit.")
  else:
    self.unset_flag('lit')
    self.game.output("You blow out the candle.")
  return True

candle.add_verb(Verb(blow_out, "blow out"))

# custom verb to push and pop messages
# self is the location since that is where the verb was added
def push(self, actor, noun, words):
  if not noun:
    return False
  if noun != 'message':
    w = "_".join([noun] + words)
  else:
    if not words:
      return False
    w = "_".join(words)
  share.push(share.ADVENTURE, 'reception_messages', w)
  print "You left a message on the stack of messages."
  return True

reception.add_verb(Verb(push, 'push'))

def pop(self, actor, noun, words):
  if (noun and noun != "message") or words:
    return False
  w = share.pop(share.ADVENTURE, 'reception_messages')
  if not w:
    print "There are no messages on the stack."
    return False
  words = w.split('_')
  print "You pull the top message from the stack and read '%s'." % " ".join(words)
  return True

reception.add_verb(Verb(pop, 'pop'))


# custom verb on an object
def rub_key(self, actor, noun, words):
  if noun or words:
    return False
  self.game.output("You rub the key but only succeed in making it more tarnished.")
  return True

elev_key.add_verb(Verb(rub_key, 'rub'))

# high score example.  When the adventurer's score changes use zadd to add/update the score.
share.delete(share.ADVENTURE, 'highscore')
share.zadd(share.ADVENTURE, 'highscore', 'joe', 10)
share.zadd(share.ADVENTURE, 'highscore', 'bob', 20)
share.zadd(share.ADVENTURE, 'highscore', 'fred', 30)

def top(self, actor, noun, words):
  if (noun and noun != "scores") or words:
    return False
  w = share.ztop(share.ADVENTURE, 'highscore', 10)
  if w:
    print "Top Players"
    for x in w:
      print "  %s" % x
  return True

def scores(self, actor, noun, words):
  if (noun and noun != "scoreboard") or words:
    return False
  w = share.ztop_with_scores(share.ADVENTURE, 'highscore', 10)
  if w:
    print "High Scores"
    for x in w:
      print "  %s %s" % (x[0], x[1])
  return True

reception.add_verb(Verb(top, 'top'))
reception.add_verb(Verb(scores, 'scores'))
reception.add_verb(Verb(scores, 'read'))

# Now that we have created our game and everything in it, we can start the game!

# Start on the sidewalk.
hero.set_location(sidewalk)

def update():
  if (game.entering_location(reception)):
    if (game.inventory_contains([pebble])):
      game.output("The pebble you picked up is suddenly feeling warm to the touch!")

# Create a test script to exercise the features we coded above:
test_script = Script("test",
"""
> look
> tell Fido to follow me
> take candle pebble key
> go in
> pet cat
> flip switch
> look
> flip switch
> light candle
> blow out candle
> throw pebble
> take pebble
> look
> go up
> s
> n
> drop key
> e
> take key
> e
> w
> look
> w
> n
> s
> d
> out
> knock
> scream foo
> look
> end
""")

# Then add the script to a player, or a robot
# with code like the following:
hero.add_script(test_script)

# Now you can run this script from within the game as the hero
# by typing "run test"
      
# Start playing.
game.run(update)
