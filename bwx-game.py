#! /usr/bin/python
import random
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
cat = world.add_actor("cat", loc_sidewalk)

cat.add_verb("pet", say('The cat purrs.') )

# simple verb applicable at this location
loc_sidewalk.add_verb( 'knock', say('The door makes a hollow sound.') )

# custom single location verb
def scream( world, words ):
  print "You scream your head off!"
  for w in words[1:]:
    print "You scream '%s'." % w
  return True

loc_sidewalk.add_verb( 'scream', scream )

# make the player
hero = world.add_hero()

# add a hero verb
def throw( self, noun ):
  if self.act('drop', noun):
     print 'The %s bounces and falls to the floor' % noun
     return True
  else:
     print 'You hurt your arm.'
     return False

hero.add_verb( "throw", throw )

def move_cat( world ):
  e = random.choice( cat.location.exits.items() )
  cat.set_location( e[1].point_b )
  if e[1].point_a == hero.location:
    print "The cat leaves."
  if e[1].point_b == hero.location:
    print "The cat enters."

world.add_turn_hook(move_cat)

# start on the sidewalk
hero.set_location( loc_sidewalk )

# start playing
run_game(hero)
