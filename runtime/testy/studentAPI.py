from runtimeUtil import *

class Robot:
  def __init__(self, toManager, fromManager):
    self.fromManager = fromManager
    self.toManager = toManager
    # Wait for ack from SM before continuing
    self.fromManager.recv()

  def getValue(self, name):
    """Returns the value associated with name
    """
    # TODO: Actually use name
    self.toManager.put([SM_COMMANDS.HELLO])
    return self.fromManager.recv()

  def setValue(self, name, value):
    """Sets the value associated with name
    """
    # TODO: Implement
    raise NotImplementedError
