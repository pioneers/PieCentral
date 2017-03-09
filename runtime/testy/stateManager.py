import sys
import time
import runtime_pb2

from runtimeUtil import *

# TODO:
# 0. modify self.state to acually store (name, value) pairs
class StateManager(object):

  """input is a multiprocessing.Queue object to support multiple
  processes requesting state data
  """
  def __init__(self, badThingsQueue, inputQueue, runtimePipe):
    self.initRobotState()
    self.badThingsQueue = badThingsQueue
    self.input = inputQueue
    self.commandMapping = self.makeCommandMap()
    # map process names to pipes
    self.hibikeMapping = self.makeHibikeMap()
    self.hibikeResponseMapping = self.makeHibikeResponseMap()
    self.deviceName_to_subscribeParams = self.makeSubscriptionMap()
    self.processMapping = {PROCESS_NAMES.RUNTIME: runtimePipe}

  def makeSubscriptionMap(self):
    subscriptionMap = {
      "LimitSwitch"  : ["switch0", "switch1", "switch2"],
      "LineFollower"  : ["left", "center", "right"],
      "Potentiometer"  : ["pot0", "pot1", "pot2"],
      "BatteryBuzzer"  : ["total", "safe"],
      "ServoControl"  : ["servo0", "servo1"],
      "YogiBear" : ["duty_cycle", "enc_pos", "enc_vel"],
      "RFID" : ["id", "tag_detect"],
    }
    return subscriptionMap

  def makeCommandMap(self):
    commandMapping = {
      SM_COMMANDS.RESET : self.initRobotState,
      SM_COMMANDS.ADD : self.addPipe,
      SM_COMMANDS.GET_VAL : self.getValue,
      SM_COMMANDS.SET_VAL : self.setValue,
      SM_COMMANDS.STUDENT_MAIN_OK : self.studentCodeTick,
      SM_COMMANDS.CREATE_KEY : self.createKey,
      SM_COMMANDS.SEND_ANSIBLE : self.send_ansible,
      SM_COMMANDS.RECV_ANSIBLE: self.recv_ansible,
      SM_COMMANDS.GET_TIME : self.getTimestamp,
      SM_COMMANDS.EMERGENCY_STOP: self.emergencyStop,
      SM_COMMANDS.EMERGENCY_RESTART: self.emergencyRestart,
      SM_COMMANDS.STUDENT_UPLOAD: self.student_upload,
      SM_COMMANDS.SEND_CONSOLE: self.send_console,
      SM_COMMANDS.SET_ADDR: self.set_addr,
      SM_COMMANDS.SEND_ADDR: self.send_addr,
      SM_COMMANDS.ENTER_IDLE: self.enter_idle,
      SM_COMMANDS.ENTER_TELEOP: self.enter_teleop,
      SM_COMMANDS.ENTER_AUTO: self.enter_auto,
      SM_COMMANDS.END_STUDENT_CODE: self.endStudentCode,
    }
    return commandMapping

  def makeHibikeMap(self):
    hibikeMapping = {
      HIBIKE_COMMANDS.ENUMERATE: self.hibikeEnumerateAll,
      HIBIKE_COMMANDS.SUBSCRIBE: self.hibikeSubscribeDevice,
      HIBIKE_COMMANDS.READ: self.hibikeReadParams,
      HIBIKE_COMMANDS.WRITE: self.hibikeWriteParams,
      HIBIKE_COMMANDS.E_STOP: self.hibikeEmergencyStop
    }
    return hibikeMapping

  def makeHibikeResponseMap(self):
    hibikeResponseMapping = {
      HIBIKE_RESPONSE.DEVICE_SUBBED: self.hibikeResponseDeviceSubbed,
      HIBIKE_RESPONSE.DEVICE_VALUES: self.hibikeResponseDeviceValues
    }
    return {k.value: v for k, v in hibikeResponseMapping.items()}

  def initRobotState(self):
    t = time.time()
    self.state = {
     "studentCodeState": [2, t],
     "limit_switch": [["limit_switch", 0, 123456], t],
     "incrementer" : [2, t],
     "int1" : [112314, t],
     "float1": [987.123, t],
     "bool1" : [True, t],
     "dict1" : [{"inner_dict1_int" : [555, t], "inner_dict_1_string": ["hello", t]}, t],
     "list1" : [[[70, t], ["five", t], [14.3, t]], t],
     "string1" : ["abcde", t],
     "runtime_meta" : [{"studentCode_main_count" : [0, t], "e_stopped" : [False, t]}, t],
     "hibike" : [{"device_subscribed": [0, t], "devices" : [{12345 : [{"sensor0": [1, t]}, t]}, t]}, t],
     "dawn_addr" : [None, t],
     "gamepads" : [{0 : {"axes" : {0:0.5, 1:-0.5, 2:1, 3:-1}, "buttons" : {0:True, 1:False, 2:True, 3:False, 4:True, 5:False}}}, t],
    }

  def addPipe(self, processName, pipe):
    self.processMapping[processName] = pipe
    pipe.send(RUNTIME_CONFIG.PIPE_READY.value)

  def createKey(self, keys, send=True):
    currDict = self.state
    path = []
    for key in keys:
      try:
        if key not in currDict:
          currDict[key] = [{}, 0]
        path.append(currDict[key])
        currDict = currDict[key][0]
      except TypeError:
        error = StudentAPIKeyError(
          "key '{}' is defined, but does not contain a dictionary.".format(key))
        self.processMapping[PROCESS_NAMES.STUDENT_CODE].send(error)
        return
    currTime = time.time()
    for item in path:
      item[1] = currTime
    if send:
      self.processMapping[PROCESS_NAMES.STUDENT_CODE].send(None)

  def getValue(self, keys):
    result = self.state
    try:
      for i, key in enumerate(keys):
        result = result[key][0]
      self.processMapping[PROCESS_NAMES.STUDENT_CODE].send(result)
    except:
      error = StudentAPIKeyError(self.dictErrorMessage(i, keys, result))
      self.processMapping[PROCESS_NAMES.STUDENT_CODE].send(error)

  def setValue(self, value, keys, send=True):
    currDict = self.state
    try:
      path = []
      for i, key in enumerate(keys[:-1]):
        path.append(currDict[key])
        currDict = currDict[key][0]
      if len(keys) > 1:
        i += 1
      else:
        i = 0
      if keys[i] not in currDict:
        raise Exception
      path.append(currDict[keys[i]])
      currDict[keys[i]][0] = value
      currTime = time.time();
      for item in path:
        item[1] = currTime
      if send:
        self.processMapping[PROCESS_NAMES.STUDENT_CODE].send(value)
    except:
      error = StudentAPIKeyError(self.dictErrorMessage(i, keys, currDict))
      if send:
        self.processMapping[PROCESS_NAMES.STUDENT_CODE].send(error)

  def send_ansible(self):
    self.processMapping[PROCESS_NAMES.UDP_SEND_PROCESS].send(self.state)

  def recv_ansible(self, new_data):
    self.state.update(new_data)

  def set_addr(self, new_addr):
    self.state["dawn_addr"] = [new_addr, time.time()]
    self.badThingsQueue.put(BadThing(sys.exc_info(), None, BAD_EVENTS.NEW_IP, False))

  def send_addr(self, process_name):
    self.processMapping[process_name].send(self.state["dawn_addr"][0])

  def student_upload(self):
    self.badThingsQueue.put(BadThing(sys.exc_info(), None, BAD_EVENTS.ENTER_IDLE, False))
    self.processMapping[PROCESS_NAMES.TCP_PROCESS].send([ANSIBLE_COMMANDS.STUDENT_UPLOAD, True])

  def send_console(self, console_log):
    #TODO: Fix Console Logging
    if PROCESS_NAMES.TCP_PROCESS in self.processMapping:
      self.processMapping[PROCESS_NAMES.TCP_PROCESS].send([ANSIBLE_COMMANDS.CONSOLE, console_log])

  def enter_auto(self):
    self.badThingsQueue.put(BadThing(sys.exc_info(), None, BAD_EVENTS.ENTER_AUTO, False))
    self.state["studentCodeState"] = [runtime_pb2.RuntimeData.AUTO, time.time()]

  def enter_teleop(self):
    self.badThingsQueue.put(BadThing(sys.exc_info(), None, BAD_EVENTS.ENTER_TELEOP, False))
    self.state["studentCodeState"] = [runtime_pb2.RuntimeData.TELEOP, time.time()]

  def enter_idle(self):
    self.badThingsQueue.put(BadThing(sys.exc_info(), None, BAD_EVENTS.ENTER_IDLE, False))
    self.state["studentCodeState"] = [runtime_pb2.RuntimeData.STUDENT_STOPPED, time.time()]

  def getTimestamp(self, keys):
    currDict = self.state
    timestamp = 0
    try:
      for i, key in enumerate(keys):
        currDict, timestamp = currDict[key]
      self.processMapping[PROCESS_NAMES.STUDENT_CODE].send(timestamp)
    except:
      error = StudentAPIKeyError(self.dictErrorMessage(i, keys, result))
      self.processMapping[PROCESS_NAMES.STUDENT_CODE].send(error)

  def studentCodeTick(self):
    self.state["runtime_meta"][0]["studentCode_main_count"][0] += 1

  def emergencyStop(self):
    self.state["runtime_meta"][0]["e_stopped"][0] = True
    self.badThingsQueue.put(BadThing(sys.exc_info(), "Emergency Stop Activated", event = BAD_EVENTS.EMERGENCY_STOP, printStackTrace = False))
    self.state["studentCodeState"] = [runtime_pb2.RuntimeData.ESTOP, time.time()]

  def emergencyRestart(self):
    self.state["runtime_meta"][0]["e_stopped"][0] = False

  def endStudentCode(self):
    self.processMapping[PROCESS_NAMES.UDP_RECEIVE_PROCESS].send(runtime_pb2.RuntimeData.STUDENT_STOPPED)

  def hibikeEnumerateAll(self, pipe):
    pipe.send([HIBIKE_COMMANDS.ENUMERATE.value, []])

  def hibikeSubscribeDevice(self, pipe, uid, delay, params):
    pipe.send([HIBIKE_COMMANDS.SUBSCRIBE.value, [uid, delay, params]])

  def hibikeWriteParams(self, pipe, uid, param_values):
    pipe.send([HIBIKE_COMMANDS.WRITE.value, [uid, param_values]])

  def hibikeReadParams(self, pipe, uid, params):
    pipe.send([HIBIKE_COMMANDS.READ.value, [uid, params]])

  def hibikeResponseDeviceSubbed(self, uid, delay, params):
    if delay == 0:
      deviceName = SENSOR_TYPE[uid >> 72]
      if deviceName in self.deviceName_to_subscribeParams:
        self.hibikeSubscribeDevice(self.processMapping[PROCESS_NAMES.HIBIKE], uid, 40, self.deviceName_to_subscribeParams[deviceName])
    self.createKey(["hibike", "devices", uid], send=False)
    for param in params:
      self.createKey(["hibike", "devices", uid, param], send=False)
      self.setValue(None, ["hibike", "devices", uid, param], send=False)
    self.state["hibike"][0]["device_subscribed"][0] += 1

  def hibikeResponseDeviceValues(self, uid, params):
    for key, value in params:
      self.setValue(value, ["hibike", "devices", uid, key], send=False)

  def hibikeEmergencyStop(self, pipe):
    pipe.send([HIBIKE_COMMANDS.E_STOP.value, []])

  def dictErrorMessage(self, erroredIndex, keys, currDict):
    keyChain = ""
    i = 0
    while (i < erroredIndex):
      # Assembles a string representation of the dictionary indexing that occurred
      keyChain += "['" + keys[i] + "']" if (type(keys[i]) is str) else "[" + str(keys[i]) + "]"
      i += 1
    keys = [None] if len(keys) == 0 else keys
    erroredKey = "'" + keys[erroredIndex] + "'" if type(keys[erroredIndex]) is str else str(keys[erroredIndex])
    errorMessage = "KeyError: key " + erroredKey + " not found in state" + keyChain + "\n"

    if type(currDict) is dict:
      # Converts all available keys to strings, and adds commas and spaces at the end of each element
      availableKeys = [("'" + el + "', " if type(el) is str else str(el) + ", ") for el in currDict.keys()]
      if len(availableKeys) > 0:
        # Removes comma and space from last item in availableKeys
        availableKeys[-1] = availableKeys[-1][:-2]
      errorMessage += "Available keys in state" + keyChain + ": " + "".join(availableKeys)
    else:
      errorMessage += "state" + keyChain + " is of type " + type(currDict).__name__

    return errorMessage

  def start(self):
    # TODO: Make sure request is a list/tuple before attempting to access
    # And that there are the correct number of elements
    while True:
      try:
        request = self.input.get(block=True)
        cmdType = request[0]
        args = request[1]
        if(len(request) != 2):
          self.badThingsQueue.put(BadThing(sys.exc_info(), "Wrong input size, need list of size 2", event = BAD_EVENTS.UNKNOWN_PROCESS, printStackTrace = False))
        elif cmdType in self.commandMapping:
          command = self.commandMapping[cmdType]
          command(*args)
        elif cmdType in self.hibikeMapping:
          if (not self.state["runtime_meta"][0]["e_stopped"][0]):
            command = self.hibikeMapping[cmdType]
            command(self.processMapping[PROCESS_NAMES.HIBIKE], *args)
        elif cmdType in self.hibikeResponseMapping:
          command = self.hibikeResponseMapping[cmdType]
          command(*args)
        else:
          self.badThingsQueue.put(BadThing(sys.exc_info(), "Unknown process name: %s" % (request,), event = BAD_EVENTS.UNKNOWN_PROCESS, printStackTrace = False))
      except Exception as e:
        self.badThingsQueue.put(BadThing(sys.exc_info(), "State Manager Loop crash with: " + str(e), event = BAD_EVENTS.STATE_MANAGER_CRASH, printStackTrace = True))
