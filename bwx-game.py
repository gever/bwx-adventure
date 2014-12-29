#! /usr/bin/python
# vim: et sw=2 ts=2 sts=2
from advent import *

world = World()
# Sample Game - Brightworks Adventure!
loc_sidewalk = world.add_location(
"Sidewalk", """
There is a large glass door to the east.
The sign says 'Come In!'
""" )

loc_vestibule = world.add_location(
"Vestibule", """
A small area at the bottom of a flight of stairs.
There is an elevator here (currently locked).
Up the stars you see the reception desk.
""" )

loc_reception = world.add_location( "Reception Desk",
"""Behind an opening in the wall you see an unlit room.
There is a locked sliding door to the south, and an intersection to the north.
""" )

loc_intersection = world.add_location( "Intersection",
"""A boring intersection. There is a passageway to the
north that leads to the shop. To the east is the elevator
landing, to the west is the guest lounge, and to the
south is the reception desk. There is nothing to do here.
""" )

loc_elevator = world.add_location( "Elevator",
"""The elevator is turned off, but the door is open.
The controls on the elevator do not seem to work.
To the west is an intersection.
""" )

# the connections between the places
world.biconnect( loc_sidewalk, loc_vestibule, "Big Door", [IN, EAST], [WEST, OUT] )
world.biconnect( loc_vestibule, loc_reception, "Stairs", UP, DOWN )
world.biconnect( loc_reception, loc_intersection, "A Few Steps", NORTH, SOUTH )
world.biconnect( loc_intersection, loc_elevator, "A Few Steps", EAST, WEST )

elev_key = Thing( "key", "small tarnished brass key" )
elev_lock = Thing( "lock", "ordinary lock" )
loc_sidewalk.put( elev_key )
loc_sidewalk.put( elev_lock )
loc_sidewalk.put( Thing( "pebble", "round pebble" ) )
loc_sidewalk.put( Thing( "Gary the garden gnome",
                          "a small figure liberated from a nearby garden." ) )

# simple verb applicable at this location
loc_sidewalk.add_verb( 'knock', say('The door makes a hollow sound.') )

# custom single location verb
def scream( location, words ):
  print "You scream your head off!"
  for w in words[1:]:
    print "You scream '%s'." % w
  return True

loc_sidewalk.add_verb( 'scream', scream )

# Add an animal to roam around.  Animals act autonomously
cat = Animal(world, "cat")
cat.set_location(loc_sidewalk)
cat.add_verb("pet", say("The cat purrs.") )
cat.add_verb("eat", say_on_noun("cat", "Don't do that, PETA will get you!"));
cat.add_verb("kill", say_on_noun("cat", "The cat escapes and bites you. Ouch!"));

# Add a robot.  Robots can take commands to perform actions.
robby = Robot( world, "Robby" )
robby.set_location( loc_sidewalk )

# Add a Pet.  Pets are like Animals because they can act autonomously,
# but they also are like Robots in that they can take commands to
# to perform actions.
fido = Pet ( world, "Fido")
fido.set_location( loc_sidewalk )

# make the player
hero = Hero(world)

# add a hero verb
def throw( self, actor, words ):
  if len(words) > 1 and self.act('drop', words[1] ):
     print 'The %s bounces and falls to the floor' % words[1]
     return True
  else:
     print 'You hurt your arm.'
     return False

hero.add_verb( "throw", throw )

# create shared data
# NOTE: you must either set the server with share.set_host(...) or place the host information
# in a file 'share.info' in the local directory.  The host must be a webdis host using basic
# authentication.
share = Share()
share.set_game("bwx-adventure")
share.set_player("default")
share.start()

# custom verb to record things at locations
def scribble( self, actor, words ):
  if len(words) != 2:
    print "You can only scrible a single word."
    return False
  share.put_game_data('crumb.' + self.location.name, words[1].strip())
  return True

hero.add_verb( "scribble", scribble )

# custom verb to see things written
def peek( self, actor, words ):
  print 'Someone scribbled "%s" here.' % share.get_game_data('crumb.' + self.location.name)
  return True

hero.add_verb( "peek", peek )

# start on the sidewalk
hero.set_location( loc_sidewalk )

# start playing
run_game(hero)
