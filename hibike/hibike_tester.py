"""
Create a separate Hibike process, for testing.
"""
from multiprocessing import Process, Pipe, Queue
# pylint: disable=import-error
import hibike_process

class Hibike:
    """
    Interface to a separate Hibike process.
    """
    def __init__(self):
        self.bad_things_queue = Queue()
        self.state_queue = Queue()
        self.pipe_to_child, self.pipe_from_child = Pipe()
        self.hibike_process = Process(target=hibike_process.hibike_process,
                                      args=(self.bad_things_queue,
                                            self.state_queue, self.pipe_from_child))
        self.hibike_process.daemon = True
        self.hibike_process.start()

    def enumerate(self):
        """
        Enumerate all devices.
        """
        self.pipe_to_child.send(["enumerate_all", []])

    def subscribe(self, uid, delay, params):
        """
        Subscribe to device UID, with DELAY delay, and parameters PARAMS.
        """
        self.pipe_to_child.send(["subscribe_device", [uid, delay, params]])

    def write(self, uid, params_and_values):
        """
        Write PARAMS_AND_VALUES to the device at UID.
        """
        self.pipe_to_child.send(["write_params", [uid, params_and_values]])

    def read(self, uid, params):
        """
        Read PARAMS from the device at UID.
        """
        self.pipe_to_child.send(["read_params", [uid, params]])

    def disable(self):
        """
        Disable all attached devices.
        """
        self.pipe_to_child.send(["disable_all", []])
if __name__ == '__main__':
    HIBIKE = Hibike()
    HIBIKE.enumerate()
    while True:
        print(HIBIKE.state_queue.get())
