import sys

from runtimeUtil import *


class HibikeSimulator:
    def __init__(self, badThingsQueue, toManager, fromManager):
        self.badThingsQueue = badThingsQueue
        self.fromManager = fromManager
        self.toManager = toManager
        self.commandMapping = self.makeCommandMap()  # dict with command names

    def makeCommandMap(self):
        commandMapping = {
            HIBIKE_COMMANDS.SUBSCRIBE: self.subscribe_device,
        }
        return commandMapping

    def subscribe_device(self, uid, delay, params):
        self._device_subscribed()

    def _device_subscribed(self, uid=123, delay=321, param1="param1", param2="param2"):
        self.toManager.put([HIBIKE_RESPONSE.DEVICE_SUBBED,
                            [uid, delay, [param1, param2]]])

    def emergency_stop(self):
        # should write 0 to all motors and set stopped boolean to true
        print("EMERGENCY STOPPED COMMAND")

    def start(self):
        # TODO: Make sure request is a list/tuple before attempting to access
        # And that there are the correct number of elements
        while True:
            request = self.fromManager.recv()
            cmdType = request[0]
            args = request[1]
            if(len(request) != 2):
                self.badThingsQueue.put(BadThing(sys.exc_info(
                ), "Wrong input size, need list of size 2", event=BAD_EVENTS.UNKNOWN_PROCESS, printStackTrace=False))
            elif(cmdType not in self.commandMapping):
                self.badThingsQueue.put(BadThing(sys.exc_info(), "Unknown process name: %s" % (
                    request,), event=BAD_EVENTS.UNKNOWN_PROCESS, printStackTrace=False))
            else:
                command = self.commandMapping[cmdType]
                command(*args)
