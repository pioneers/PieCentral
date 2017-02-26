import csv
import asyncio
import inspect
import os
import time

from runtimeUtil import *

class Robot:
  def __init__(self, toManager, fromManager):
    self.fromManager = fromManager
    self.toManager = toManager
    self._createSensorMapping()
    self._coroutines_running = set()

  def run(self, fn, *args, **kwargs):
    """
    Starts a "coroutine", i.e. a series of actions that proceed 
    independently of the main loop of code.

    The first argument must be a function defined with 'async def'.

    The remaining arguments are then passed to that function before it is
    called.

    Multiple simultaneous coroutines that use the same robot actuators will
    lead to surprising behavior. To help guard against errors, calling
    `run` with a `fn` argument that is currently running is a no-op.
    """

    if not inspect.isfunction(fn):
        raise ValueError("First argument to Robot.run must be a function")
    elif not inspect.iscoroutinefunction(fn):
        raise ValueError("First argument to Robot.run must be defined with `async def`, not `def`")

    if fn in self._coroutines_running:
        return

    self._coroutines_running.add(fn)

    future = fn(*args, **kwargs)

    async def wrapped_future():
        await future
        self._coroutines_running.remove(fn)

    asyncio.ensure_future(wrapped_future())

  def _createSensorMapping(self, filename = 'namedPeripherals.csv'):
    with open(filename, 'r') as f:
      sensorMappings = csv.reader(f)
      self.sensorMappings = {name: int(uid) for name, uid in sensorMappings}

  def createKey(self, key, *args):
    """ Creates a new key, or nested keys if more than 1 key is passed in.
        If any nested key does not exist, it will be created.
    """
    self.toManager.put([SM_COMMANDS.CREATE_KEY, [[key] + list(args)]])
    message = self.fromManager.recv()
    if isinstance(message, StudentAPIKeyError):
      raise message

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
    return self.sensorMappings.get(name)

  def emergencyStop(self):
    self.toManager.put([SM_COMMANDS.EMERGENCY_STOP, []])
