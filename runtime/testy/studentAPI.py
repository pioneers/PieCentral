import csv

from runtimeUtil import *

class Robot:
  def __init__(self, toManager, fromManager):
    self.fromManager = fromManager
    self.toManager = toManager
    self._createSensorMapping()

  def _createSensorMapping(self, filename = 'namedPeripherals.csv'):
    self.sensorMappings = {}
    with open(filename, 'r') as f:
        sensorMappings = csv.reader(f)
        for name, uid in sensorMappings:
            self.sensorMappings[name] = int(uid)

  def createKey(self, key, *args):
    """ Creates a new key, or nested keys if more than 1 key is passed in.
        If any nested key does not exist, it will be created.
    """
    self.toManager.put([SM_COMMANDS.CREATE_KEY, [[key] + list(args)]])
    message = self.fromManager.recv()
    if isinstance(message, StudentAPIKeyError):
        raise message
    return

  def getValue(self, key, *args):
    """Returns the value associated with key
    """
    self.toManager.put([SM_COMMANDS.GET_VAL, [[key] + list(args)]])
    message = self.fromManager.recv()
    if isinstance(message, StudentAPIKeyError):
        raise message
    return message

  def setValue(self, value, key, *args):
    """Sets the value associated with key
    """
    #statemanager passes exception, then check to see if returned value is exception or not
    self.toManager.put([SM_COMMANDS.SET_VAL, [value, [key] + list(args)]])
    message = self.fromManager.recv()
    if isinstance(message, StudentAPIKeyError):
        raise message
    return message

  def getTimestamp(self, key, *args):
    """Returns the value associated with key
    """
    self.toManager.put([SM_COMMANDS.GET_TIME, [[key] + list(args)]])
    message = self.fromManager.recv()
    if isinstance(message, StudentAPIKeyError):
        raise message
    return message

  # TODO: Only for testing. Remove in final version
  def _hibikeSubscribeDevice(self, uid, delay, params):
    """Uses direct uid to access hibike."""
    self.toManager.put([HIBIKE_COMMANDS.SUBSCRIBE, [uid, delay, params]])

  def _hibikeGetUID(self, name):
    if name in self.sensorMappings:
        return self.sensorMappings[name]
    else:
        return None

  def emergencyStop(self):
    self.toManager.put([SM_COMMANDS.EMERGENCY_STOP, []])
