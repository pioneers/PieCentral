"""
Create a separate Hibike process, for testing.
"""
from multiprocessing import Process, Pipe, Queue
# pylint: disable=import-error
import hibike_process

class Hibike:
    """ Interface to a separate Hibike process. """
    def __init__(self):
        self.bad_things_queue = Queue()
        self.state_queue = Queue()
        self.pipe_to_child, self.pipe_from_child = Pipe()
        self.hibike_process = Process(target=hibike_process.hibike_process,
                                      args=(self.bad_things_queue,
                                            self.state_queue, self.pipe_from_child))
        self.hibike_process.daemon = True
        self.hibike_process.start()
        self.uids = set()
        out_thread = threading.Thread(target=self.process_output)
        out_thread.start()
        self.device_values_cache = {}

    def process_output(self):
       """ Processes the output uploaded to the state queue by te devices
       If it's a subscription response from a device whose uid is not in
       self.uids, the uid will be added to self.uids
       If it's a device disconnection from a device whose uid in self.uids,
       the uid will be removed from self.uids
       If it's a device value, cache it in the dictionary """
       while True:
           output = self.state_queue.get()
           command = output[0]
           if command == "device_subscribed":
               uid = output[1][0]
               if uid not in self.uids:
                   self.uids.add(uid)
          if command == "device_disconnected":
              uid = output[1]
              if uid in self.uids:
                  self.uids.remove(uid)

          if command == "device_values":
              uid = 0
              for key in output[1][0].keys():
                  uid = key
              try:
                  params_values = output[1][0][uid]
              except KeyError:
                  params_values = [{}]

              for param_val_tuple in params_values:
                  try:
                      parameter = param_val_tuple[0]
                      value = param_val_tuple[1]
                  except KeyError: # Treat a tuple with a missing value as if it didn't exist, except to print an error message
                     continue
                 if uid not in self.device_values_cache:
                    self.device_values_cache.update({uid: {parameter: (value, time.time())}})
                 else:
                    self.device_values_cache[uid].update({parameter: (value, time.time())})

    def get_last_cached(self, uid, param):
      """
         Returns a tuple of the value and the timestamp of the last device_values
         package recieved from a uid and a parameter.

         Precondition: a device_data with a UID, params, and values must have been
         recieved from the param before calling this function

      """
      try:
         return self.device_values_cache[uid][param]
      except KeyError:
         print("Keyerror detected, returning zero as last cached")
         return 0

    def get_uids_and_types(self):
      """
      Returns a list of tuples of all of the uids of all devices that the
      HibikeCommunicator talks to Tuple structure: (uid, device type name)
      """
      list = []
      for uid in self.uids:
          list.append((uid, hm.uid_to_device_name(uid)))
      return list

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
