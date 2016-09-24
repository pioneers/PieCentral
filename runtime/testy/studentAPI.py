from runtimeUtil import *

class Robot:
  def __init__(self, toManager, fromManager):
    self.fromManager = fromManager
    self.toManager = toManager
    # Wait for ack from SM before continuing
    self.fromManager.recv()

  def getValue(self, key):
    """Returns the value associated with key
    """
    # TODO: Actually use key
    self.toManager.put([SM_COMMANDS.GET_VAL, key])
    return self.fromManager.recv()

  def setValue(self, key, value):
    """Sets the value associated with key
    """
    # TODO: Implement
    self.toManager.put([SM_COMMANDS.SET_VAL, key, value])
