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

  def getValue(self, key):
    self.processMapping[PROCESS_NAMES.STUDENT_CODE].send(self.state[key])

  def setValue(self, key, value):
    self.state[key] = value
    self.processMapping[PROCESS_NAMES.STUDENT_CODE].send(self.state[key])

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
