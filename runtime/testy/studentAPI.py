import csv
import asyncio
import inspect
import os
import time

from runtimeUtil import *

class Actions:
  async def sleep(self, seconds):
    await asyncio.sleep(seconds)

class StudentAPI:
  def __init__(self, toManager, fromManager):
    StudentAPI.fromManager = fromManager
    StudentAPI.toManager = toManager

  def _getSMValue(self, key, *args):
    """Returns the value associated with key
    """
    self.toManager.put([SM_COMMANDS.GET_VAL, [[key] + list(args)]])
    message = self.fromManager.recv()
    if isinstance(message, Exception):
      raise message
    return message

  def _setSMValue(self, value, key, *args):
    """Sets the value associated with key
    """
    #statemanager passes exception, then check to see if returned value is exception or not
    self.toManager.put([SM_COMMANDS.SET_VAL, [value, [key] + list(args)]])
    message = self.fromManager.recv()
    if isinstance(message, Exception):
      raise message
    return message

class Gamepad(StudentAPI):
  buttons = {
    "button_a" : 0,
    "button_b" : 1,
    "button_x" : 2,
    "button_y" : 3,
    "l_bumper" : 4,
    "r_bumper" : 5,
    "l_trigger" : 6,
    "r_trigger" : 7,
    "button_back" : 8,
    "button_start" : 9,
    "l_stick" : 10,
    "r_stick" : 11,
    "dpad_up" : 12,
    "dpad_down" : 13,
    "dpad_left" : 14,
    "dpad_right" : 15,
    "button_xbox" : 16
  }
  joysticks = {
    "joystick_left_x" : 0,
    "joystick_left_y" : 1,
    "joystick_right_x" : 2,
    "joystick_right_y" : 3
  }

  def __init__(self):
    super().__init__(self.toManager, self.fromManager)

  def get_value(self, name, gamepad_number=0):
    gamepad_dict = self._getSMValue('gamepads')[gamepad_number]
    if name in self.joysticks.keys():
      return gamepad_dict["axes"][self.joysticks[name]]
    elif name in self.buttons.keys():
      return gamepad_dict["buttons"][self.buttons[name]]
    else:
      raise StudentAPIKeyError()

class Robot(StudentAPI):
  def __init__(self, toManager, fromManager):
    super().__init__(toManager, fromManager)
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
    if self.is_running(fn):
      return

    self._coroutines_running.add(fn)

    future = fn(*args, **kwargs)

    async def wrapped_future():
      await future
      self._coroutines_running.remove(fn)

    asyncio.ensure_future(wrapped_future())

  def is_running(self, fn):
    if not inspect.isfunction(fn):
      raise StudentAPIValueError("First argument to Robot.run must be a function")
    elif not inspect.iscoroutinefunction(fn):
      raise StudentAPIValueError("First argument to Robot.run must be defined with `async def`, not `def`")

    return fn in self._coroutines_running

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
    try:
      return self.sensorMappings.get(name)
    except:
      raise StudentAPIKeyError()

  def emergencyStop(self):
    self.toManager.put([SM_COMMANDS.EMERGENCY_STOP, []])

  def _print(self, *args):
    print(*args)
    console_string = " ".join([str(arg) for arg in args])
    self.toManager.put([SM_COMMANDS.SEND_CONSOLE, [console_string]]) 
