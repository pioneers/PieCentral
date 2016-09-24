from runtimeUtil import *

class Robot:
  def __init__(self, toManager, fromManager):
    self.fromManager = fromManager
    self.toManager = toManager
    # Wait for ack from SM before continuing
    self.fromManager.recv()

  def getState(self):
    self.toManager.put([SM_COMMANDS.GET_STATE])
    return self.fromManager.recv()

  def getValue(self, key):
    """Returns the value associated with key
    """
    # TODO: Actually use key
    if key not in list( (self.getState().keys()) ):
        raise StudentValueError("'{}' is not a valid key.".format(name))
    self.toManager.put([SM_COMMANDS.GET_VAL, key])
    return self.fromManager.recv()

  def setValue(self, key, value):
    """Sets the value associated with key
    """
    if key not in list( (self.getState().keys()) ):
        raise StudentValueError("'{}' is not a valid key.".format(name))
    self.toManager.put([SM_COMMANDS.SET_VAL, key, value])
    return self.fromManager.recv()

class StudentError(Exception):
  pass

class StudentValueError(StudentError):
    pass
