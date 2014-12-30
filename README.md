bwx-adventure
=============

A simple module for writing text adventure games in python.

This module posits a text adventure World made up of Locations. Locations are
linked by Connections and sometimes contain Things. The player is represented
by a Hero object that has a current location. The command parser is simple but
is easily extended with new commands.

This was initially written in support of the Orange Band at <a href="http://sfbrightworks.org">SF Brightworks</a>.

```python
from advent import *

# make your world
world = World()

# add locations (basically a name and a narrative description)
loc_sidewalk = world.add_location(
"Sidewalk", """
You are standing in front of a large glass door.
The sign says 'Come In!'
""" )
loc_vestibule = world.add_location(
"Vestibule", """
A small area at the bottom of a flight of stairs.
There is an elevator here (currently locked).
Up the stairs you see the reception desk.
""" )

# make connections between the various locations
world.biconnect( loc_sidewalk, loc_vestibule, "Big Door", IN, OUT )

# put some things in the locations
loc_sidewalk.put( Thing( "pebble", "round pebble" ) )
loc_vestibule.put( Thing( "key", "small brass key") )

# make the player
hero = Hero( world )

# start somewhere (hey, there's a pebble here!)
hero.set_location( loc_sidewalk )

```
