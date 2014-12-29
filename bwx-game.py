#! /usr/bin/python

from advent import *
# for cloud9...
from advent import Game, World, Location, Connection, Thing, Animal, Robot, Pet, Hero
from advent import NORTH, SOUTH, EAST, WEST, UP, DOWN, RIGHT, LEFT, IN, OUT, FORWARD, BACK, NORTH_WEST, NORTH_EAST, SOUTH_WEST, SOUTH_EAST, NOT_DIRECTION

# create your world, then we can stick stuff in it
world = World()

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
There is an elevator here (currently locked), to the east.
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

# add the locations to your world
world.add_location(sidewalk)
world.add_location(vestibule)
world.add_location(reception)
world.add_location(intersection)
world.add_location(elevator)
world.add_location(secret_lab)

# create connections between the different places. each connection needs 
# a name, the two locations to connect, and the two directions you can go to get into and out of the space
# like this: variable = Connection("The Connection Name", location_a, location_b, direction_a, direction_b)
# you can have more than one way of using a connection by combining them in an array
# like this: Connection("The Connection Name", location_a, location_b, [direction_a, other_direction_a], [direction_b, other_direction_b])
big_door = Connection("Big Door", sidewalk, vestibule, [IN, EAST], [WEST, OUT])
stairs = Connection("Stairs", vestibule, reception, UP, DOWN)
steps_to_reception = Connection("A Few Steps", reception, intersection, NORTH, SOUTH)
steps_to_elevator = Connection("A Few Steps", intersection, elevator, EAST, WEST)

# now add the connections to the world too
world.add_connection(big_door)
world.add_connection(stairs)
world.add_connection(steps_to_reception)
world.add_connection(steps_to_elevator)

# create some things to put in your world
elev_key = Thing( "key", "small tarnished brass key" )
elev_lock = Thing( "lock", "ordinary lock" )
sidewalk.put( elev_key )
sidewalk.put( elev_lock )
sidewalk.put( Thing( "pebble", "round pebble" ) )
sidewalk.put( Thing( "Gary the garden gnome",
                          "a small figure liberated from a nearby garden." ) )

# simple verb applicable at this location
sidewalk.add_verb( 'knock', Game.say('The door makes a hollow sound.') )

# custom single location verb
def scream( world, words ):
  print "You scream your head off!"
  for w in words[1:]:
    print "You scream '%s'." % w
  return True

sidewalk.add_verb( 'scream', scream )

# Add an animal to roam around.  Animals act autonomously
cat = Animal(world, "cat")
cat.set_location(sidewalk)
cat.add_verb("pet", Game.say("The cat purrs.") )
cat.add_verb("eat", Game.say_on_noun("cat", "Don't do that, PETA will get you!"));
cat.add_verb("kill", Game.say_on_noun("cat", "The cat escapes and bites you. Ouch!"));

# Add a robot.  Robots can take commands to perform actions.
robby = Robot( world, "Robby" )
robby.set_location( sidewalk )

# Add a Pet.  Pets are like Animals because they can act autonomously,
# but they also are like Robots in that they can take commands to
# to perform actions.
fido = Pet ( world, "Fido")
fido.set_location( sidewalk )

# make the player
hero = Hero(world)

# add a hero verb
def throw( self, noun ):
  if self.act('drop', noun):
     print 'The %s bounces and falls to the floor' % noun
     return True
  else:
     print 'You hurt your arm.'
     return False

hero.add_verb( "throw", throw )

# start on the sidewalk
hero.set_location( sidewalk )

# start playing
Game.run_game(hero)
