from collections import defaultdict
from advent import NORTH, SOUTH, EAST, WEST, \
                   NORTHWEST, NORTHEAST, SOUTHWEST, SOUTHEAST, \
                   direction_names

"""
This module defines write_as_dot, which writes a file in the .dot
format.  The open source GraphViz command-line tools (or online
interfaces to it such as http://graphviz-dev.appspot.com) can then be
used to render the graph in many different bitmap and vector formats
(e.g. png, gif, jpg, pdf, svg, ...).
"""

############
# Helpers

def munge_name (name):
  """Remove code-unfriendly characters"""
  return "".join(c for c in name if c not in " ,_-")

def get_abbr (dir):
  """Abbreviate a direction. Return 'n' for NORTH, 'nw' for NORTHWEST, etc."""
  abbr_by_compound_dir = {NORTHWEST : "nw",
                          NORTHEAST : "ne",
                          SOUTHWEST : "sw",
                          SOUTHEAST : "se"}
  rv = abbr_by_compound_dir.get(dir)
  return rv or direction_names[dir][0].lower()
  

def get_label (dirs):
  """Return e.g. 'n/in' if dirs is [NORTH, IN]."""
  return "/".join(get_abbr(dir) for dir in dirs)


############
# Public API: write_as_dot

def write_as_dot (game, file_name=None):
  """
  Call this from your game before doing game.run().
  Then after you quit, do the following:
      dot -Tpng game.dot > game.png
  Or if you don't have GraphViz, paste the contents of game.dot
  into a web form like this one:
      http://graphviz-dev.appspot.com
  Behold your map.  Or something vaguely resembling how your map would
  look after going through a blender.
  """
  # define helper for printing to the .dot file
  f = open(file_name, 'w') if file_name else None
  def _dot (line):
    print >> f, line
  # get node names by munging loc names (bail if any are dups)
  node_name_set = set()
  node_name_by_loc = {}
  for (name, loc) in game.locations.items():
    nodeName = munge_name(loc.name)
    assert nodeName not in node_name_set, (nodeName, node_name_set)
    node_name_by_loc[loc] = nodeName
  # write header and node defaults
  _dot("digraph game {")
  _dot("  node [shape=rect, style=rounded];")
  # write locations as nodes
  _dot("  // nodes")
  for loc in game.locations.values():
    _dot('  %s [label="%s"];' % (node_name_by_loc[loc], loc.name))
  # write connections as edges:
  _dot("  // edges")
  # for each location...
  for loc in game.locations.values():
    # store all ways to get to a given connection of this node
    dirs_by_conn = defaultdict(list) 
    for (dir,conn) in loc.exits.items():
      dirs_by_conn[conn].append(dir)
    # for each of this location's connections...
    for (conn, dirs) in dirs_by_conn.items():
      # write out an edge , labeled using the directions
      (node_name, other_node_name) = [node_name_by_loc[l]
                                      for l in (loc, conn.point_b)]
      _dot('  %s -> %s [label="%s"];' %
           (node_name, other_node_name, get_label(dirs)))          
  # write footer
  _dot("}")
  # clean up, if necessary
  if file_name:
    f.close()
