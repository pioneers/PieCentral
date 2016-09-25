import sys

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
    self.processMapping = {PROCESS_NAMES.RUNTIME: runtimePipe}

  def makeCommandMap(self):
    commandMapping = {
      SM_COMMANDS.RESET : self.initRobotState,
      SM_COMMANDS.ADD : self.addPipe,
      SM_COMMANDS.GET_VAL : self.getValue,
      SM_COMMANDS.SET_VAL : self.setValue,
      SM_COMMANDS.HELLO : "print"
    }
    return commandMapping

  def initRobotState(self):
    self.state = {
     "incrementer" : 5,
     "int1" : 112314,
     "float1": 987.123,
     "bool1" : True,
     "dict1" : {"inner_dict1_int" : 555, "inner_dict_1_string": "hello"},
     "list1" : [70, "five", 14.3],
     "string1" : "abcde"
    }

  def addPipe(self, processName, pipe):
    self.processMapping[processName] = pipe
    pipe.send(RUNTIME_CONFIG.PIPE_READY.value)

  def getValue(self, keys):
    result = self.state
    try:
      for key in enumerate(keys):
        i = key[0]
        result = result[key[1]]
      self.processMapping[PROCESS_NAMES.STUDENT_CODE].send(result)
    except:
      self.badThingsQueue.put(BadThing(sys.exc_info(), self.dictErrorMessage(i, keys, result), event = BAD_EVENTS.STATE_MANAGER_KEY_ERROR, printStackTrace = False))

  def setValue(self, value, keys):
    currDict = self.state
    i = 0
    try:
      for key in enumerate(keys[:-1]):
        i = key[0]
        currDict = currDict[key[1]]
      if len(keys) > 1:
        i += 1
      currDict[keys[i]] = value
      self.processMapping[PROCESS_NAMES.STUDENT_CODE].send(value)
    except:
      self.badThingsQueue.put(BadThing(sys.exc_info(), self.dictErrorMessage(i, keys, currDict), event = BAD_EVENTS.STATE_MANAGER_KEY_ERROR, printStackTrace = False))

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
      request = self.input.get(block=True)
      cmdType = request[0]
      args = request[1]

      if(len(request) != 2):
        self.badThingsQueue.put(BadThing(sys.exc_info(), "Wrong input size, need list of size 2", event = BAD_EVENTS.UNKNOWN_PROCESS, printStackTrace = False))
      elif(cmdType not in self.commandMapping):
        self.badThingsQueue.put(BadThing(sys.exc_info(), "Unknown process name: %s" % (request,), event = BAD_EVENTS.UNKNOWN_PROCESS, printStackTrace = False))
      else:
        command = self.commandMapping[cmdType]
        if command == "print":
          print("HELLO")
        else:
          command(*args)
