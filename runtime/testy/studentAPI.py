from runtimeUtil import *

class Robot:
  def __init__(self, toManager, fromManager):
    self.fromManager = fromManager
    self.toManager = toManager
    # Wait for ack from SM before continuing
    # self.fromManager.recv()

  def getValue(self, key):
    """Returns the value associated with key
    """
    # TODO: Actually use key
    self.toManager.put([SM_COMMANDS.GET_VAL, key])
    if name not in SM_COMMANDS.__members__:
        raise StudentValueError("'{}' is not a valid command.".format(name))
    return self.fromManager.recv()

  def setValue(self, key, value):
    """Sets the value associated with key
    """
    if name not in SM_COMMANDS.__members__:
        raise StudentValueError("'{}' is not a valid command.".format(name))
    self.toManager.put([SM_COMMANDS.SET_VAL, key, value])

class StudentError(Exception):
  pass

class StudentValueError(StudentError):
    pass
