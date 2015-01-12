#
# adventure game developer tools
#

from advent import DevToolsBase, register_devtools, DEBUG
import argparse

class DevTools(DevToolsBase):
  def __init__(self):
    DevToolsBase.__init__(self)
    self.args = {}
    self.debug_level = 0
    self.argparser = argparse.ArgumentParser(description='Process command line arguments.')
    self.argparser.add_argument('-e', '--execute');  # script to execute
    self.argparser.add_argument('-d', '--debug_level');  # debugging output level

  def get_script(self):
    return self.args.execute
      
  def debug_output(self, text, level):
    if self.debug_level >= level:
      self.game.output(text, DEBUG)
    return

  def start(self):
    # parse the args now that all modules have had a chance to add arg handlers
    self.args = self.argparser.parse_args()
    if self.args.debug_level:
      self.debug_level = int(self.args.debug_level)
    self.debug_output("advent_devtools enabled:\n" +
                      "\tdebug output level: %d\n" % self.debug_level +
                      "\texecuting script: %s" % self.args.execute,
                      0)
    
register_devtools(DevTools())
