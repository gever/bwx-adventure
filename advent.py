# 
# adventure module
#
# vim: et sw=2 ts=2 sts=2

# for Python3, use:
# import urllib.request as urllib2
import urllib2

import random
import string
import textwrap
import time

# "directions" are all the ways you can describe going some way; 
# they are code-visible names for directions for adventure authors
direction_names = ["NORTH","SOUTH","EAST","WEST","UP","DOWN","RIGHT","LEFT",
                   "IN","OUT","FORWARD","BACK",
                   "NORTHWEST","NORTHEAST","SOUTHWEST","SOUTHEAST"]
direction_list  = [ NORTH,  SOUTH,  EAST,  WEST,  UP,  DOWN,  RIGHT,  LEFT,
                    IN,  OUT,  FORWARD,  BACK,
                    NORTHWEST,  NORTHEAST,  SOUTHWEST,  SOUTHEAST] = \
                    range(len(direction_names))
NOT_DIRECTION = None

# some old names, for backwards compatibility
(NORTH_WEST, NORTH_EAST, SOUTH_WEST, SOUTH_EAST) = \
             (NORTHWEST, NORTHEAST, SOUTHWEST, SOUTHEAST)

directions = dir_by_name = dict(zip(direction_names, direction_list))


def define_direction (number, name):
    if name in dir_by_name:
        exit("%s is already defined as %d" % (name, dir_by_name[name]))
    dir_by_name[name] = number

def lookup_dir (name):
    return dir_by_name.get(name, NOT_DIRECTION)

# add lower-case versions of all names in direction_names
for name in direction_names:
    define_direction(dir_by_name[name], name.lower())

# add common aliases:
# maybe the alias mechanism should be a more general
# (text-based?) mechanism that works for any command?!!!
common_aliases = [
    (NORTH, "n"),
    (SOUTH, "s"),
    (EAST, "e"),
    (WEST, "w"),
    (UP, "u"),
    (DOWN, "d"),
    (FORWARD, "fd"),
    (FORWARD, "fwd"),
    (FORWARD, "f"),
    (BACK, "bk"),
    (BACK, "b"),
    (NORTHWEST,"nw"),
    (NORTHEAST,"ne"),
    (SOUTHWEST,"sw"),
    (SOUTHEAST, "se")
]

for (k,v) in common_aliases:
    define_direction(k,v)

# define the pairs of opposite directions
opposite_by_dir = {}

def define_opposite_dirs (d1, d2):
  for dir in (d1, d2):
    opposite = opposite_by_dir.get(dir)
    if opposite is not None:
      exit("opposite for %s is already defined as %s" % (dir, opposite))
  opposite_by_dir[d1] = d2
  opposite_by_dir[d2] = d1

opposites = [(NORTH, SOUTH),
             (EAST, WEST),
             (UP, DOWN),
             (LEFT, RIGHT), 
             (IN, OUT),
             (FORWARD, BACK),
             (NORTHWEST, SOUTHEAST),
             (NORTHEAST, SOUTHWEST)]

for (d1,d2) in opposites:
  define_opposite_dirs(d1,d2)

def opposite_direction (dir):
  return opposite_by_dir[dir]


# registered games
registered_games = {}

FEEDBACK = 0
TITLE = 1
DESCRIPTION = 2
CONTENTS = 3
DEBUG = 4

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

articles = ['a', 'an', 'the']
# some prepositions to recognize indirect objects in prepositional phrases
prepositions = ['aboard', 'about', 'above', 'across', 'after', 'against', 'along'
    'among', 'around', 'at', 'atop', 'before', 'behind', 'below', 'beneath',
    'beside', 'besides', 'between', 'beyond', 'by', 'for', 'from', 'in', 'including'
    'inside', 'into', 'on', 'onto', 'outside', 'over', 'past', 'than' 'through', 'to',
    'toward', 'under', 'underneath',  'onto', 'upon', 'with', 'within']


# changes "lock" to "a lock", "apple" to "an apple", etc.
# note that no article should be added to proper names;
# For now we'll just assume
# anything starting with upper case is proper.
# Do not add an article to plural nouns.
def add_article (name):
  # simple plural test
  if len(name) > 1 and name[-1] == 's' and name[-2] != 's':
    return name
  # check if there is already an article on the string
  if name.split()[0] in articles:
    return name
  consonants = "bcdfghjklmnpqrstvwxyz"
  vowels = "aeiou"
  if name and (name[0] in vowels):
     article = "an "
  elif name and (name[0] in consonants):
     article = "a "
  else:
     article = ""
  return "%s%s" % (article, name)


def normalize_input(text):
  superfluous = articles +  ['and']
  rest = []
  for word in text.split():
    word = "".join(l for l in word if l not in string.punctuation)
    if word not in superfluous:
      rest.append(word)
  return ' '.join(rest)


def proper_list_from_dict(d):
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
    self.phrases = {}
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

  def var(self, var):
    if var in self.vars:
      return self.vars[var]
    else:
      return None

  def set_var(self, var, val):
    self.vars[var] = val

  def unset_var(self, var):
    if var in self.vars:
      del self.vars[var]

  def add_verb(self, v):
    self.verbs[' '.join(v.name.split())] = v
    v.bind_to(self)
    return v

  def get_verb(self, verb):
    c = ' '.join(verb.split())
    if c in self.verbs:
       return self.verbs[c]
    else:
      return None

  def add_phrase(self, phrase, f, requirements = []):
    if isinstance(f, BaseVerb):
      f.bind_to(self)
    self.phrases[' '.join(phrase.split())] = (f, set(requirements))

  def get_phrase(self, phrase, things_present):
    phrase = phrase.strip()
    things_present = set(things_present)
    if not phrase in self.phrases:
      return None
    p = self.phrases[phrase]
    if things_present.issuperset(p[1]):
      return p[0]
    return None

  def output(self, text, message_type = 0):
    self.game.output(text, message_type)

class BaseVerb(Base):
  def __init__(self, function, name):
    Base.__init__(self, name)
    self.function = function 
    self.bound_to = None
    
  def bind_to(self, obj):
    self.bound_to = obj
    
  def act(self, actor, noun, words):
    result = True
    if not self.function(actor, noun, None):
      result = False
    # treat 'verb noun1 and noun2..' as 'verb noun1' then 'verb noun2'
    # treat 'verb noun1, noun2...' as 'verb noun1' then 'verb noun2'
    # if any of the nouns work on the verb consider the command successful,
    # even if some of them don't
    if words:
      for noun in words:
        if self.function(actor, noun, None):
          result = True
    return result

class Die(BaseVerb):
  def __init__(self, string, name = ""):
    BaseVerb.__init__(self, None, name)
    self.string = string

  def act(self, actor, noun, words):
    self.bound_to.game.output("%s %s %s" % (actor.name.capitalize(),
                                            actor.isare, self.string), FEEDBACK)
    self.bound_to.game.output("%s %s dead." % (actor.name.capitalize(),
                                               actor.isare), FEEDBACK)
    actor.terminate()
    return True

class Say(BaseVerb):
  def __init__(self, string, name = ""):
    BaseVerb.__init__(self, None, name)
    self.string = string

  def act(self, actor, noun, words):
    self.bound_to.game.output(self.string, FEEDBACK)
    return True

class SayOnNoun(Say):    
  def __init__(self, string, noun, name = ""):
    Say.__init__(self, string, name)
    self.noun = noun

  def act(self, actor, noun, words):
    if self.noun != noun:
      return False
    self.bound_to.game.output(self.string, FEEDBACK)
    return True

class SayOnSelf(SayOnNoun):
  def __init__(self, string, name = ""):
    SayOnNoun.__init__(self, string, None, name)

# Verb is used for passing in an unbound global function to the constructor
class Verb(BaseVerb):
  def __init__(self, function, name = ""):
    BaseVerb.__init__(self, function, name)

  # explicitly pass in self to the unbound function
  def act(self, actor, noun, words):
    return self.function(self.bound_to, actor, noun, words)


def list_prefix(a, b):  # is a a prefix of b
  if not a:
    return True
  if not b:
    return False
  if a[0] != b[0]:
    return False
  return list_prefix(a[1:], b[1:])


def get_noun(words, things):
  if words[0] in articles:
    if len(words) > 1:
      done = False
      for t in things:
        n = t.name.split()
        if list_prefix(n, words[1:]):
          noun = t.name
          words = words[len(n)+1:]
          done = True
          break
      if not done:
        noun = words[1]
        words = words[2:]
  else:
    done = False
    for t in things:
      n = t.name.split()
      if list_prefix(n, words):
        noun = t.name
        words = words[len(n):]
        done = True
        break
    if not done:
      noun = words[0]
      words = words[1:]
  return (noun, words)


# A class to hold utility methods useful during game development, but
# not needed for normal game play.  Import the advent_devtools module
# to get the full version of the tools.
class DevToolsBase(object):
  def __init__(self):
    self.game = None

  def set_game(self, game):
    self.game = game
    
  def debug_output(self, text, level):
    return

  def start(self):
    return

global _devtools
_devtools = DevToolsBase()
  
def register_devtools(devtools):
  global _devtools
  _devtools = devtools
      
# The Game: container for hero, locations, robots, animals etc.
class Game(Base):
  def __init__(self, name="bwx-adventure"):
    Base.__init__(self, name)
    self.objects = {}
    self.fresh_location = False
    self.player = None
    self.current_actor = None
    self.location_list = []
    self.robots = {}
    self.animals = {}
    global _devtools
    self.devtools = _devtools
    self.devtools.set_game(self)
    self.http_output = False
    self.http_text = ""
    self.done = False

  def set_name(self, name):
    self.name = name

  # add a bidirectional connection between points A and B
  def add_connection(self, connection):
    connection.game = self
    if isinstance(connection.way_ab, (list, tuple)):
      for way in connection.way_ab:
        connection.point_a.add_exit(connection, way)
    else:
      connection.point_a.add_exit(connection, connection.way_ab)

    # this is messy, need a better way to do this
    reverse_connection = Connection(connection.name,
                                    connection.point_b,
                                    connection.point_a,
                                    connection.way_ba,
                                    connection.way_ab)
    reverse_connection.game = self
    if isinstance(connection.way_ba, (list, tuple)):
      for way in connection.way_ba:
        connection.point_b.add_exit(reverse_connection, way)
    else:
      connection.point_b.add_exit(reverse_connection, connection.way_ba)
    return connection

  def new_connection(self, *args):
    return self.add_connection(Connection(*args))

  def connect(self, place_a, place_b, way_ab, way_ba=None):
    """An easier-to use version of new_connection. It generates a
    connection name automatically from the two location names and also
    allows the second direction argument to be omitted.  If the second
    direction is omitted, it defaults to the opposite of the first
    direction."""
    name = place_a.name + "_to_" + place_b.name
    return self.new_connection(name, place_a, place_b, way_ab, way_ba)


  # add another location to the game
  def add_location(self,  location):
    location.game = self
    self.location_list.append(location)
    return location

  def new_location(self, *args):
    return self.add_location(Location(*args))

  # add an actor to the game
  def add_actor(self, actor):
    actor.game = self

    if isinstance(actor, Player):
      self.player = actor

    if isinstance(actor, Animal):
      self.animals[actor.name] = actor

    if isinstance(actor, Robot):
      self.robots[actor.name] = actor

    return actor

  def new_player(self, location):
    self.player = Player()
    self.add_actor(self.player)
    self.player.set_location(location)
    return self.player

  def if_flag(self, flag, s_true, s_false, location = None):
    return lambda loc: (s_false, s_true)[flag in (location or loc).vars]

  def if_var(self, v, value, s_true, s_false, location = None):
    return lambda loc: (s_false, s_true)[v in (location or loc).vars and (location or loc).vars[v] == value] 

  def output(self, text, message_type = 0):
    if message_type != DEBUG:
      self.current_actor.set_next_script_response(text)
    self.print_output(text, message_type)

  def style_text(self, text, message_type):
    if False: # trinket.io
      return text

    if self.http_output:
      if (message_type == FEEDBACK):
        text = "<font color='red'>" + text + '</font>'
      if (message_type == TITLE):
        text = "<font color='blue'>" + text + '</font>'
      if (message_type == DESCRIPTION):
        pass
      if (message_type == CONTENTS):
        text = "<font color='green'>" + text + '</font>'
      if (message_type == DEBUG):
        text = "<font color='orange'>" + text + '</font>'
      return text

    if (message_type == FEEDBACK):
      text = Colors.FG.pink + text + Colors.reset
    if (message_type == TITLE):
      text = Colors.FG.yellow + Colors.BG.blue + "\n" + text + Colors.reset
    if (message_type == DESCRIPTION):
      text = Colors.reset + text
    if (message_type == CONTENTS):
      text = Colors.FG.green + text + Colors.reset
    if (message_type == DEBUG):
      text = Colors.bold + Colors.FG.black + Colors.BG.orange + "\n" + text + Colors.reset
    return text

  # overload this for HTTP output
  def print_output(self, text, message_type = 0):
    if self.http_output:
      self.http_text += self.style_text(text, message_type) + "\n"
    else:
      print self.style_text(text, message_type)

  # checks to see if the inventory in the items list is in the user's inventory
  def inventory_contains(self, items):
    if set(items).issubset(set(self.player.inventory.values())):
      return True
    return False

  def entering_location(self, location):
    if (self.player.location == location and self.fresh_location):
        return True
    return False

  def say(self, s):
    return lambda game: game.output(s)

  @staticmethod
  def register(name, fn):
    global registered_games
    registered_games[name] = fn

  @staticmethod
  def get_registered_games():
    global registered_games
    return registered_games

  def run_init(self, update_func = None):
    # reset this every loop so we don't trigger things more than once
    self.fresh_location = False
    self.update_func = update_func
    self.current_actor = self.player
    self.devtools.start()

  def init_scripts(self):
    actor = self.current_actor
    script_name = self.var('script_name')
    if script_name != None:
      self.devtools.debug_output("script_name: " + script_name, 3)
      actor.act_load_file(actor, script_name, None)
      if self.flag('check'):
        actor.act_check_script(actor, script_name, None)
      else:
        actor.act_run_script(actor, script_name, None)

    recording_name = self.var('start_recording')
    if recording_name != None:
      self.devtools.debug_output("recording_name: " + recording_name, 3)
      actor.act_start_recording(actor, recording_name, None)
          
  def run_room(self):
    actor = self.current_actor
    if actor == self.player or actor.flag('verbose'):
      # if the actor moved, describe the room
      if actor.check_if_moved():
        self.output(actor.location.title(actor), TITLE)

        # cache this as we need to know it for the query to entering_location()
        self.fresh_location = actor.location.first_time

        where = actor.location.describe(actor, actor.flag('verbose'))
        if where:
          self.output("")
          self.output(where)
          self.output("")

    # See if the animals want to do anything
    for animal in self.animals.values():
      # first check that it is not dead
      if animal.health >= 0:
        animal.act_autonomously(actor.location)


  def run_step(self, cmd = None):
    self.http_text = ""
    actor = self.current_actor

    # has the developer supplied an update function?
    if self.update_func:
      self.update_func() # call the update function

    # check if we're currently running a script
    user_input = actor.get_next_script_command();
    if user_input == None:
      if cmd != None:
        user_input = cmd
      else:
        # get input from the user
        try:
          self.output("")  # add a blank line
          user_input = raw_input("> ")
        except EOFError:
          return False

    # see if the command is for a robot
    if ':' in user_input:
       robot_name, command = user_input.split(':')
       try:
          actor = self.robots[robot_name]
       except KeyError:
          self.output("I don't know anybot named %s" % robot_name, FEEDBACK)
          return True
    else:
       actor = self.player
       command = user_input

    self.current_actor = actor
                
    # now we're done with punctuation and other superfluous words like articles
    command = normalize_input(command)

    # see if we want to quit
    if command == 'q' or command == 'quit':
      return False

    # give the input to the actor in case it's recording a script
    if not actor.set_next_script_command(command):
      return True

    words = command.split()
    if not words:
      return True

    # following the Infocom convention commands are decomposed into
    # VERB(verb), OBJECT(noun), INDIRECT_OBJECT(indirect).
    # For example: "hit zombie with hammer" = HIT(verb) ZOMBIE(noun) WITH HAMMER(indirect).

    # handle 'tell XXX ... "
    target_name = ""
    if words[0].lower() == 'tell' and len(words) > 2:
      (target_name, words) = get_noun(words[1:], actor.location.actors.values())

    things = actor.inventory.values() + \
      actor.location.contents.values() + \
      actor.location.exits.values() + \
      list(actor.location.actors.values()) + \
      [actor.location] + \
      [actor]

    for c in actor.location.contents.values():
        if isinstance(c, Container) and c.is_open:
          things += c.contents.values()
      
    potential_verbs = []
    for t in things:
      potential_verbs += t.verbs.keys()

    # extract the VERB
    verb = None
    potential_verbs.sort(key=lambda key : -len(key))
    for v in potential_verbs:
      vv = v.split()
      if list_prefix(vv, words):
        verb = v
        words = words[len(vv):]
    if not verb:
      verb = words[0]
      words = words[1:]

    # extract the OBJECT
    noun = None
    if words:
      (noun, words) = get_noun(words, things)

    # extract INDIRECT (object) in phrase of the form VERB OBJECT PREPOSITION INDIRECT
    indirect = None
    if len(words) > 1 and words[0].lower() in prepositions:
      (indirect, words) = get_noun(words[1:], things)

    # first check phrases
    for thing in things:
      f = thing.get_phrase(command, things)
      if f:
        if isinstance(f, BaseVerb):
          if f.act(actor, noun, words):
            return True
        else:
          f(self, thing)
          return True

    # if we have an explicit target of the VERB, do that.
    # e.g. "tell cat eat foo" -> cat.eat(cat, 'food', [])
    if target_name:
      for a in actor.location.actors.values():
        if a.name != target_name:
          continue
        v = a.get_verb(verb)
        if v:
          if v.act(a, noun, words):
            return True
      self.output("Huh? %s %s?" % (target_name, verb), FEEDBACK)
      return True

    # if we have an INDIRECT object, try it's handle first
    # e.g. "hit cat with hammer" -> hammer.hit(actor, 'cat', [])
    if indirect:
      # try inventory and room contents
      things = actor.inventory.values() + actor.location.contents.values()
      for thing in things:
        if indirect == thing.name:
          v = thing.get_verb(verb)
          if v:
            if v.act(actor, noun, words):
              return True
      for a in actor.location.actors.values():
        if indirect == a.name:
          v = a.get_verb(verb)
          if v:
            if v.act(a, noun, words):
              return True

    # if we have a NOUN, try it's handler next
    if noun:
      for thing in things:
        if noun == thing.name:
          v = thing.get_verb(verb)
          if v:
            if v.act(actor, None, words):
              return True
      for a in actor.location.actors.values():
        if noun == a.name:
          v = a.get_verb(verb)
          if v:
            if v.act(a, None, words):
              return True

    # location specific VERB
    v = actor.location.get_verb(verb)
    if v:
      if v.act(actor, noun, words):
        return True

    # handle directional moves of the actor
    if not noun:
      if verb in directions:
        actor.act_go1(actor, verb, None)
        return True

    # general actor VERB
    v = actor.get_verb(verb)
    if v:
      if v.act(actor, noun, words):
        return True

    # not understood
    self.output("Huh?", FEEDBACK)
    return True

  def run(self , update_func = None):
    self.run_init(update_func)
    self.run_room() # just set the stage before we do any scripting
    self.init_scripts() # now we can set up scripts
    while True:
      if self.done:
          return
      self.run_room()
      if self.player.health < 0:
        self.output ("Better luck next time!")
        break
      if not self.run_step():
        break
    self.output("\ngoodbye!\n", FEEDBACK)


class Object(Base):
  # name: short name of this thing
  # description: full description
  # fixed: is it stuck or can it be taken

  def __init__(self, name, desc, fixed=False):
    Base.__init__(self, name)
    self.description = desc
    self.fixed = fixed

  def describe(self, observer):
    if isinstance(self.description, str):
      return self.description
    else:
      return self.description(self)

class Consumable(Object):
  def __init__(self, name, desc, verb, replacement = None):
    Object.__init__(self, name, desc)
    self.verb = verb
    verb.bind_to(self)
    self.consume_term = "consume"
    self.replacement = replacement
    
  def consume(self, actor, noun, words):
    if not actor.location.replace_object(actor, self.name, self.replacement):
      return False
    
    self.output("%s %s%s %s." % (actor.name.capitalize(), self.consume_term,
                                 actor.verborverbs, self.description))
    self.verb.act(actor, noun, words)
    return True
    
class Food(Consumable):
  def __init__(self, name, desc, verb, replacement = None):
    Consumable.__init__(self, name, desc, verb, replacement)
    self.consume_term = "eat"
    
class Drink(Consumable):
  def __init__(self, name, desc, verb, replacement = None):
    Consumable.__init__(self, name, desc, verb, replacement)
    self.consume_term = "drink"

class Lockable(Base):
  def __init__(self, name):
    Base.__init__(self, name)
    self.requirements = {}
  
  def make_requirement(self, thing):
    self.requirements[thing.name] = thing
    self.lock()
      
  def lock(self):
    self.set_flag('locked')

  def unlock(self):
    self.unset_flag('locked')

  def is_locked(self):
    return self.flag('locked')
    
  def try_unlock(self, actor):
    # first see if the actor is whitelisted
    if isinstance(self, Location) and actor.allowed_locs:
      if not self in actor.allowed_locs:
        return False

    # now check if we're locked
    if not self.flag('locked'):
      return True
    
    # check if there are any implicit requirements for this object
    if len(self.requirements) == 0:
      self.output("It's locked!")
      return False

    # check to see if the requirements are in the inventory
    if set(self.requirements).issubset(set(actor.inventory)):
      self.output("You use the %s, the %s unlocks" % \
                  (proper_list_from_dict(self.requirements),
                  self.name), FEEDBACK)
      self.unlock()
      return True

    self.output("It's locked! You will need %s." % \
                proper_list_from_dict(self.requirements), FEEDBACK)
    return False

class Container(Lockable):
  def __init__(self, name, description):
    Lockable.__init__(self, name)
    self.description = description
    self.first_time = True
    self.contents = {}
    self.close()

  def add_object(self, obj):
    self.contents[obj.name] = obj
    obj.game = self.game
    return obj

  def new_object(self, name, desc, fixed=False):
    return self.add_object(Object(name, desc, fixed))

  def describe(self, observer, force=False):
    desc = ""   # start with a blank string

    # add the description
    if self.first_time or force:
      desc += self.description
      self.first_time = False
    else:
      desc += add_article(self.name)

    if not self.is_open():
      desc += " The %s is closed." % self.name
    else:
      desc += " The %s is open." % self.name
      # it's open so describe the contents
      desc += self.describe_contents()
    return desc
    
  def describe_contents(self):
    desc = ""
    if not self.contents:
      return desc
    
    # try to make a readable list of the things
    contents_description = proper_list_from_dict(self.contents)
    # is it just one thing?
    if len(self.contents) == 1:
      desc += self.game.style_text("\nThere is %s in the %s." % \
                                   (contents_description, self.name), CONTENTS)
    else:
      desc += self.game.style_text("\nThere are a few things in the %s: %s." % \
                                   (self.name, contents_description), CONTENTS)

    return desc

  def open(self, actor):
    if self.is_open():
      self.output("The %s is already open." % self.name)
      return True
    if not self.try_unlock(actor):
      return False
    self.output("The %s opens." % self.name, FEEDBACK)
    self.output(self.describe_contents(), CONTENTS)
    self.unset_flag('closed')

  def close(self):
    self.set_flag('closed')

  def is_open(self):
    return not self.flag('closed')

        
# A "location" is a place in the game.
class Location(Lockable):
  # name: short name of this location
  # description: full description
  # contents: things that are in a location
  # exits: ways to get out of a location
  # first_time: is it the first time here?
  # actors: other actors in the location

  def __init__(self, name, description, inonat="in"):
    Lockable.__init__(self, name)
    self.description = description
    self.inonat = inonat
    self.contents = {}
    self.exits = {}
    self.first_time = True
    self.actors = {}

  def title(self, actor):
    preamble = ""
    if (actor != self.game.player):
      preamble = "%s %s %s the " % (actor.name.capitalize(), actor.isare, self.inonat)
    return "        --=( %s%s )=--        " % (preamble, self.name)

  def add_object(self, obj):
    self.contents[obj.name] = obj
    obj.game = self.game
    return obj

  def add_actor(self, actor):
    actor.set_location(self)
    return actor

  def new_object(self, name, desc, fixed=False):
    return self.add_object(Object(name, desc, fixed))

  def description_str(self, d):
    if isinstance(d, (list, tuple)):
      desc = ""
      for dd in d:
        desc += self.description_str(dd)
      return desc
    else:
      if isinstance(d, str):
        return self.game.style_text(d,  DESCRIPTION)
      else:
        return self.description_str(d(self))

  def describe(self, observer, force=False):
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
        desc += self.game.style_text("\nThere is %s here." % \
                                     contents_description, CONTENTS)
      else:
        desc += self.game.style_text("\nThere are a few things here: %s." % \
                                     contents_description, CONTENTS)
      for k in sorted(self.contents.keys()):
        c = self.contents[k]
        if isinstance(c, Container) and c.is_open():
          desc += c.describe_contents()
                                     
    if self.actors:
      for k in sorted(self.actors.keys()):
        a = self.actors[k]
        if a.health < 0:
          deadornot = "lying here dead as a doornail"
        else:
          deadornot = "here"
        if a != observer:
          desc += self.game.style_text("\n" + add_article(a.describe(a)).capitalize() + \
                                       " " + a.isare + " " + deadornot + ".", CONTENTS)

    return desc

  def find_object(self, actor, name):
    if not name:
      return None
    if self.contents:
      if name in self.contents.keys():
        return self.contents
      for c in self.contents.values():
        if isinstance(c, Container) and c.is_open() and name in c.contents.keys():
          return c.contents
    if name in actor.inventory:
      return actor.inventory
    return None

  def replace_object(self, actor, old_name, new_obj):
    d = self.find_object(actor, old_name)
    if d == None:
      return None
    if not old_name in d.keys():
      return None
    old_obj = d[old_name]
    del d[old_name]
    if new_obj:
      d[new_obj.name] = new_obj
    return old_obj
    
  def add_exit(self, con, way):
    self.exits[ way ] = con

  def go(self, actor, way):
    if not way in self.exits:
      return None
    
    c = self.exits[ way ]

    # first check if the connection is locked
    if not c.try_unlock(actor):
      return None

    # check if the room on the other side is locked        
    if not c.point_b.try_unlock(actor):
      return None

    return c.point_b

  def debug(self):
    for key in self.exits:
      print "exit: %s" % key


# A "connection" connects point A to point B. Connections are
# always described from the point of view of point A.
class Connection(Lockable):
  # name
  # point_a
  # point_b

  def __init__(self, name, pa, pb, way_ab, way_ba=None):
    Lockable.__init__(self, name)
    # way_ba defaults to the opposite of way_ab
    if way_ba is None:
        way_ba = ([opposite_direction(way) for way in way_ab]
                  if isinstance(way_ab, (list, tuple))
                  else opposite_direction(way_ab))
    self.point_a = pa
    self.point_b = pb
    self.way_ab = way_ab
    self.way_ba = way_ba


# An actor in the game
class Actor(Base):
  # location
  # inventory
  # moved
  # verbs

  def __init__(self, name):
    Base.__init__(self, name)
    self.health = 0
    self.location = None
    self.allowed_locs = None
    self.inventory = {}
    self.cap_name = name.capitalize()
    self.player = False
    self.isare = "is"
    self.verborverbs = "s"
    self.trades = {}
    # associate each of the known actions with functions
    self.add_verb(BaseVerb(self.act_take1, 'take'))
    self.add_verb(BaseVerb(self.act_take1, 'get'))
    self.add_verb(BaseVerb(self.act_drop1, 'drop'))
    self.add_verb(BaseVerb(self.act_give, 'give'))
    self.add_verb(BaseVerb(self.act_inventory, 'inventory'))
    self.add_verb(BaseVerb(self.act_inventory, 'i'))
    self.add_verb(BaseVerb(self.act_look, 'look'))
    self.add_verb(BaseVerb(self.act_examine1, 'examine'))
    self.add_verb(BaseVerb(self.act_examine1, 'look at'))
    self.add_verb(BaseVerb(self.act_look, 'l'))
    self.add_verb(BaseVerb(self.act_go1, 'go'))
    self.add_verb(BaseVerb(self.act_eat, 'eat'))
    self.add_verb(BaseVerb(self.act_drink, 'drink'))
    self.add_verb(BaseVerb(self.act_open, 'open'))
    self.add_verb(BaseVerb(self.act_list_verbs, 'verbs'))
    self.add_verb(BaseVerb(self.act_list_verbs, 'commands'))

  # terminate
  def terminate(self):
    self.health = -1
    
  # describe ourselves
  def describe(self, observer):
    return self.name

  # establish where we are "now"
  def set_location(self, loc):
    self.game = loc.game # XXX this is a hack do this better
    if not self.player and self.location:
      del self.location.actors[self.name]
    self.location = loc
    self.moved = True
    if not self.player:
      self.location.actors[self.name] = self

  # confine this actor to a list of locations
  def set_allowed_locations(self, locs):
    self.allowed_locs = locs

  # add something to our inventory
  def add_to_inventory(self, thing):
    self.inventory[thing.name] = thing
    return thing

  # remove something from our inventory
  def remove_from_inventory(self, thing):
    return self.inventory.pop(thing.name, None)
    
  # set up a trade
  def add_trade(self, received_obj, returned_obj, verb):
    verb.bind_to(self)
    self.trades[received_obj] = (returned_obj, verb)

  # receive a given object
  def receive_item(self, giver, thing):
    self.add_to_inventory(thing)
    if thing in self.trades.keys():
      (obj, verb) = self.trades[thing]
      verb.act(giver, thing.name, None)
      self.location.contents[obj.name] = obj
      self.remove_from_inventory(obj)

  # give something to another actor
  def act_give(self, actor, noun, words):
    d = actor.location.find_object(actor, noun)
    if not d:
      return False
    thing = d[noun]

    receiver = self
    if words:
      for w in words:
        if w in self.location.actors.keys():
          receiver = self.location.actors[w]
          break

    if not receiver:
      return False

    receiver.receive_item(actor, thing)
    del d[thing.name]
    return True
      
  # move a thing from the current location to our inventory
  def act_take1(self, actor, noun, words):
    if not noun:
      return False
    t = self.location.contents.pop(noun, None)
    if not t:
      for c in self.location.contents.values():
        if isinstance(c, Container) and c.is_open:
          t = c.contents.pop(noun, None)      
    if t:
      self.inventory[noun] = t
      self.output("%s take%s the %s." % (actor.cap_name,
                                         actor.verborverbs,
                                         t.name))
      return True
    else:
      self.output("%s can't take the %s." % (actor.cap_name, noun))
      return False

  # move a thing from our inventory to the current location
  def act_drop1(self, actor, noun, words):
    if not noun:
      return False
    t = self.inventory.pop(noun, None)
    if t:
      self.location.contents[noun] = t
      return True
    else:
      self.output("%s %s not carrying %s." % (self.cap_name, self.isare, add_article(noun)), FEEDBACK)
      return False

  def act_look(self, actor, noun, words):
    self.output(self.location.describe(actor, True))
    return True

  # examine a thing in our inventory or location
  def act_examine1(self, actor, noun, words):
    if not noun:
      return False
    n = None
    if noun in self.inventory:
      n = self.inventory[noun]
    if noun in self.location.contents:
      n = self.location.contents[noun]
    for c in self.location.contents.values():
      if isinstance(c, Container) and c.is_open:
        if noun in c.contents:
          n = c.contents[noun]
    if not n:
      return False
    self.output("You see " + n.describe(self) + ".")
    return True

  # list the things we're carrying
  def act_inventory(self, actor, noun, words):
    msg = '%s %s carrying ' % (self.cap_name, self.isare)
    if self.inventory.keys():
      msg += proper_list_from_dict(self.inventory)
    else:
      msg += 'nothing'
    msg += '.'
    self.output(msg, FEEDBACK)
    return True

  # check/clear moved status
  def check_if_moved(self):
    status = self.moved
    self.moved = False
    return status

  # try to go in a given direction
  def act_go1(self, actor, noun, words):
    if not noun in directions:
      self.output("Don't know how to go '%s'." % noun, FEEDBACK)
      return False
    loc = self.location.go(actor, directions[noun])
    if loc == None:
      self.output("Bonk! %s can't seem to go that way." % self.name, FEEDBACK)
      return False
    else:
      # update where we are
      self.set_location(loc)
      return True

  # eat something
  def act_eat(self, actor, noun, words):
    d = actor.location.find_object(actor, noun)
    if not d:
      return False
    t = d[noun]
    
    if isinstance(t, Food):
      t.consume(actor, noun, words)
    else:
      self.output("%s can't eat the %s." % (actor.name.capitalize(), noun))

    return True

  # drink something
  def act_drink(self, actor, noun, words):
    d = actor.location.find_object(actor, noun)
    if not d:
      return False
    t = d[noun]
    
    if isinstance(t, Drink):
      t.consume(actor, noun, words)
    else:
      self.output("%s can't drink the %s." % (actor.name.capitalize(), noun))

    return True

  # open a Container
  def act_open(self, actor, noun, words):
    if not noun:
      return False
    if not noun in actor.location.contents:
      return False
    
    t = self.location.contents[noun]
    if isinstance(t, Container):
      t.open(actor)
    else:
      self.output("%s can't open the %s." % (actor.name.capitalize(), noun))

    return True

  def act_list_verbs(self, actor, noun, words):
    things = (actor.inventory.values() + actor.location.contents.values() +
       list(actor.location.actors.values()) + [actor.location] + [actor])
    result = set()
    for t in things:
      for v in t.verbs.keys():
        if len(v.split()) > 1:
          result.add('"' + v + '"')
        else:
          result.add(v);
      for v in t.phrases.keys():
        if len(v.split()) > 1:
          result.add('"' + v + '"')
        else:
          result.add(v);
    self.output(textwrap.fill(" ".join(sorted(result))), FEEDBACK)
    return True

  # support for scriptable actors, override these to implement
  def get_next_script_command(self):
    return None

  def set_next_script_command(self, line):
    return True

  def set_next_script_response(self, response):
    return True
  
# Scripts are sequences of instructions for Robots to execute
class Script(Base):
  def __init__(self, name, lines=None, game=None):
    Base.__init__(self, name)
    self.game = game
    self.commands = list()
    self.responses = list()
    self.current_response = None
    self.check_responses = False
    self.mismatched_responses = -1
    self.current_command = -1
    self.recording = False
    self.running = False
    self.start_time = None
    self.finish_time = None
    self.response_errors = 0
    self.parse_lines(lines)

  def parse_lines(self, lines):
    if lines != None:
      self.start_recording()
      for line in lines.split("\n"):
        if line.startswith("> "):
          # save the new command, and any accumulated response from previous
          self.set_next_command(line.strip("> \n"))
        elif self.current_response != None:
          # accumulate response lines until the next command
          self.current_response += line + "\n"
        else:
          self.current_response = line + "\n"
      # if we didn't manage to get "end" go ahead and stop things brute force
      if self.recording:
        self.stop_recording()
    
  def start_recording(self):
    assert not self.running
    assert not self.recording
    self.current_response = None
    self.responses = list()
    self.commands = list()
    self.recording = True

  def stop_recording(self):
    assert self.recording
    assert not self.running
    self.current_response = None
    self.recording = False

  def start_running(self):
    assert not self.running
    assert not self.recording
    self.current_response = None
    self.check_responses = False
    self.running = True
    self.current_command = 0
    self.mismatched_responses = 0
    self.start_time = time.time()

  def start_checking(self):
    assert self.running
    assert not self.recording
    print "check_responses on"
    self.check_responses = True
    self.current_response = ""

  def stop_running(self):
    assert self.running
    assert not self.recording
    self.stop_time = time.time()
    self.game.devtools.debug_output(
      "script \"%s\":\n\tcommands: %d\n\tmismatched responses: %d\n\truntime: %f %s\n" % (
        self.name, self.current_command, self.mismatched_responses,
        (self.stop_time - self.start_time) * 1000, "milliseconds"), 0)
    self.current_response = None
    self.check_responses = False
    self.running = False
    self.current_command = -1
    if self.mismatched_responses != 0:
      assert(not self.game.flag('fail_on_mismatch'))

  def get_next_command(self):
    # if we're running a checker, examine the current response vs what's expected
    if self.current_command >= 1:
      self.check_response_match(self.current_response,
                                self.responses[self.current_command - 1])
      self.current_response = ""

    if not self.commands:
      return None
      
    while True:
      line = self.commands[self.current_command].strip()
      self.current_command += 1
      # support comments and/or blank lines within the script
      line = line.split("#")[0]
      if line != "":
        break 
    if line == "end":
      self.stop_running()
      return None
    return line

  def check_response_match(self, response, expected_response):
    if self.check_responses:
      match = "match"
      level = 2
      if response != expected_response:
        match = "mismatch"
        level = 0
        self.mismatched_responses += 1

      self.game.devtools.debug_output(
        "response %s:\n>>>\n%s\n===\n%s\n<<<\n" % (match,
                                                   response,
                                                   expected_response),
        level)
      
  
  def set_next_command(self, command):
    if not self.recording:
      return True
    
    # save the accumulated response from the previous command
    if self.current_response != None:
      # append the response, trimming the final newline that preceded this command
      self.responses.append(self.current_response[:-1])
    self.current_response = ""

    # save the current command
    self.commands.append(command)
    if command.strip() == "end":
      self.stop_recording()
      return False
    self.current_command += 1
      
    return True

  def set_next_response(self, response):
    if self.current_response != None:
      # strip out color changing chars which may be in there
      control_chars = False
      for c in response:
        if c == '\33':
          control_chars = True
        if control_chars:
          if c == 'm':
            control_chars = False
          continue
        self.current_response += c
      self.current_response += "\n"
      
  def print_script(self):
    i = 0
    for command in self.commands:
      print "> " + command
      if command == "end":
        break
      print self.responses[i]
      i = i + 1

  def save_file(self):
    f = open(self.name + ".script", "w")
    i = 0
    for command in self.commands:
      f.write('> ' + command + '\n')
      if command != "end":
        response_lines = self.responses[i].split('\n')
        for line in response_lines:
          f.write(line + '\n')
      i = i + 1
    f.close()

  def load_file(self):
    f = open(self.name + ".script", "r")
    self.parse_lines(f.read())
    f.close()


# Robots are actors which accept commands to perform actions.
# They can also record and run scripts.
class Robot(Actor):
  def __init__(self, name):
    #super(Robot, self).__init__(name )
    Actor.__init__(self, name)
    self.name = name
    self.scripts = {}
    self.current_script = None
    self.script_think_time = 0
    self.add_verb(BaseVerb(self.act_start_recording, 'record'))
    self.add_verb(BaseVerb(self.act_run_script, 'run'))
    self.add_verb(BaseVerb(self.act_check_script, 'check'))
    self.add_verb(BaseVerb(self.act_print_script, 'print'))
    self.add_verb(BaseVerb(self.act_save_file, 'save'))
    self.add_verb(BaseVerb(self.act_load_file, 'load'))
    self.add_verb(BaseVerb(self.set_think_time, 'think'))
    self.add_verb(BaseVerb(self.toggle_verbosity, 'verbose'))
    self.leader = None
    self.add_verb(BaseVerb(self.act_follow, 'heel'))
    self.add_verb(BaseVerb(self.act_follow, 'follow'))
    self.add_verb(BaseVerb(self.act_stay, 'stay'))

  def act_follow(self, actor, noun, words=None):
    if noun == None or noun == "" or noun == "me":
      self.leader = self.game.player
    elif noun in self.game.robots:
      self.leader = self.game.robots[noun]
    elif noun in self.game.animals:
      self.leader = self.game.animals[noun]
    self.output("%s obediently begins following %s" % \
                (self.name, self.leader.name) , FEEDBACK)
    return True

  def act_stay(self, actor, noun, words=None):
    if self.leader:
      self.output("%s obediently stops following %s" % \
                  (self.name, self.leader.name) , FEEDBACK)
    self.leader = None
    return True

  def toggle_verbosity(self, actor, noun, words):
    if self.flag('verbose'):
      self.unset_flag('verbose')
      self.output("minimal verbosity")
    else:
      self.set_flag('verbose')
      self.output("maximum verbosity")
    return True

  def parse_script_name(self, noun):
    if not noun:
        script_name = "default"
    else:
        script_name = noun
    return script_name

  def act_start_recording(self, actor, noun, words):
    script_name = self.parse_script_name(noun)
    self.set_flag('verbose')
    self.game.devtools.debug_output("start recording %s" % script_name, 2)
    script = Script(script_name, None, self.game)
    self.scripts[script_name] = script
    script.start_recording()
    self.current_script = script
    return True

  def act_run_script(self, actor, noun, words):
    if self.current_script:
      print "You must stop \"%s\" first." % (self.current_script.name)
    script_name = self.parse_script_name(noun)
    if not script_name in self.scripts:
      print "%s can't find script \"%s\" in its memory." % (self.name,
                                                            script_name)

      return True;
    
    self.game.devtools.debug_output("start running %s" % script_name, 2)
    script = self.scripts[script_name]
    self.current_script = script
    script.start_running()
    return True

  def act_check_script(self, actor, noun, words):
    if self.act_run_script(actor, noun, words):
      self.set_flag('verbose')
      self.current_script.start_checking()
      self.game.devtools.debug_output("start checking", 2)
      return True
    return False
  
  def act_print_script(self, actor, noun, words):
    script_name = self.parse_script_name(noun)
    if not script_name in self.scripts:
      print "%s can't find script \"%s\" in its memory." % (self.name,
                                                              script_name)
      return True

    print "----------------------8<-------------------------\n"
    print "# Paste the following into your game code in order"
    print "# to be able to run this script in the game:"
    print "%s_script = Script(\"%s\"," % (script_name, script_name)
    print "\"\"\""
    self.scripts[script_name].print_script()
    print "\"\"\")"
    print "\n# Then add the script to a player, or a robot"
    print "# with code like the following:"
    print "player.add_script(%s_script)" % script_name
    print "\n# Now you can run the script from within the game"
    print "# by typing \"run %s\"" % script_name
    print "\n---------------------->8-------------------------"
    return True

  def act_save_file(self, actor, noun, words):
    script_name = self.parse_script_name(noun)
    if not script_name in self.scripts:
      print "%s can't find script \"%s\" in its memory." % (self.name,
                                                            script_name)
      return True
    self.scripts[script_name].save_file()
    return True

  def act_load_file(self, actor, noun, words):
    script_name = self.parse_script_name(noun)
    self.scripts[script_name] = Script(script_name, None, self.game)
    self.scripts[script_name].load_file()
    return True

  def add_script(self, script):
    script.game = self.game
    self.scripts[script.name] = script    
  
  def set_think_time(self, actor, noun, words):
    if noun:
      t = float(noun)
      if t >= 0 and t <= 60:
          self.script_think_time = t
          return True

    print "\"think\" requires a number of seconds (0.0000-60.0000) as an argument"
    return True

  def get_next_script_command(self):
    if not self.current_script or not self.current_script.running:
      return None
    line = self.current_script.get_next_command()
    if not line:
      print "%s %s done running script \"%s\"." % (self.name,
                                                   self.isare,
                                                   self.current_script.name)
      self.current_script = None
      return None
    if self.script_think_time > 0:
      time.sleep(self.script_think_time)
    line = self.name + ": " + line
    print "> %s" % line
    return line

  def set_next_script_command(self, command):
    if not self.current_script:
      return True
    if not self.current_script.set_next_command(command):
      print "%s finished recording script \"%s\"." % (self.name,
                                                      self.current_script.name)
      self.current_script = None
      return False
    return True

  def set_next_script_response(self, response):
    if not self.current_script:
      return True
    self.current_script.set_next_response(response)
    return True


# Player derives from Robot so that we can record and run scripts as the player
class Player(Robot):
  def __init__(self):
    # super(Player, self).__init__("you")
    Robot.__init__(self, "you")
    self.player = True
    self.isare = "are"
    self.verborverbs = ""

# Animals are actors which may act autonomously each turn
class Animal(Actor):
  def __init__(self, name):
    #super(Animal, self).__init__(name )
    Actor.__init__(self, name)
    
  def act_autonomously(self, observer_loc):
    self.random_move(observer_loc)

  def random_move(self, observer_loc):
    if random.random() > 0.2:  # only move 1 in 5 times
      return

    # filter out any locked or forbidden locations
    exits = list()
    for (d, c) in self.location.exits.items():
      if c.is_locked():
        continue
      if c.point_b.is_locked():
        continue
      if self.allowed_locs and not c.point_b in self.allowed_locs:
        continue
      exits.append((d ,c))
    if not exits:
      return
    (exitDir, exitConn) = random.choice(exits)
    quiet = True
    if self.game.current_actor == self.game.player:
      quiet = False
    if self.game.current_actor.flag('verbose'):
      quiet = False
    if not quiet and self.location == observer_loc:
      self.output("%s leaves the %s, heading %s." % \
                  (add_article(self.name).capitalize(),
                   observer_loc.name,
                   direction_names[exitDir].lower()), FEEDBACK)
    self.act_go1(self, direction_names[exitDir], None)
    if not quiet and self.location == observer_loc:
      self.output("%s enters the %s via the %s." % (add_article(self.name).capitalize(),
                                               observer_loc.name,
                                               exitConn.name), FEEDBACK)


# A pet is an actor with free will (Animal) that you can also command to do things (Robot)
class Pet(Robot, Animal):
  def __init__(self, name):
    #super(Pet, self).__init__(name )
    Robot.__init__(self, name)

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
    net_f = self.opener.open('http://%s:%s/%s/%s.raw' % (self.hostname, self.port, cmd, k))
    v = net_f.read().split('\n')
    if len(v) > 1:
       return v[1].strip()
    return None

  def _do1(self, domain, cmd, key, arg1):
    assert(domain in self.key_fns)
    if not self.is_available():
      return None
    k = self.key_fns[domain](key)
    net_f = self.opener.open('http://%s:%s/%s/%s/%s.raw' % (self.hostname, self.port, cmd, k, arg1))
    v = net_f.read().split('\n')
    if len(v) > 1:
       return v[1]  # should be ""
    return None

  def _do2(self, domain, cmd, key, arg1, arg2):
    assert(domain in self.key_fns)
    if not self.is_available():
      return None
    k = self.key_fns[domain](key)
    net_f = self.opener.open('http://%s:%s/%s/%s/%s/%s.raw' % (self.hostname, self.port, cmd, k, arg1, arg2))
    v = net_f.read().split('\n')
    if len(v) > 1:
       return v[1]  # should be ""
    return None

  # return a list
  def _do2l(self, domain, cmd, key, arg1, arg2):
    assert(domain in self.key_fns)
    if not self.is_available():
      return []
    k = self.key_fns[domain](key)
    net_f = self.opener.open('http://%s:%s/%s/%s/%s/%s.raw' % (self.hostname, self.port, cmd, k, arg1, arg2))
    v = net_f.read().split('\n')
    return v

  # return a list
  def _do3l(self, domain, cmd, key, arg1, arg2, arg3):
    assert(domain in self.key_fns)
    if not self.is_available():
      return []
    k = self.key_fns[domain](key)
    net_f = self.opener.open('http://%s:%s/%s/%s/%s/%s/%s.raw' % (self.hostname, self.port, cmd, k, arg1, arg2, arg3))
    v = net_f.read().split('\n')
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


