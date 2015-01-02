#
# adventure module
#
# vim: et sw=2 ts=2 sts=2

# for Python3, use:
# import urllib.request as urllib2
import urllib2

import random
import time

# A "direction" is all the ways you can describe going some way
directions = {}

# These are code-visible canonical names for directions for adventure authors
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

# define player words used to describe known directions
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

def remove_superfluous_input(text):
  superfluous = articles +  ['to']
  rest = []
  for word in text.split():
    if word not in superfluous:
      rest.append(word)
  return ' '.join(rest)

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

class Game(object):
  
  def __init__(self, name="bwx-adventure-game"):
    self.name = name
    self.objects = {}
    self.world = None
    self.fresh_location = False

  def set_name(self, name):
    self.name = name

  def add_world(self, world):
    self.world = world
    world.game = self
      
  def add_object(self, obj, scope):
    self.objects[scope + '.' + obj.name] = obj
    
  def output(self, text, message_type = 0):
    # we add a newline to user putput since they may not add it themselves
    output(text + "\n", message_type)
  
  def do_say(self, s):
    print s
    return True
    
  # checks to see if the inventory in the items list is in the user's inventory
  def inventory_contains(self, items):
    if set(items).issubset(set(self.world.hero.inventory.values())):
      return True
    return False
    
  def entering_location(self, location):
    if (self.world.hero.location == location and self.fresh_location):
        return True
    return False
  
  def say(self, s):
    return (lambda s: lambda *args: self.do_say(s))(s)
  
  
  def do_say_on_noun(self, n, s, words):
    if len(words) < 2:
      return False
    noun = words[1]
    if noun != n:
      return False
    print s
    return True
  
  
  def say_on_noun(self, n, s):
    return (lambda n, s: lambda self, words: self.do_say_on_noun(n, s, words))(n, s)
  
  
  def run(self , update_func = False):
    
    # reset this every loop so we dont trigger things more than once
    self.fresh_location = False
    
    actor = self.world.hero
    while True:
      # if the actor moved, describe the room
      if actor.check_if_moved():
        output("        --=( %s %s in the %s )=--        " % (actor.name.capitalize(),
                                                     actor.isare,
                                                     actor.location.name), TITLE)

        # cache this as we need to know it for the query to entering_location()
        self.fresh_location = actor.location.first_time
        
        where = actor.location.describe(actor)
        if where:
          output( where )
  
      # See if the animals want to do anything
      for animal in actor.world.animals.items():
        animal[1].act_autonomously(actor.location)
        
      # has the developer supplied an update function?
      if (update_func):
        update_func() #call the update function
  
      # check if we're currently running a script
      user_input = actor.get_next_script_line();
      if user_input == None:    
        # get input from the user
        try:
          user_input = raw_input("> ")
        except EOFError:
          break
        if user_input == 'q' or user_input == 'quit':
          break

      clean_user_input = remove_superfluous_input(user_input)
        
      # see if the command is for a robot
      if ':' in clean_user_input:
         robot_name, command = clean_user_input.split(':')
         try:
            actor = self.world.robots[robot_name]
         except KeyError:
            output( "I don't know anybot named %s" % robot_name, FEEDBACK)
            continue
      else:
         actor = self.world.hero
         command = clean_user_input
  
      # give the input to the actor in case it's recording a script
      if not actor.set_next_script_line(command):
        continue
         
      words = command.split()
      if not words:
        continue
  
      verb = words[0]
      noun = None
      if len(words) > 1:
        noun = words[1]
  
      f = actor.location.get_verb( verb )
      if f:
        if f( actor.location, words ):
          continue
  
      # give precedence to the primary actor for the verb
      f = actor.get_verb( verb )
      if f:
        if f( actor, words ):
          continue
      
      done = False  # sadly, python doesn't have break with a label
      for a in actor.location.actors:
        if a == actor:
          continue
        f = a.get_verb( verb )
        if f:
          if f( a, words ):
            done = True
            break
      if done:
        continue
  
      # treat 'verb noun1 and noun2..' as 'verb noun1' then 'verb noun2'
      # treat 'verb noun1, noun2...' as 'verb noun1' then 'verb noun2'
      if len( words ) > 2:
        for noun in words[1:]:
          noun = noun.strip(',')
          if noun in articles: continue
          if noun == 'and': continue
          actor.do_act( verb, noun )
        continue
  
      # try to do what the user says
      if len( words ) == 2:
        # action object
        # e.g. take key
        actor.do_act( verb, noun )
        continue
  
      assert len( words ) == 1
      # action (implied object/subject)
      # e.g. north
      actor.do_act( "go", verb )

# GameObject is a place to put default inplementations of methods that everything
# in the world should support (eg save/restore, how to respond to verbs etc)
class GameObject(object):
  def __init__(self, name):
    self.game = None
    #self.game.add_object(self, "GameObject") #should this be handed in the Game.add_object method?

class Thing(object):
  # name: short name of this thing
  # description: full description
  # fixed: is it stuck or can it be taken

  def __init__( self, name, desc, fixed=False ):
    self.name = name
    self.description = desc
    self.fixed = fixed

  def describe( self, observer ):
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

  def __init__( self, name, desc):#, world ):
    self.name = name
    self.description = desc.strip()
    self.contents = {}
    self.exits = {}
    self.first_time = True
    self.verbs = {}
    self.actors = set()
    self.requirements = {}
    #self.world = world
    self.world = None

  def put( self, thing ):
    self.contents[thing.name] = thing
    return thing

  def describe( self, observer, force=False ):
    desc = ""   # start with a blank string

    # add the description
    if self.first_time or force:
      desc += style_text(self.description + "\n", DESCRIPTION)
      self.first_time = False

    # any things here?
    if self.contents:
      # add a newline so that the list starts on it's own line
      desc += "\n"
      
      # try to make a readable list of the things
      contents_description = proper_list_from_dict(self.contents)
      # is it just one thing?
      if len(self.contents) == 1:
        desc += style_text("There is %s here." % contents_description, CONTENTS)
      else:
        desc += style_text("There are a few things here: %s." % contents_description, CONTENTS)
    
    if self.actors:
      desc += "\n"
      for a in self.actors:
        if a != observer:
          desc += style_text(add_article(a.describe(a)).capitalize() + " " + a.isare + " here.\n", CONTENTS)
    
    return desc

  def add_exit( self, con, way ):
    self.exits[ way ] = con

  def go( self, way ):
    if way in self.exits:
      c = self.exits[ way ]
      
      # check if there are any requirements for this room
      if len(c.point_b.requirements) > 0:
        # check to see if the requirements are in the inventory
        if set(c.point_b.requirements).issubset(set(self.world.hero.inventory)):
          output( "You use the %s, the %s unlocks" % (proper_list_from_dict(c.point_b.requirements), c.point_b.name), FEEDBACK)
          return c.point_b
        
        output( "It's locked! You will need %s." % proper_list_from_dict(c.point_b.requirements), FEEDBACK)
        return None
      else:
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
      
  def add_requirement(self, thing):
      self.requirements[thing.name] = thing


# A "connection" connects point A to point B. Connections are
# always described from the point of view of point A.
class Connection(object):
  # name
  # point_a
  # point_b

  def __init__( self, name, pa, pb, way_ab, way_ba):
    self.name = name
    self.point_a = pa
    self.point_b = pb
    self.way_ab = way_ab
    self.way_ba = way_ba


# An actor in the world
class Actor(object):
  # world
  # location
  # inventory
  # moved
  # verbs

  def __init__( self, n, hero = False ):
    self.world = None
    self.location = None
    self.inventory = {}
    self.verbs = {}
    self.name = n
    self.cap_name = n.capitalize()
    self.hero = hero
    if hero:
      self.isare = "are"
      #assert self.world.hero == None
      #self.world.hero = self
    else:
      self.isare = "is"
    # associate each of the known actions with functions
    self.verbs['take'] = self.act_take
    self.verbs['get'] = self.act_take
    self.verbs['drop'] = self.act_drop
    self.verbs['inventory'] = self.act_inventory
    self.verbs['i'] = self.act_inventory
    self.verbs['look'] = self.act_look
    self.verbs['l'] = self.act_look

  # describe ourselves
  def describe( self, observer ):
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
  def act_take( self, actor, words=None ):
    if len(words) < 2:
       return False
    noun = words[1]
    t = self.location.contents.pop(noun, None)
    if t:
      self.inventory[noun] = t
      output("You take the %s \n" % t.name)
      return True
    else:
      output("%s can't take the %s." % (self.cap_name, noun))
      return False

  # move a thing from our inventory to the current location
  def act_drop( self, actor, words=None ):
    if not words:
      return False
    noun = words[1]
    if not noun:
      return False
    t = self.inventory.pop(noun, None)
    if t:
      self.location.contents[noun] = t
      return True
    else:
      output( "%s %s not carrying %s." % (self.cap_name, self.isare, add_article(noun)), FEEDBACK)
      return False

  def act_look( self, actor, words=None ):
    print self.location.describe( actor, True )
    return True

  # list the things we're carrying
  def act_inventory( self, actor, words=None ):
    msg = '%s %s carrying ' % (self.cap_name, self.isare)
    if self.inventory.keys():
      msg += proper_list_from_dict( self.inventory )
    else:
      msg += 'nothing'
    msg += '.'
    output( msg, FEEDBACK)
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
      output( "Bonk! %s can't seem to go that way.\n" % self.name, FEEDBACK)
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
    if verb in self.verbs:
      verbs = [verb]
    else:
      for v in self.verbs:
        if v.startswith(verb):
          verbs.append(v)
    words = [verb]
    if noun:
      words.append(noun)
    if len(verbs) == 1:
      return self.verbs[verbs[0]]( self, words )
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
      output( "Huh?", FEEDBACK)

  def add_verb( self, verb, f ):
    self.verbs[' '.join(verb.split())] = f

  def get_verb( self, verb ):
    c = ' '.join(verb.split())
    if c in self.verbs:
       return self.verbs[c]
    else:
      return None

  # support for scriptable actors, override these to implement
  def get_next_script_line( self ):
    return None

  def set_next_script_line( self, line ):
    return True


class Hero(Actor):

  def __init__( self ):
    super(Hero, self).__init__("you", True)

  def add_verb( self, name, f ):
    self.verbs[name] = (lambda self: lambda *args : f(self, *args))(self)


# Scripts are sequences of instructions for Robots to execute
class Script(object):
  def __init__( self, name ):
    self.name = name
    self.lines = list()
    self.current_line = -1
    self.recording = False
    self.running = False

  def start_recording( self ):
    assert not self.running
    assert not self.recording
    self.recording = True

  def stop_recording( self ):
    assert self.recording
    assert not self.running
    self.recording = False

  def start_running( self ):
    assert not self.running
    assert not self.recording
    self.running = True
    self.current_line = 0;

  def stop_running( self ):
    assert self.running
    assert not self.recording
    self.running = False
    self.current_line = -1;

  def get_next_line( self ):
    line = self.lines[self.current_line]
    self.current_line += 1
    if line.strip() == "end":
      self.stop_running()
      return None
    return line

  def set_next_line( self, line ):
    self.lines.append(line)
    if line.strip() == "end":
      self.stop_recording()
      return False
    return True

  def print_lines( self ):
    for line in self.lines:
      print line  

  def save_file(self):
    f = open(self.name + ".script", "w")
    for line in self.lines:
      f.write(line + '\n')
    f.close()

  def load_file(self):
    f = open(self.name + ".script", "r")
    for line in f:
      self.lines.append(line.strip())
    f.close()

    
# Robots are actors which accept commands to perform actions.
# They can also record and run scripts.
class Robot(Actor):
  def __init__( self, name ):
    super(Robot, self ).__init__( name )
    self.name = name
    self.scripts = {}
    self.current_script = None
    self.script_think_time = 0
    self.verbs['record'] = self.act_start_recording
    self.verbs['run'] = self.act_run_script
    self.verbs['print'] = self.act_print_script
    self.verbs['save'] = self.act_save_file
    self.verbs['load'] = self.act_load_file
    self.verbs['think'] = self.set_think_time

  def parse_script_name(self, words):
    if not words or len(words) < 2:
        script_name = "default"
    else:
        script_name = words[1]
    return script_name
      
  def act_start_recording(self, actor, words=None):
    script_name = self.parse_script_name(words)
    script = Script(script_name)
    self.scripts[script_name] = script
    script.start_recording()
    self.current_script = script
    return True
      
  def act_run_script(self, actor, words=None):
    if self.current_script:
      print "You must stop \"%s\" first." % (self.current_script.name)
    script_name = self.parse_script_name(words)
    if not script_name in self.scripts:
      print "%s can't find script \"%s\" in its memory." % (self.name,
                                                              script_name)

      return True;
    
    script = self.scripts[script_name]
    self.current_script = script
    script.start_running()
    return True
      
  def act_print_script(self, actor, words=None):
    script_name = self.parse_script_name(words)
    if not script_name in self.scripts:
      print "%s can't find script \"%s\" in its memory." % (self.name,
                                                              script_name)
      return True

    print "----------------------8<-------------------------"
    self.scripts[script_name].print_lines()
    print "---------------------->8-------------------------"
    return True

  def act_save_file(self, actor, words=None):
    script_name = self.parse_script_name(words)
    if not script_name in self.scripts:
      print "%s can't find script \"%s\" in its memory." % (self.name,
                                                              script_name)
      return True
    self.scripts[script_name].save_file()
    return True

  def act_load_file(self, actor, words=None):
    script_name = self.parse_script_name(words)
    self.scripts[script_name] = Script(script_name)
    self.scripts[script_name].load_file()
    return True

  def set_think_time(self, actor, words):
    if words and len(words) == 2:
      t = float(words[1])
      if t >= 0 and t <= 60:
          self.script_think_time = t
          return True
      
    print "\"think\" requires a number of seconds (0-60) as an argument"
    return True    
      
  def get_next_script_line(self):
    if not self.current_script or not self.current_script.running:
      return None
    line = self.current_script.get_next_line()
    if not line:
      print "%s is done running script \"%s\"." % (self.name,
                                                   self.current_script.name)
      self.current_script = None
      return None
    if self.script_think_time > 0:
      time.sleep(self.script_think_time)
    line = self.name + ": " + line
    print "> %s" % line
    return line

  def set_next_script_line(self, line):
    if not self.current_script or not self.current_script.recording:
      return True
    if not self.current_script.set_next_line(line):
      print "%s finished recording script \"%s\"." % (self.name,
                                                      self.current_script.name)
      self.current_script = None
      return False
    return True

        

# Animals are actors which may act autonomously each turn
class Animal(Actor):
  def __init__( self, name ):
    super(Animal, self ).__init__( name )
    self.name = name
       
  def act_autonomously(self, observer_loc):
    self.random_move(observer_loc)

  def random_move(self, observer_loc):
    if random.random() > 0.2:  # only move 1 in 5 times
      return
    exit = random.choice(self.location.exits.items())
    desc = ""
    if self.location == observer_loc:
      desc += "%s leaves the %s via the %s \n" % (add_article(self.name).capitalize(),
                                            observer_loc.name,
                                            exit[1].name)
      output( desc, FEEDBACK)
    self.go(exit[0])
    if self.location == observer_loc:
      desc += "%s enters the %s via the %s \n" % (add_article(self.name).capitalize(),
                                            observer_loc.name,
                                            exit[1].name)
      output( desc, FEEDBACK)

# A pet is an actor with free will (Animal) that you can also command to do things (Robot)
class Pet(Robot, Animal):
  def __init__( self, name ):
    super(Pet, self ).__init__( name )
    self.leader = None
    self.verbs['heel'] = self.act_follow
    self.verbs['follow'] = self.act_follow
    self.verbs['stay'] = self.act_stay
      
  def act_follow(self, actor, words=None):
    self.leader = self.world.hero
    output( "%s obediently begins following %s" % (self.name, self.leader.name) , FEEDBACK)
    return True

  def act_stay(self, actor, words=None):
    if self.leader:
      output( "%s obediently stops following %s" % (self.name, self.leader.name) , FEEDBACK)
    self.leader = None
    return True

  def act_autonomously(self, observer_loc):
    if self.leader:
      self.set_location(self.leader.location)
    else:
      self.random_move(observer_loc)
    

# a World is how all the locations, things, and connections are organized
class World(object):
  # locations
  # hero, the first person actor
  # robots, list of actors which are robots (can accept comands from the hero)
  # animals, list of actors which are animals (act on their own)
  
  def __init__ ( self ):
    self.hero = None
    self.locations = {}
    self.robots = {}
    self.animals = {}
    self.game = None

    
  # make a (one-way) connection between point A and point B
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
    
  # add a bidirectional connection between points A and B
  def add_connection( self, connection ):
    if isinstance(connection.way_ab, (list, tuple)):
      for way in connection.way_ab:
        connection.point_a.add_exit( connection, way )
    else:
      connection.point_a.add_exit( connection, connection.way_ab )
    
    # this is messy, need a better way to do this
    reverse_connection = Connection( connection.name, connection.point_b, connection.point_a, connection.way_ba, connection.way_ab)
    if isinstance(connection.way_ba, (list, tuple)):
      for way in connection.way_ba:
        connection.point_b.add_exit( reverse_connection, way )
    else:
      connection.point_b.add_exit( reverse_connection, connection.way_ba )
      
    return connection

  # add another location to the world
  def add_location(self,  location ):
    location.world = self
    self.locations[location.name] = location
    return location
    
  # add an actor to the world
  def add_actor(self, actor):
    if isinstance(actor, Hero):
      self.hero = actor
      
    if isinstance(actor, Animal):
      self.animals[actor.name] = actor
      
    if isinstance(actor, Robot):
      self.robots[actor.name] = actor
      
    actor.world = self
    return actor


class Share(object):
  def __init__(self):
    self.hostname = None
    self.port = None
    self.username = None
    self.password = None
    self.GLOBAL = 1
    self.ADVENTURE = 2
    self.PLAYER = 3
    self.SESSION = 4
    self.game = ""
    self.player = ""
    self.session = ""
    self.key_fns = {
        self.GLOBAL: self.global_key,
        self.ADVENTURE: self.adventure_key,
        self.PLAYER: self.player_key,
        self.SESSION: self.session_key,
    }
    try:
      f = open("share.info", "r")
      self.hostname = f.readline().strip()
      self.port = f.readline().strip()
      self.username = f.readline().strip()
      self.password = f.readline().strip()
    except IOError:
      pass

  def set_host(self, hostname, port, username, password):
    self.hostname = hostname
    self.port = port
    self.username = username
    self.password = password

  def set_adventure(self, adventure):
    self.adventure = adventure

  def set_player(self, player):
    self.player = player

  def set_session(self, session):
    self.session = session

  def is_available(self):
    return self.hostname != None

  def start(self):
    if not self.is_available():
      return
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    webdis_url = "http://%s:%s/" % (self.hostname, self.port)
    password_mgr.add_password(None, webdis_url, self.username, self.password)
    self.opener = urllib2.build_opener(urllib2.HTTPBasicAuthHandler(password_mgr))

  def global_key(self, key):
    return 'g.' + key

  def adventure_key(self, key):
    return 'a.' + self.adventure + '.' + key

  def player_key(self, key):
    return 'p.' + self.adventure + '.' + self.player + '.' + key

  def session_key(self, key):
    return 's.' + self.adventure + '.' + self.player + '.' + self.session + key

  def _do(self, domain, cmd, key):
    assert(domain in self.key_fns)
    if not self.is_available():
      return None
    k = self.key_fns[domain](key)
    f = self.opener.open('http://%s:%s/%s/%s.raw' % (self.hostname, self.port, cmd, k))
    v = f.read().split('\n')
    if len(v) > 1:
       return v[1].strip()
    return None

  def _do1(self, domain, cmd, key, arg1):
    assert(domain in self.key_fns)
    if not self.is_available():
      return None
    k = self.key_fns[domain](key)
    f = self.opener.open('http://%s:%s/%s/%s/%s.raw' % (self.hostname, self.port, cmd, k, arg1))
    v = f.read().split('\n')
    if len(v) > 1:
       return v[1]  # should be ""
    return None

  def _do2(self, domain, cmd, key, arg1, arg2):
    assert(domain in self.key_fns)
    if not self.is_available():
      return None
    k = self.key_fns[domain](key)
    f = self.opener.open('http://%s:%s/%s/%s/%s/%s.raw' % (self.hostname, self.port, cmd, k, arg1, arg2))
    v = f.read().split('\n')
    if len(v) > 1:
       return v[1]  # should be ""
    return None

  # return a list
  def _do2l(self, domain, cmd, key, arg1, arg2):
    assert(domain in self.key_fns)
    if not self.is_available():
      return []
    k = self.key_fns[domain](key)
    f = self.opener.open('http://%s:%s/%s/%s/%s/%s.raw' % (self.hostname, self.port, cmd, k, arg1, arg2))
    v = f.read().split('\n')
    return v

  # return a list
  def _do3l(self, domain, cmd, key, arg1, arg2, arg3):
    assert(domain in self.key_fns)
    if not self.is_available():
      return []
    k = self.key_fns[domain](key)
    f = self.opener.open('http://%s:%s/%s/%s/%s/%s/%s.raw' % (self.hostname, self.port, cmd, k, arg1, arg2, arg3))
    v = f.read().split('\n')
    return v

  def delete(self, domain, key):
    return self._do(domain, "DEL", key)

  def get(self, domain, key):
    return self._do(domain, "GET", key)

  def put(self, domain, key, value):
    return self._do1(domain, "SET", key, value)

  def increment(self, domain, key):
    return self._do(domain, "INCR", key)

  def decrement(self, domain, key):
    return self._do(domain, "DECR", key)

  def push(self, domain, key, value):
    return self._do1(domain, "LPUSH", key, value)

  def pop(self, domain, key):
    return self._do(domain, "LPOP", key)

  def zadd(self, domain, key, value, score):
    return self._do2(domain, "ZADD", key, score, value)

  def zscore(self, domain, key):
    return self._do(domain, "ZSCORE", key, value)

  def zdelete_over_rank(self, domain, key, rank):
    return self._do2(domain, "ZREMRANGEBYRANK", key, rank, "-1")

  def ztop(self, domain, key, rank):
    v = self._do2l(domain, "ZREVRANGE", key, "0", rank)
    v = [x.strip() for x in v[1:]]
    result = []
    for x in xrange(0, len(v)):
      if x % 2 == 1:
        result.append(v[x])
    return result

  def ztop_with_scores(self, domain, key, rank):
    v = self._do3l(domain, "ZREVRANGE", key, "0", rank, "WITHSCORES")
    v = [x.strip() for x in v[1:]]
    result = []
    for x in xrange(0, len(v)):
      if x % 4 == 1:
        p = [v[x]]
      elif x % 4 == 3:
        p.append(v[x])
        result.append(p)
    return result

  def zdelete(self, domain, key, value):
    return self._do(domain, "ZREM", key, value)



FEEDBACK = 0
TITLE = 1
DESCRIPTION = 2
CONTENTS = 3


# this handles printing things to output, it also styles them
def output(text, message_type = 0):
    print style_text(text, message_type)
    
# this makes the text look nice in the nerinal... WITH COLORS!
def style_text(text, message_type):
  if (message_type == FEEDBACK):
    text = Colors.FG.pink + text + Colors.reset
  
  if (message_type == TITLE):
    text = Colors.FG.yellow + Colors.BG.blue + "\n" + text + "\n" +  Colors.reset

  if (message_type == DESCRIPTION):
    text = Colors.reset + text

  if (message_type == CONTENTS):
    text = Colors.FG.green + text + Colors.reset
  
  return text
    
    
class Colors:
  '''
  Colors class:
  reset all colors with colors.reset
  two subclasses fg for foreground and bg for background.
  use as colors.subclass.colorname.
  i.e. colors.fg.red or colors.bg.green
  also, the generic bold, disable, underline, reverse, strikethrough,
  and invisible work with the main class
  i.e. colors.bold
  '''
  reset='\033[0m'
  bold='\033[01m'
  disable='\033[02m'
  underline='\033[04m'
  reverse='\033[07m'
  strikethrough='\033[09m'
  invisible='\033[08m'
  class FG:
    black='\033[30m'
    red='\033[31m'
    green='\033[32m'
    orange='\033[33m'
    blue='\033[34m'
    purple='\033[35m'
    cyan='\033[36m'
    lightgrey='\033[37m'
    darkgrey='\033[90m'
    lightred='\033[91m'
    lightgreen='\033[92m'
    yellow='\033[93m'
    lightblue='\033[94m'
    pink='\033[95m'
    lightcyan='\033[96m'
  class BG:
    black='\033[40m'
    red='\033[41m'
    green='\033[42m'
    orange='\033[43m'
    blue='\033[44m'
    purple='\033[45m'
    cyan='\033[46m'
    lightgrey='\033[47m'
    
    
