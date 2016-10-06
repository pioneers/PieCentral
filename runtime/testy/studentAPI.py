from runtimeUtil import *

class Robot:
  def __init__(self, toManager, fromManager):
    self.fromManager = fromManager
    self.toManager = toManager

  def getValue(self, key, *args):
    """Returns the value associated with key
    """
    self.toManager.put([SM_COMMANDS.GET_VAL, [[key] + list(args)]])
    return self.fromManager.recv()

  def setValue(self, value, key, *args):
    """Sets the value associated with key
    """
    self.toManager.put([SM_COMMANDS.SET_VAL, [value, [key] + list(args)]])
    return self.fromManager.recv()
