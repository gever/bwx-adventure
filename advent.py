#
# adventure module
#

# A "direction" is all the ways you can describe going some way
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

articles = ['a', 'an', 'the']

# changes "lock" to "a lock", "apple" to "an apple", etc.
# note that no article should be added to proper names; store
# a global list of these somewhere?  For now we'll just assume
# anything starting with upper case is proper.
def add_article ( name ):
   consonants = "bcdfghjklmnpqrstvwxyz"
   vowels = "aeiou"
   if name and (name[0] in vowels):
      article = "an "
   elif name and (name[0] in consonants):
      article = "a "
   else:
      article = ""
   return "%s%s" % (article, name)

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

class Thing(object):
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
class Location(object):
  # name: short name of this location
  # description: full description
  # contents: things that are in a location
  # exits: ways to get out of a location
  # first_time: is it the first time here?
  # actors: other actors in the location
  # world: the world

  def __init__( self, name, desc, world ):
    self.name = name
    self.description = desc.strip()
    self.contents = {}
    self.exits = {}
    self.first_time = True
    self.verbs = {}
    self.actors = set()
    self.world = world

  def put( self, thing ):
    self.contents[thing.name] = thing

  def describe( self, force=False ):
    desc = ""   # start with a blank string

    # add the description
    if self.first_time or force:
      desc += self.description
      self.first_time = False

    # any things here?
    if self.contents:
      # add a newline so that the list starts on it's own line
      desc += "\n"

      # try to make a readable list of the things
      contents_description = proper_list_from_dict(self.contents)
      # is it just one thing?
      if len(self.contents) == 1:
        desc += "There is %s here." % contents_description
      else:
        desc += "There are a few things here: %s." % contents_description

    if self.actors:
      desc += "\n"
      for a in self.actors:
        desc += add_article(a.describe()).capitalize() + " is here.\n"

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
    for key in self.exits:
      print "exit: %s" % key

  def add_verb( self, verb, f ):
    self.verbs[' '.join(verb.split())] = f

  def get_verb( self, verb ):
    c = ' '.join(verb.split())
    if c in self.verbs:
       return self.verbs[c]
    else:
      return None


# A "connection" connects point A to point B. Connections are
# always described from the point of view of point A.
class Connection(object):
  # name
  # point_a
  # point_b

  def __init__( self, pa, name, pb ):
    self.name = name
    self.point_a = pa
    self.point_b = pb


# An actor in the world
class Actor(object):
  # world
  # location
  # inventory
  # moved
  # verbs

  def __init__( self, w, n, hero = False ):
    self.world = w
    self.location = None
    self.inventory = {}
    self.verbs = {}
    self.name = n
    self.cap_name = n.capitalize()
    self.hero = hero
    if hero:
      self.isare = "are"
    else:
      self.isare = "is"

  # describe ourselves
  def describe( self ):
    return self.name

  # establish where we are "now"
  def set_location( self, loc ):
    if not self.hero and self.location:
      self.location.actors.remove( self )
    self.location = loc
    self.moved = True
    if not self.hero:
      self.location.actors.add( self )

  # move a thing from the current location to our inventory
  def act_take( self, noun=None ):
    t = self.location.contents.pop(noun, None)
    if t:
      self.inventory[noun] = t
      return True
    else:
      print "%s can't take the %s." % (self.cap_name, noun)
      return False

  # move a thing from our inventory to the current location
  def act_drop( self, noun=None ):
    if not noun:
      return False
    t = self.inventory.pop(noun, None)
    if t:
      self.location.contents[noun] = t
      return True
    else:
      print "%s %s not carrying %s." % (self.cap_name, self.isare, add_article(noun))
      return False

  def act_look( self, noun=None ):
    print self.location.describe( True )
    return True

  # list the things we're carrying
  def act_inventory( self, noun=None ):
    msg = '%s %s carrying ' % (self.cap_name, self.isare)
    if self.inventory.keys():
      msg += proper_list_from_dict( self.inventory )
    else:
      msg += 'nothing'
    msg += '.'
    print msg
    return True

  # check/clear moved status
  def check_if_moved( self ):
    status = self.moved
    self.moved = False
    return status

  # try to go in a given direction
  def go( self, d ):
    loc = self.location.go( d )
    if loc == None:
      print "Bonk! %s can't seem to go that way." % self.name
      return False
    else:
      # update where we are
      self.set_location( loc )
      return True

  # define action verbs
  def define_action( self, verb, func ):
    self.verbs[verb] = func

  # return True on success, False on failure and None if the command isn't found.
  def perform_action( self, verb, noun=None ):
    verbs = []
    for v in self.verbs:
      if v.startswith(verb):
        verbs.append(v)
    if len(verbs) == 1:
      return self.verbs[verbs[0]]( noun )
    else:
      return None

  # do something
  def simple_act( self, verb ):
    # try direction
    d = lookup_dir( verb )
    if d != NOT_DIRECTION:
      return self.go( d )
    verbs = []
    for v in self.verbs:
      if v.startswith(verb):
        verbs.append(v)
    # try prefix match
    return self.perform_action( verb )

  # do something to something
  def act( self, verb, noun ):
    # "go" is a special case
    if verb == 'go':
      return self.simple_act( noun )
    else:
      return self.perform_action( verb, noun )

  # do something and report if the command is not found.
  def do_act( self, verb, noun ):
    if self.act( verb, noun ) == None:
      print "Huh?"

  def add_verb( self, verb, f ):
    self.verbs[' '.join(verb.split())] = f

  def get_verb( self, verb ):
    c = ' '.join(verb.split())
    if c in self.verbs:
       return self.verbs[c]
    else:
      return None


class Hero(Actor):

  def __init__( self, w ):
    super(Hero, self).__init__(w, "you", True)
    # associate each of the known actions with functions
    self.verbs['take'] = self.act_take
    self.verbs['get'] = self.act_take
    self.verbs['drop'] = self.act_drop
    self.verbs['inventory'] = self.act_inventory
    self.verbs['look'] = self.act_look

  def add_verb( self, name, f ):
      self.verbs[name] = (lambda self: lambda *args : f(self, *args))(self)



# a World is how all the locations, things, and connections are organized
class World(object):
  # locations

  def __init__ ( self ):
    self.locations = {}
    self.turn_hooks = set()

  # make a connection between point A and point B
  def connect( self, point_a, name, point_b, way ):
    c = Connection( point_a, name, point_b )
    point_a.add_exit( c, way )
    return c

  # make a bidirectional between point A and point B
  def biconnect( self, point_a, point_b, name, ab_way, ba_way ):
    c1 = Connection( point_a, name, point_b )
    if isinstance(ab_way, (list, tuple)):
      for way in ab_way:
        point_a.add_exit( c1, way )
    else:
      point_a.add_exit( c1, ab_way )
    c2 = Connection( point_b, name, point_a )
    if isinstance(ba_way, (list, tuple)):
      for way in ba_way:
        point_b.add_exit( c2, way )
    else:
      point_b.add_exit( c2, ba_way )
    return c1, c2

  # add another location to the world
  def add_location( self, name, description ):
    l = Location( name, description, self )
    self.locations[name] = l
    return l

  # add an actor to the world
  def add_actor( self, name, loc ):
    a = Actor( self, name )
    a.set_location( loc )
    return a

  # a hero to the world
  def add_hero( self ):
    return Hero( self )

  def add_turn_hook( self, h ):
    self.turn_hooks.add( h )

  def call_turn_hooks( self ):
    for h in self.turn_hooks:
      h(self)


def do_say(s):
  print s
  return True


def say(s):
  return (lambda s: lambda *args: do_say(s))(s)


def do_say_on_noun(n, s, words):
  if len(words) < 2:
    return False
  noun = words[1]
  if noun != n:
    return False
  print s
  return True


def say_on_noun(n, s):
  return (lambda n, s: lambda self, words: do_say_on_noun(n, s, words))(n, s)


def run_game( hero ):
  while True:
    hero.world.call_turn_hooks()

    # if the hero moved, describe the room
    if hero.check_if_moved():
      print
      print "        --=( %s )=--" % hero.location.name
      where = hero.location.describe()
      if where:
        print where

    # get input from the user
    try:
      command = raw_input("> ")
    except EOFError:
      break
    if command == 'q' or command == 'quit':
       break
    words = command.split()
    if not words:
      continue

    f = hero.location.get_verb( words[0] )
    if f:
      if f( hero.location, words ):
        continue

    done = False  # sadly, python doesn't have break with a label
    for a in hero.location.actors:
      f = a.get_verb( words[0] )
      if f:
        if f( a, words ):
          done = True
          break
    if done:
      continue

    verb = words[0]
    # treat 'verb noun1 and noun2..' as 'verb noun1' then 'verb noun2'
    # treat 'verb noun1, noun2...' as 'verb noun1' then 'verb noun2'
    if len( words ) > 2:
      for noun in words[1:]:
        noun = noun.strip(',')
        if noun in articles: continue
        if noun == 'and': continue
        hero.do_act( verb, noun )
      continue

    # try to do what the user says
    if len( words ) == 2:
      # action object
      # e.g. take key
      verb, noun = words
      hero.do_act( verb, noun )
      continue

    assert len( words ) == 1
    # action (implied object/subject)
    # e.g. north
    hero.do_act( "go", verb )
