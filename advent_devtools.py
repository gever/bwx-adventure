#
# adventure game developer tools
#

from advent import DevToolsBase, register_devtools
import argparse

class DevTools(DevToolsBase):
  def __init__(self):
    print "advent_devtools enabled"
    DevToolsBase.__init__(self)
    self.args = {}
    self.argparser = argparse.ArgumentParser(description='Process command line arguments.')
    self.argparser.add_argument('-e', '--execute');  # script to execute

  def get_script(self):
    return self.args.execute
      
  def start(self):
    # parse the args now that all modules have had a chance to add arg handlers
    self.args = self.argparser.parse_args()
    
register_devtools(DevTools())
