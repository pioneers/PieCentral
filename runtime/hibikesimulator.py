import sys

from runtimeUtil import *


class HibikeSimulator:
    def __init__(self, bad_things_queue, to_manager, from_manager):
        self.bad_things_queue = bad_things_queue
        self.from_manager = from_manager
        self.to_manager = to_manager
        self.command_mapping = self.make_command_map()  # dict with command names

    def make_command_map(self):
        command_mapping = {
            HIBIKE_COMMANDS.SUBSCRIBE: self.subscribe_device,
        }
        return command_mapping

    def subscribe_device(self, _uid, _delay, _params):
        self._device_subscribed()

    def _device_subscribed(self, uid=123, delay=321, param1="param1", param2="param2"):
        self.to_manager.put([HIBIKE_RESPONSE.DEVICE_SUBBED,
                             [uid, delay, [param1, param2]]])

    def emergency_stop(self):
        # should write 0 to all motors and set stopped boolean to true
        print("EMERGENCY STOPPED COMMAND")

    def start(self):
        # TODO: Make sure request is a list/tuple before attempting to access
        # And that there are the correct number of elements
        while True:
            request = self.from_manager.recv()
            cmd_type = request[0]
            args = request[1]
            if len(request) != 2:
                self.bad_things_queue.put(BadThing(sys.exc_info()
                                                   , "Wrong input size, need list of size 2"
                                                   , event=BAD_EVENTS.UNKNOWN_PROCESS
                                                   , printStackTrace=False))
            elif cmd_type not in self.command_mapping:
                self.bad_things_queue.put(BadThing(sys.exc_info(), "Unknown process name: %s" % (
                    request,), event=BAD_EVENTS.UNKNOWN_PROCESS, printStackTrace=False))
            else:
                command = self.command_mapping[cmd_type]
                command(*args)
