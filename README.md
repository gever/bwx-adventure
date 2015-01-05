bwx-adventure
=============

A simple module for writing text adventure games in Python.

This module posits a text adventure World made up of Locations. Locations are
linked by Connections and sometimes contain Things. The player is represented
by a Hero object that has a current location. The command parser is simple but
is easily extended with new commands.

This was initially written in support of the Orange Band at <a href="http://sfbrightworks.org">SF Brightworks</a>.

Contributions are welcome! Open an issue or a pull request.

```python
from advent import *

# setup the game you are going to build on...
my_game = Game()

# create your world, then we can stick stuff in it
my_world = World()

# create some locations
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

# let's add the locations to your world
my_world.add_location(sidewalk)
my_world.add_location(vestibule)

# make connections between those locations
big_door = Connection("Big Door", sidewalk, vestibule, [IN, EAST], [WEST, OUT])

# now add the connections to the world too
my_world.add_connection(big_door)

# create some things to put in your world. You need a name and
elev_key = Thing( "key", "small tarnished brass key" )
pebble = sidewalk.put( Thing( "pebble", "round pebble" ) )
sidewalk.put( elev_key )
sidewalk.put( pebble )

# simple verb applicable at this location
sidewalk.add_verb( 'knock', my_game.say('The door makes a hollow sound.') )

# Add an animal to roam around.  Animals act autonomously
cat = Animal(my_world, "cat")
cat.set_location(sidewalk)
cat.add_verb("pet", my_game.say("The cat purrs.") )

# make the player
hero = Hero(my_world)

# add a new hero verb (allows player to say "throw pebble")
def throw( self, actor, words ):
  if len(words) > 1 and self.act('drop', words[1] ):
     print 'The %s bounces and falls to the floor' % words[1]
     return True
  else:
     print 'You hurt your arm.'
     return False

hero.add_verb( "throw", throw )

# start on the sidewalk
hero.set_location( sidewalk )

# start playing (hey, there's a key here!)
my_game.run(hero)
```
