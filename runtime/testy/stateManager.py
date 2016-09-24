# import multiprocessing
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
    # map process names to pipes
    self.processMapping = {PROCESS_NAMES.RUNTIME: runtimePipe}

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
      cmd_type = request[0]
      if cmd_type == SM_COMMANDS.RESET:
        self.initRobotState()
      elif cmd_type == SM_COMMANDS.ADD:
        self.addPipe(request[1], request[2])
      elif cmd_type == SM_COMMANDS.GET_VAL:
        self.getValue(request[1])
      elif cmd_type == SM_COMMANDS.SET_VAL:
        self.setValue(request[1], request[2])
      elif cmd_type == SM_COMMANDS.HELLO:
        print("HELLO")
      # TODO: Add better error description
      else:
        self.badThingsQueue.put(BadThing(sys.exc_info(), "Unknown process name: %s" % (request,), event = BAD_EVENTS.UNKNOWN_PROCESS, printStackTrace = False))
