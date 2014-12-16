#
# adventure module
#

# A "direction" is all the ways you can describe going some way
directions = {}
NORTH = 1
SOUTH = 2
EAST = 3
WEST = 4
UP = 5
DOWN = 6
RIGHT = 7
LEFT = 8
IN = 9
OUT = 10
FORWARD = 11
BACK = 12
NORTH_WEST = 13
NORTH_EAST = 14
SOUTH_WEST = 15
SOUTH_EAST = 16
NOT_DIRECTION = -1

# map direction names to direction numbers
def define_direction( number, name ):
	# check to see if we are trying to redefine an existing direction
	if name in directions:
		print name, "is already defined as,", directions[name] 
	directions[name] = number

# see if a word is a defined direction
def lookup_dir( d ):
	if d in directions:
		return directions[d]
	else:
		return NOT_DIRECTION

define_direction( NORTH, "north" )
define_direction( NORTH, "n" )
define_direction( SOUTH, "south" )
define_direction( SOUTH, "s" )
define_direction( EAST, "east" )
define_direction( EAST, "e" )
define_direction( WEST, "west" )
define_direction( WEST, "w" )
define_direction( UP, "up" )
define_direction( UP, "u" )
define_direction( DOWN, "down" )
define_direction( DOWN, "d" )
define_direction( RIGHT, "right" )
define_direction( RIGHT, "r" )
define_direction( LEFT, "left" )
define_direction( LEFT, "l" )
define_direction( IN, "in" )
define_direction( OUT, "out" )
define_direction( FORWARD, "forward" )
define_direction( FORWARD, "fd" )
define_direction( FORWARD, "fwd" )
define_direction( FORWARD, "f" )
define_direction( BACK, "back" )
define_direction( BACK, "bk" )
define_direction( BACK, "b" )
define_direction( NORTH_WEST, "nw" )
define_direction( NORTH_EAST, "ne" )
define_direction( SOUTH_WEST, "sw" )
define_direction( SOUTH_EAST, "se" )

# changes "lock" to "a lock", "apple" to "an apple", etc.
# note that no article should be added to proper names; store
# a global list of these somewhere?!!!
def add_article ( name ):
   vowels = "aeiou"
   article = "an" if name and (name[0] in vowels) else "a"
   return "%s %s" % (article, name)
    
def proper_list_from_dict( d ):
	names = d.keys()
	buf = []
	name_count = len(names)
	for (i,name) in enumerate(names):
		if i != 0:
			buf.append(", " if name_count > 2 else " ")
		if i == name_count-1 and name_count > 1:
			buf.append("and ")
		buf.append(add_article(name))
	return "".join(buf)

class Thing:
	# name: short name of this thing
	# description: full description
	# fixed: is it stuck or can it be taken

	def __init__( self, name, desc, fixed=False ):
		self.name = name
		self.description = desc
		self.fixed = fixed
	
	def describe( self ):
		return self.name

# A "location" is a place in the game.
class Location:
	# name: short name of this location
	# description: full description
	# contents: things that are in a location
	# exits: ways to get out of a location
	# first_time: is it the first time here?

	def __init__( self, name, desc ):
		self.name = name
		self.description = desc.strip()
		self.contents = {}
		self.exits = {}
		self.first_time = True
		
	def put( self, thing ):
		self.contents[thing.name] = thing

	def describe( self, force=False ):
		desc = ""		# start with a blank string

		# add the description
		if self.first_time or force:
			desc += self.description
			self.first_time = False

		# any things here?
		if len(self.contents) > 0:
			# add a newline so that the list starts on it's own line
			desc += "\n"

			# try to make a readable list of the things
			contents_description = proper_list_from_dict(self.contents)
			# is it just one thing?
			if len(self.contents) == 1:
			   desc += "There is %s here." % contents_description
			else: 
				desc += "There are a few things here: %s" % contents_description
		return desc

	def add_exit( self, con, way ):
		self.exits[ way ] = con
	
	def go( self, way ):
		if way in self.exits:
			c = self.exits[ way ]
			return c.point_b
		else:
			return None

	def debug( self ):
		for key in exits:
			print "exit:", directions[key], 

# A "connection" connects point A to point B. Connections are
# always described from the point of view of point A.
class Connection:
	# name
	# description
	# point_a
	# point_b

	def __init__( self, pa, name, pb ):
		self.name = name
		self.point_a = pa
		self.point_b = pb

# a World is how all the locations, things, and connections are organized
class World:
	# locations

	def __init__ ( self ):
		self.locations = {}
   
	# make a connection between point A and point B
	def connect( self, point_a, name, point_b, way ):
		c = Connection( point_a, name, point_b )
		point_a.add_exit( c, way )
		return c

	# make a bidirectional between point A and point B
	def biconnect( self, point_a, point_b, name, ab_way, ba_way ):
		c1 = Connection( point_a, name, point_b )
		point_a.add_exit( c1, ab_way )
		c2 = Connection( point_b, name, point_a )
		point_b.add_exit( c2, ba_way )
		return c1, c2
	
	# add another location to the world
	def add_location( self, name, description ):
		l = Location( name, description )
		self.locations[name] = l
		return l
	
# A "person" is the actor in a world
class Person:
	# world
	# location
	# inventory
	# moved
	# verbs

	def __init__( self, w ):
		self.world = w
		self.inventory = {}
		self.verbs = {}

		# associate each of the known actions with functions
		self.verbs['take'] = self.act_take
		self.verbs['inventory'] = self.act_inventory
		self.verbs['i'] = self.act_inventory
		self.verbs['look'] = self.act_look

	# describe where we are
	def describe( self ):
		return self.location.describe()
	
	# establish where we are "now"
	def set_location( self, loc ):
		self.location = loc
		self.moved = True

	# move a thing from the current location to our inventory
	def act_take( self, noun=None ):
		if noun in self.location.contents:
			t = self.location.contents[noun]
			del self.location.contents[noun]
			self.inventory[noun] = t
			return True
		else:
			return False
	
	def act_look( self, noun=None ):
		print self.location.describe( True )
	
	# list the things we're carrying
	def act_inventory( self, noun=None ):
		msg = ""
		if len(self.inventory.keys()) > 0:
			msg += "You are carrying "
			msg += proper_list_from_dict( self.inventory )
			print msg

	# check/clear moved status
	def check_if_moved( self ):
		status = self.moved
		self.moved = False
		return status

	# try to go in a given direction
	def go( self, d ):
		loc = self.location.go( d )
		if loc == None:
			print "Bonk! Sorry, you can't seem to go that way."
		else:
			# update where we are
			self.location = loc
			self.moved = True
		return self.location

	# define action verbs
	def define_action( self, verb, func ):
		self.verbs[verb] = func
	
	def perform_action( self, verb, noun=None ):
		if verb in self.verbs:
			self.verbs[verb]( noun )
			return True
		else:
			return False

	# do something
	def simple_act( self, verb ):
		d = lookup_dir( verb )
		if d == NOT_DIRECTION:
			# see if it's a known action
			if self.perform_action( verb ):
				return
			else:
				print "Sorry, I don't understand '%s'." % verb
		else:
			# try to move in the given direction
			self.location = self.go( d )

	# do something to something
	def act( self, verb, noun ):
		# "go" is a special case
		if verb == 'go':
			self.simple_act( noun )
		else:
			if self.perform_action( verb, noun ):
				return
			else:
				print "Oops. Don't know how to '%s'." % verb
