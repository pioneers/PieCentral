from runtimeUtil import *
class HibikeSimulator:
	def __init__(self, badThingsQueue, inputQueue, stateManagerPipe):
		self.badThingsQueue = badThingsQueue
		self.input = inputQueue
		self.commandMapping = self.makeCommandMap #dict with command names

	def makeCommandMap():
		commandMapping = {
      SM_COMMANDS.GET_VAL : self.getValue,
      SM_COMMANDS.SET_VAL : self.setValue
    }
    return commandMapping

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
        command(*args)
