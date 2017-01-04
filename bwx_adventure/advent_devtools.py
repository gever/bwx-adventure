#
# adventure game developer tools
#

from advent import DevToolsBase, register_devtools, DEBUG
import argparse
import random

class DevTools(DevToolsBase):
  def __init__(self):
    DevToolsBase.__init__(self)
    self.args = {}
    self.debug_level = 0
    self.argparser = argparse.ArgumentParser(description='Process command line arguments.')
    self.argparser.add_argument('-c', '--check', action='store_true');  # check responses
    self.argparser.add_argument('-d', '--debug_level')  # debugging output level
    self.argparser.add_argument('-e', '--execute')  # script to execute
    self.argparser.add_argument('-f', '--fail_on_mismatch', action='store_true')
    self.argparser.add_argument('-s', '--start_recording') # script to record
    self.argparser.add_argument('-r', '--random', action='store_true') # force random seed
        
  def debug_output(self, text, level):
    if self.debug_level >= level:
      self.game.output(text, DEBUG)
    return

  def start(self):
    # parse the args now that all modules have had a chance to add arg handlers
    self.args = self.argparser.parse_args()

    if self.args.debug_level:
      self.debug_level = int(self.args.debug_level)

    seed=12345 # fixed seed is useful to get reproducible test runs
    if self.args.random:
      seed = None
    random.seed(seed)

    if self.args.execute:
      self.game.set_var('script_name', self.args.execute)
      
    if self.args.check:
      self.game.set_flag('check')

    if self.args.fail_on_mismatch:
      self.game.set_flag('fail_on_mismatch')

    if self.args.start_recording:
      self.game.set_var('start_recording', self.args.start_recording)
          
    self.debug_output("advent_devtools enabled:\n" +
                      "\tdebug output level: %d\n" % self.debug_level +
                      "\texecuting script: %s" % self.args.execute,
                      0)
    
register_devtools(DevTools())
