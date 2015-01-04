#
# adventure module
#
# vim: et sw=2 ts=2 sts=2

# for Python3, use:
# import urllib.request as urllib2
import urllib2

import random
import textwrap
import time

# A "direction" is all the ways you can describe going some way
directions = {}
direction_name = {}

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
  if not number in direction_name or (len(direction_name[number]) < len(name)):
    direction_name[number] = name

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
define_direction( LEFT, "left" )
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


# Base is a place to put default inplementations of methods that everything
# in the game should support (eg save/restore, how to respond to verbs etc)
class Base(object):
  def __init__(self, name):
    self.game = None
    self.name = name
    self.verbs = {}
    self.vars = {}

  def flag(self, f):
    if f in self.vars:
      return self.vars[f]
    else:
      return False

  def set_flag(self, f):
    self.vars[f] = True

  def unset_flag(self, f):
    if f in self.vars:
      del self.vars[f]

  def do_say(self, s):
    self.output( s, FEEDBACK )
    return True

  def say(self, s):
    return (lambda s: lambda *args: self.do_say(s))(s)

  def do_say_on_noun(self, n, s, actor, noun, words):
    if noun != n:
      return False
    self.output( s, FEEDBACK )
    return True

  def say_on_noun(self, n, s):
    return (lambda n, s: lambda actor, noun, words: self.do_say_on_noun(n, s, actor, noun, words))(n, s)

  def say_on_self(self, s):
    return (lambda s: lambda actor, noun, words: self.do_say_on_noun(None, s, actor, noun, words))(s)

  def add_verb( self, verb, f ):
    self.verbs[' '.join(verb.split())] = f

  def get_verb( self, verb ):
    c = ' '.join(verb.split())
    if c in self.verbs:
       return self.verbs[c]
    else:
      return None

  def output(self, text, message_type = 0):
    self.game.output(text, message_type)


# The Game: container for hero, locations, robots, animals etc.
class Game(Base):
  def __init__(self, name="bwx-adventure"):
    Base.__init__(self, name)
    self.objects = {}
    self.fresh_location = False
    self.hero = None
    self.locations = {}
    self.robots = {}
    self.animals = {}

  def set_name(self, name):
    self.name = name

  # add a bidirectional connection between points A and B
  def add_connection( self, connection ):
    connection.game = self
    if isinstance(connection.way_ab, (list, tuple)):
      for way in connection.way_ab:
        connection.point_a.add_exit( connection, way )
    else:
      connection.point_a.add_exit( connection, connection.way_ab )

    # this is messy, need a better way to do this
    reverse_connection = Connection( connection.name, connection.point_b, connection.point_a, connection.way_ba, connection.way_ab)
    reverse_connection.game = self
    if isinstance(connection.way_ba, (list, tuple)):
      for way in connection.way_ba:
        connection.point_b.add_exit( reverse_connection, way )
    else:
      connection.point_b.add_exit( reverse_connection, connection.way_ba )
    return connection

  def new_connection(self, *args):
    return self.add_connection(Connection(*args))

  # add another location to the game
  def add_location(self,  location ):
    location.game = self
    self.locations[location.name] = location
    return location

  def new_location(self, *args):
    return self.add_location(Location(*args))

  # add an actor to the game
  def add_actor(self, actor):
    actor.game = self

    if isinstance(actor, Player):
      self.hero = actor

    if isinstance(actor, Animal):
      self.animals[actor.name] = actor

    if isinstance(actor, Robot):
      self.robots[actor.name] = actor

    return actor

  def add_player(self, location):
    player = Player()
    self.add_actor(player)
    player.set_location(location)
    return player

  def if_flag(self, flag, s_true, s_false, location = None):
    return lambda loc: (s_false, s_true)[flag in (location or loc).vars]

  def if_var(self, var, value, s_true, s_false, location = None):
    return lambda loc: (s_false, s_true)[var in (location or loc).var and (location or loc).vars[var] == value] 

  # overload this for HTTP output
  def output(self, text, message_type = 0):
    print_output(text, message_type)

  # checks to see if the inventory in the items list is in the user's inventory
  def inventory_contains(self, items):
    if set(items).issubset(set(self.hero.inventory.values())):
      return True
    return False

  def entering_location(self, location):
    if (self.hero.location == location and self.fresh_location):
        return True
    return False

  def run(self , update_func = False):

    # reset this every loop so we don't trigger things more than once
    self.fresh_location = False

    actor = self.hero
    while True:
      # if the actor moved, describe the room
      if actor.check_if_moved():
        self.output("        --=( %s %s in the %s )=--        " % (
          actor.name.capitalize(), actor.isare, actor.location.name), TITLE)

        # cache this as we need to know it for the query to entering_location()
        self.fresh_location = actor.location.first_time

        where = actor.location.describe(actor)
        if where:
          self.output( "" )
          self.output( where )
          self.output( "" )

      # See if the animals want to do anything
      for animal in self.animals.items():
        animal[1].act_autonomously(actor.location)

      # has the developer supplied an update function?
      if (update_func):
        update_func() # call the update function

      # check if we're currently running a script
      user_input = actor.get_next_script_line();
      if user_input == None:
        # get input from the user
        try:
          self.output("")  # add a blank line
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
            actor = self.robots[robot_name]
         except KeyError:
            self.output( "I don't know anybot named %s" % robot_name, FEEDBACK)
            continue
      else:
         actor = self.hero
         command = clean_user_input

      # give the input to the actor in case it's recording a script
      if not actor.set_next_script_line(command):
        continue

      words = command.split()
      if not words:
        continue

      # following the Infocom convention commands are decomposed into
      # VERB(verb), OBJECT(noun), INDIRECT_OBJECT(indirect).
      # For example: "hit zombie with hammer" = HIT(verb) ZOMBIE(noun) WITH HAMMER(indirect).

      target_name = ""
      if words[0].lower() == 'tell' and len(words) > 2:
        target_name = words[1]
        words = words[2:]

      verb = words[0]
      words = words[1:]

      noun = None
      if words:
        noun = words[0]
        words = words[1:]

      indirect = None
      if len(words) > 1 and words[0].lower() == 'with':
        indirect = words[0]
        words = words[2:]

      # if we have an explicit target of the verb, do that.
      # e.g. "tell cat eat foo" -> cat.eat( cat, 'food', [] )
      if target_name:
        done = False
        for a in actor.location.actors:
          if a.name != target_name:
            continue
          f = a.get_verb( verb )
          if f:
            if f( a, noun, words ):
              done = True
              break
        if done:
          continue
        self.output( "Huh? %s %s?" % (target_name, verb), FEEDBACK)
        continue

      # if we have an indirect object, try it's handle first
      # e.g. "hit cat with hammer" -> hammer.hit( actor, 'cat', [] )
      things = actor.inventory.values() + actor.location.contents.values()
      if indirect:
        # try inventory and room contents
        done = False
        for thing in things:
          if indirect == thing.name:
            f = thing.get_verb( verb )
            if f:
              if f( actor, noun, words ):
                done = True
                break
        if done:
          continue
        for a in actor.location.actors:
          if indirect == a.name:
            f = a.get_verb( verb )
            if f:
              if f( a, noun, words ):
                done = True
                break
        if done:
          continue

      # if we have a noun, try it's handler next
      if noun:
        done = False
        for thing in things:
          if noun == thing.name:
            f = thing.get_verb( verb )
            if f:
              if f( actor, None, words ):
                done = True
                break
        if done:
          continue
        for a in actor.location.actors:
          if noun == a.name:
            f = a.get_verb( verb )
            if f:
              if f( a, None, words ):
                done = True
                break
        if done:
          continue

      # location specific verb
      f = actor.location.get_verb(verb)
      if f:
        if f( actor.location, actor, noun, words ):
          continue

      # handle directional moves of the actor
      if not noun:
        if verb in directions:
          actor.act_go1( actor, verb, None )
          continue

      # general actor verb
      f = actor.get_verb( verb )
      if f:
        if f( actor, noun, words ):
          continue

      # not understood
      self.output( "Huh?", FEEDBACK )


class Object(Base):
  # name: short name of this thing
  # description: full description
  # fixed: is it stuck or can it be taken

  def __init__( self, name, desc, fixed=False ):
    Base.__init__(self, name)
    self.description = desc
    self.fixed = fixed

  def describe( self, observer ):
    return self.name


# A "location" is a place in the game.
class Location(Base):
  # name: short name of this location
  # description: full description
  # contents: things that are in a location
  # exits: ways to get out of a location
  # first_time: is it the first time here?
  # actors: other actors in the location

  def __init__( self, name, description):
    Base.__init__(self, name)
    self.description = description
    self.contents = {}
    self.exits = {}
    self.first_time = True
    self.actors = set()
    self.requirements = {}

  def add_object(self, obj):
    self.contents[obj.name] = obj
    return obj

  def description_str(self, d):
    if isinstance(d, (list, tuple)):
      desc = ""
      for dd in d:
        desc += self.description_str(dd)
      return desc
    else:
      if isinstance(d, str):
        return style_text(d,  DESCRIPTION)
      else:
        return self.description_str(d(self))

  def describe( self, observer, force=False ):
    desc = ""   # start with a blank string

    # add the description
    if self.first_time or force:
      desc += self.description_str(self.description)
      self.first_time = False

    if self.contents:
      # try to make a readable list of the things
      contents_description = proper_list_from_dict(self.contents)
      # is it just one thing?
      if len(self.contents) == 1:
        desc += style_text("\nThere is %s here." % contents_description, CONTENTS)
      else:
        desc += style_text("\nThere are a few things here: %s." % contents_description, CONTENTS)

    if self.actors:
      for a in self.actors:
        if a != observer:
          desc += style_text("\n" + add_article(a.describe(a)).capitalize() + " " + a.isare + " here.", CONTENTS)

    return desc

  def add_exit( self, con, way ):
    self.exits[ way ] = con

  def go( self, way ):
    if way in self.exits:
      c = self.exits[ way ]

      # check if there are any requirements for this room
      if len(c.point_b.requirements) > 0:
        # check to see if the requirements are in the inventory
        if set(c.point_b.requirements).issubset(set(self.game.hero.inventory)):
          self.output( "You use the %s, the %s unlocks" % (proper_list_from_dict(c.point_b.requirements), c.point_b.name), FEEDBACK)
          return c.point_b

        self.output( "It's locked! You will need %s." % proper_list_from_dict(c.point_b.requirements), FEEDBACK)
        return None
      else:
        return c.point_b
    else:
      return None

  def debug( self ):
    for key in self.exits:
      print "exit: %s" % key

  def make_requirement(self, thing):
      self.requirements[thing.name] = thing


# A "connection" connects point A to point B. Connections are
# always described from the point of view of point A.
class Connection(Base):
  # name
  # point_a
  # point_b

  def __init__( self, name, pa, pb, way_ab, way_ba):
    Base.__init__(self, name)
    self.point_a = pa
    self.point_b = pb
    self.way_ab = way_ab
    self.way_ba = way_ba


def act_many( f, actor, noun, words ):
  result = True
  if not f( actor, noun ):
    result = False
  # treat 'verb noun1 and noun2..' as 'verb noun1' then 'verb noun2'
  # treat 'verb noun1, noun2...' as 'verb noun1' then 'verb noun2'
  if words:
    for noun in words:
      noun = noun.strip(',')
      if noun in articles: continue
      if noun == 'and': continue
      if not f( actor, noun ):
        result = False
  return result


def act_multi( f ):
  return ((lambda f : (lambda a, n, w: act_many( f, a, n, w )))(f))


# An actor in the game
class Actor(Base):
  # location
  # inventory
  # moved
  # verbs

  def __init__( self, name, hero = False ):
    Base.__init__(self, name)
    self.location = None
    self.inventory = {}
    self.cap_name = name.capitalize()
    self.hero = hero
    if hero:
      self.isare = "are"
    else:
      self.isare = "is"
    # associate each of the known actions with functions
    self.verbs['take'] = act_multi(self.act_take1)
    self.verbs['get'] = act_multi(self.act_take1)
    self.verbs['drop'] = act_multi(self.act_drop1)
    self.verbs['inventory'] = self.act_inventory
    self.verbs['i'] = self.act_inventory
    self.verbs['look'] = self.act_look
    self.verbs['l'] = self.act_look
    self.verbs['go'] = self.act_go1
    self.verbs['verbs'] = self.act_list_verbs
    self.verbs['commands'] = self.act_list_verbs

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
  def act_take1( self, actor, noun):
    if not noun:
      return False
    t = self.location.contents.pop(noun, None)
    if t:
      self.inventory[noun] = t
      self.output("You take the %s." % t.name)
      return True
    else:
      self.output("%s can't take the %s." % (self.cap_name, noun))
      return False

  # move a thing from our inventory to the current location
  def act_drop1( self, actor, noun ):
    if not noun:
      return False
    t = self.inventory.pop(noun, None)
    if t:
      self.location.contents[noun] = t
      return True
    else:
      self.output( "%s %s not carrying %s." % (self.cap_name, self.isare, add_article(noun)), FEEDBACK)
      return False

  def act_look( self, actor, noun, words ):
    print self.location.describe( actor, True )
    return True

  # list the things we're carrying
  def act_inventory( self, actor, noun, words ):
    msg = '%s %s carrying ' % (self.cap_name, self.isare)
    if self.inventory.keys():
      msg += proper_list_from_dict( self.inventory )
    else:
      msg += 'nothing'
    msg += '.'
    self.output( msg, FEEDBACK)
    return True

  # check/clear moved status
  def check_if_moved( self ):
    status = self.moved
    self.moved = False
    return status

  # try to go in a given direction
  def act_go1( self, actor, noun, words ):
    if not noun in directions:
      self.output( "Don't know how to go '%s'." % noun, FEEDBACK )
      return False
    loc = self.location.go( directions[noun] )
    if loc == None:
      self.output( "Bonk! %s can't seem to go that way." % self.name, FEEDBACK)
      return False
    else:
      # update where we are
      self.set_location( loc )
      return True

  def act_list_verbs( self, actor, noun, words ):
    self.output( textwrap.fill(" ".join(sorted(self.verbs.keys()))), FEEDBACK )
    return True

  # support for scriptable actors, override these to implement
  def get_next_script_line( self ):
    return None

  def set_next_script_line( self, line ):
    return True



class Player(Actor):
  def __init__( self ):
    super(Player, self).__init__("you", True)

  def add_verb( self, name, f ):
    self.verbs[name] = (lambda self: lambda *args : f(self, *args))(self)


# Scripts are sequences of instructions for Robots to execute
class Script(Base):
  def __init__( self, name ):
    Base.__init__(self, name)
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
    if self.location == observer_loc:
      self.output("%s leaves the %s via the %s." % (add_article(self.name).capitalize(),
                                               observer_loc.name,
                                               exit[1].name), FEEDBACK)
    self.act_go1(self, direction_name[exit[0]], None)
    if self.location == observer_loc:
      self.output("%s enters the %s via the %s." % (add_article(self.name).capitalize(),
                                               observer_loc.name,
                                               exit[1].name), FEEDBACK)


# A pet is an actor with free will (Animal) that you can also command to do things (Robot)
class Pet(Robot, Animal):
  def __init__( self, name ):
    super(Pet, self ).__init__( name )
    self.leader = None
    self.verbs['heel'] = self.act_follow
    self.verbs['follow'] = self.act_follow
    self.verbs['stay'] = self.act_stay

  def act_follow(self, actor, words=None):
    self.leader = self.hero
    self.output( "%s obediently begins following %s" % (self.name, self.leader.name) , FEEDBACK)
    return True

  def act_stay(self, actor, words=None):
    if self.leader:
      self.output( "%s obediently stops following %s" % (self.name, self.leader.name) , FEEDBACK)
    self.leader = None
    return True

  def act_autonomously(self, observer_loc):
    if self.leader:
      self.set_location(self.leader.location)
    else:
      self.random_move(observer_loc)


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
def print_output(text, message_type = 0):
  print style_text(text, message_type)

# this makes the text look nice in the terminal... WITH COLORS!
def style_text(text, message_type):
  if (message_type == FEEDBACK):
    text = Colors.FG.pink + text + Colors.reset

  if (message_type == TITLE):
    text = Colors.FG.yellow + Colors.BG.blue + "\n" + text + Colors.reset

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
