#!/user/bin/python
# vim: et sw=2 ts=2 sts=2
#
# This is a tutorial for writing Interactive Fiction with the BWX Adventure Game Engine.
# Ignore the magic before this point (feel free to ask if you are curious).
#
# First we need to import everything we need from the Game engine (a module called 'advent'):

from advent import *
# for cloud9
from advent import Game, Location, Connection, Object, Animal, Robot, Pet, Player, Say
from advent import NORTH, SOUTH, EAST, WEST, UP, DOWN, RIGHT, LEFT, IN, OUT, FORWARD, BACK, NORTH_WEST, NORTH_EAST, SOUTH_WEST, SOUTH_EAST, NOT_DIRECTION


def make_game(name):
  game = Game(name)
  sidewalk = game.new_location("Sidewalk",
      "There is a large glass door to the east. The sign says 'Come In!'")
  vestibule = game.new_location("Vestibule",
      "A small area at the bottom of a flight of stairs.\nThere is a glass door to the west and a door to the south.")
  game.new_connection("Glass Door", sidewalk, vestibule, [IN, EAST], [OUT, WEST])
  office = game.new_location( "Office",
      "A nicely organized office.\nThere is a door to the north.")
  game.new_connection("Office Door", vestibule, office, [IN, SOUTH], [OUT, NORTH])
  key = sidewalk.new_object("key", "a small tarnished key")
  office.make_requirement(key)
  coin = sidewalk.new_object("coin", "a small coin");
  player = game.new_player(sidewalk)
  key.add_phrase("rub key", Say("You rub the key, but fail to shine it."))

  def flip_coin(game):
    if not "coin" in game.player.inventory:
      game.output("The coin is on the ground!")
      return
    if random.random() > 0.5:
      game.output("The coin shows heads.");
    else:
      game.output("The coin shows tails.");

  player.add_phrase("flip coin", flip_coin, [coin])
  return game

Game.register("ExampleHTTPGame", make_game);
