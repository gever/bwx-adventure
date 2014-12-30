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

  def describe( self, observer, force=False ):
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
        if a != observer:
          desc += add_article(a.describe(a)).capitalize() + " " + a.isare + " here.\n"

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
      assert self.world.hero == None
      self.world.hero = self
    else:
      self.isare = "is"
    # associate each of the known actions with functions
    self.verbs['take'] = self.act_take
    self.verbs['get'] = self.act_take
    self.verbs['drop'] = self.act_drop
    self.verbs['inventory'] = self.act_inventory
    self.verbs['look'] = self.act_look

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
    if not words:
       return False
    noun = words[1]
    t = self.location.contents.pop(noun, None)
    if t:
      self.inventory[noun] = t
      return True
    else:
      print "%s can't take the %s." % (self.cap_name, noun)
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
      print "%s %s not carrying %s." % (self.cap_name, self.isare, add_article(noun))
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
      print "Huh?"

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

  def __init__( self, world ):
    super(Hero, self).__init__(world, "you", True)

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
    def __init__( self, world, name ):
        super(Robot, self ).__init__( world, name )
        world.robots[name] = self
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
    def __init__( self, world, name ):
       super(Animal, self ).__init__( world, name )
       world.animals[name] = self
       self.name = name
       
    def act_autonomously(self, observer_loc):
       self.random_move(observer_loc)

    def random_move(self, observer_loc):
       if random.random() > 0.2:  # only move 1 in 5 times
          return
       exit = random.choice(self.location.exits.items())
       if self.location == observer_loc:
         print "%s leaves the %s via the %s" % (add_article(self.name).capitalize(),
                                                observer_loc.name,
                                                exit[1].name)
       self.go(exit[0])
       if self.location == observer_loc:
         print "%s enters the %s via the %s" % (add_article(self.name).capitalize(),
                                                observer_loc.name,
                                                exit[1].name)

# A pet is an actor with free will (Animal) that you can also command to do things (Robot)
class Pet(Robot, Animal):
    def __init__( self, world, name ):
        super(Pet, self ).__init__( world, name )
        self.leader = None
        self.verbs['heel'] = self.act_follow
        self.verbs['follow'] = self.act_follow
        self.verbs['stay'] = self.act_stay
        
    def act_follow(self, actor, words=None):
        self.leader = self.world.hero
        print "%s obediently begins following %s" % (self.name, self.leader.name) 
        return True

    def act_stay(self, actor, words=None):
        if self.leader:
           print "%s obediently stops following %s" % (self.name, self.leader.name) 
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

  def start(self):
    assert(self.hostname)
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
    k = self.key_fns[domain](key)
    f = self.opener.open('http://%s:%s/%s/%s.raw' % (self.hostname, self.port, cmd, k))
    v = f.read().split('\n')
    if len(v) > 1:
       return v[1].strip()
    return None

  def _do1(self, domain, cmd, key, arg1):
    assert(domain in self.key_fns)
    k = self.key_fns[domain](key)
    f = self.opener.open('http://%s:%s/%s/%s/%s.raw' % (self.hostname, self.port, cmd, k, arg1))
    v = f.read().split('\n')
    if len(v) > 1:
       return v[1]  # should be ""
    return None

  def _do2(self, domain, cmd, key, arg1, arg2):
    assert(domain in self.key_fns)
    k = self.key_fns[domain](key)
    f = self.opener.open('http://%s:%s/%s/%s/%s/%s.raw' % (self.hostname, self.port, cmd, k, arg1, arg2))
    v = f.read().split('\n')
    if len(v) > 1:
       return v[1]  # should be ""
    return None

  # return a list
  def _do2l(self, domain, cmd, key, arg1, arg2):
    assert(domain in self.key_fns)
    k = self.key_fns[domain](key)
    f = self.opener.open('http://%s:%s/%s/%s/%s/%s.raw' % (self.hostname, self.port, cmd, k, arg1, arg2))
    v = f.read().split('\n')
    return v

  # return a list
  def _do3l(self, domain, cmd, key, arg1, arg2, arg3):
    assert(domain in self.key_fns)
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
    return [x.strip() for x in v[1:]]

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
  actor = hero
  while True:
    # if the actor moved, describe the room
    if actor.check_if_moved():
      print
      print "        --=( %s %s in the %s )=--" % (actor.name.capitalize(),
                                                   actor.isare,
                                                   actor.location.name)
      where = actor.location.describe(actor)
      if where:
        print where

    # See if the animals want to do anything
    for animal in actor.world.animals.items():
      animal[1].act_autonomously(actor.location)


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

    # see if the command is for a robot
    if ':' in user_input:
       robot_name, command = user_input.split(':')
       try:
          actor = hero.world.robots[robot_name]
       except KeyError:
          print "I don't know anybot named %s" % robot_name
          continue
    else:
       actor = hero
       command = user_input

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
