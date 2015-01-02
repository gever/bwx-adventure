#! /usr/bin/python
# vim: et sw=2 ts=2 sts=2
from advent import *
# for cloud9...
from advent import Game, World, Location, Connection, Thing, Animal, Robot, Pet, Hero
from advent import NORTH, SOUTH, EAST, WEST, UP, DOWN, RIGHT, LEFT, IN, OUT, FORWARD, BACK, NORTH_WEST, NORTH_EAST, SOUTH_WEST, SOUTH_EAST, NOT_DIRECTION

# setup the game you are going to build on...
# global singleton used as a top level container for collecting game info and state
my_game = Game("Brightworks Adventure")

# create your world, then we can stick stuff in it
my_world = World()

# create some interesting locations. Locations need a name, 
# and a description of any doorways or connections to the room, like this:
# variable_name = Location('The Name", "The description")
sidewalk = Location(
"Sidewalk", """
There is a large glass door to the east.
The sign says 'Come In!'
""" )

vestibule = Location(
"Vestibule", """
A small area at the bottom of a flight of stairs.
Up the stars you see the reception desk.
""" )

reception = Location( "Reception Desk",
"""Behind an opening in the wall you see an unlit room.
There is a locked sliding door to the south, and an intersection to the north.
""" )

intersection = Location( "Intersection",
"""A boring intersection. There is a passageway to the
north that leads to the shop. To the east is the elevator
landing, to the west is the guest lounge, and to the
south is the reception desk. There is nothing to do here.
""" )

elevator = Location( "Elevator",
"""The elevator is turned off, but the door is open.
The controls on the elevator do not seem to work.
To the west is an intersection.
""" )

secret_lab = Location("Secret Labratory", "This place is spooky. It's dark and \nthere are cobwebs everywhere. There must \nbe a lightswitch somewhere.")

# let's add the locations to your world
my_world.add_location(sidewalk)
my_world.add_location(vestibule)
my_world.add_location(reception)
my_world.add_location(intersection)
my_world.add_location(elevator)
my_world.add_location(secret_lab)


# create connections between the different places. each connection needs 
# a name, the two locations to connect, and the two directions you can go to get into and out of the space
# like this: variable = Connection("The Connection Name", location_a, location_b, direction_a, direction_b)
# you can have more than one way of using a connection by combining them in an array
# like this: new_connection = Connection("The Connection Name", location_a, location_b, [direction_a, other_direction_a], [direction_b, other_direction_b])
big_door = Connection("Big Door", sidewalk, vestibule, [IN, EAST], [WEST, OUT])
stairs = Connection("Stairs", vestibule, reception, UP, DOWN)
steps_to_reception = Connection("A Few Steps", reception, intersection, NORTH, SOUTH)
steps_to_elevator = Connection("A Few Steps", intersection, elevator, EAST, WEST)

# now add the connections to the world too
my_world.add_connection(big_door)
my_world.add_connection(stairs)
my_world.add_connection(steps_to_reception)
my_world.add_connection(steps_to_elevator)


# create some things to put in your world. You need a name and 
# a description for the thing you are making
# something = Thing("Think Name", "A description for the thing")
# if you add True as the last argument, then its an item that cant be taken
elev_key = Thing( "key", "small tarnished brass key" )

sidewalk.put( elev_key )

pebble = sidewalk.put( Thing( "pebble", "round pebble" ) )
sidewalk.put( Thing( "Gary the garden gnome",
                          "a small figure liberated from a nearby garden." ) )
                          


# you can make rooms require things, like keys, before a player can enter them
elevator.add_requirement(elev_key)
elevator.add_requirement(pebble)

# simple verb applicable at this location
sidewalk.add_verb( 'knock', my_game.say('The door makes a hollow sound.') )

# custom single location verb
def scream( location, words ):
  print "You scream your head off!"
  for w in words[1:]:
    print "You scream '%s'." % w
  return True

sidewalk.add_verb( 'scream', scream )

# Add an animal to roam around.  Animals act autonomously
cat = Animal("cat")
cat.set_location(sidewalk)
cat.add_verb("pet", my_game.say("The cat purrs.") )
cat.add_verb("eat", my_game.say_on_noun("cat", "Don't do that, PETA will get you!"));
cat.add_verb("kill", my_game.say_on_noun("cat", "The cat escapes and bites you. Ouch!"));

# Add a robot.  Robots can take commands to perform actions.
robby = Robot( "Robby" )
robby.set_location( sidewalk )

# Add a Pet.  Pets are like Animals because they can act autonomously,
# but they also are like Robots in that they can take commands to
# perform actions.
fido = Pet ( "Fido")
fido.set_location( sidewalk )

# make the player
hero = Hero()

my_world.add_actor(hero)
my_world.add_actor(cat)
my_world.add_actor(robby)
my_world.add_actor(fido)

# add a hero verb
def throw( self, actor, words ):
  if len(words) > 1 and self.act('drop', words[1] ):
     print 'The %s bounces and falls to the floor' % words[1]
     return True
  else:
     print 'You hurt your arm.'
     return False

hero.add_verb( "throw", throw )


# create unique player and session names for non-logged/saved sessions
player = 'player' + str(time.clock)
session = 'session' + str(time.clock)

# create shared data
# NOTE: you must either set the server with share.set_host(...) or place the host information
# in a file 'share.info' in the local directory.  The host must be a webdis host using basic
# authentication.
share = Share()
share.set_adventure("bwx-adventure")
share.set_player(player)
share.set_session(session)
share.start()

# custom verb to record things at locations
# Data can be store
#   GLOBAL: available to everyone
#   ADVENTURE: available to everyone playing a particular adventure
#   PlAYER: available to the specific palyer in the specific adventure
#   SESSION: available to the specific palyer in the specific adventure in the specific session
def scribble( self, actor, words ):
  if len(words) != 2:
    print "You can only scrible a single word."
    return False
  share.put(share.ADVENTURE, 'crumb.' + self.location.name, words[1].strip())
  return True

hero.add_verb( "scribble", scribble )

# custom verb to see things written
def peek( self, actor, words ):
  v = share.get(share.ADVENTURE, 'crumb.' + self.location.name)
  if not v:
    print 'Nothing here.'
    return False
  print 'Someone scribbled "%s" here.' % v
  return True

hero.add_verb( "peek", peek )

#  custom verb to count
def more( self, actor, words ):
  share.increment(share.ADVENTURE, 'count.' + self.location.name)
  print 'The count is %s!' % share.get(share.ADVENTURE, 'count.' + self.location.name)
  return True

def fewer( self, actor, words ):
  share.decrement(share.ADVENTURE, 'count.' + self.location.name)
  print 'The count is %s!' % share.get(share.ADVENTURE, 'count.' + self.location.name)
  return True

def reset( self, actor, words ):
  share.delete(share.ADVENTURE, 'count.' + self.location.name)
  print 'The count is reset!'
  return True

hero.add_verb( "more", more )
hero.add_verb( "fewer", fewer )
hero.add_verb( "reset", reset )

# custom verb to push and pop messages

def push( self, actor, words ):
  w = "_".join(words[1:])
  share.push(share.ADVENTURE, 'stack.' + self.location.name, w)
  print "You left a message on the stack of messages."
  return True

hero.add_verb( "push", push )

def pop( self, actor, words ):
  w = share.pop(share.ADVENTURE, 'stack.' + self.location.name)
  if not w:
    print "There are no messages on the stack."
    return False
  words = w.split('_')
  print "You pull the top message from the stack and read '%s'." % " ".join(words)
  return True

hero.add_verb( "pop", pop )

# high score example

share.delete(share.ADVENTURE, 'highscore')
share.zadd(share.ADVENTURE, 'highscore', 'joe', 10)
share.zadd(share.ADVENTURE, 'highscore', 'bob', 20)
share.zadd(share.ADVENTURE, 'highscore', 'fred', 30)

def top( self, actor, words ):
  w = share.ztop(share.ADVENTURE, 'highscore', 10)
  if w:
    print "Top Players"
    for x in w:
      print "  %s" % x
  return True

hero.add_verb( "top", top )

def scores( self, actor, words ):
  w = share.ztop_with_scores(share.ADVENTURE, 'highscore', 10)
  if w:
    print "High Scores"
    for x in w:
      print "  %s %s" % (x[0], x[1])
  return True

hero.add_verb( "scores", scores )

# start on the sidewalk
hero.set_location( sidewalk )

def update():
  print "hello"

# start playing
my_game.add_world(my_world)
my_game.run(update)
