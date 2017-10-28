"""
Create a separate Hibike process, for testing.
"""
from multiprocessing import Process, Pipe, Queue
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
                  except KeyError:
                     continue
                 if uid not in self.device_values_cache:
                    self.device_values_cache.update({uid: {parameter: (value, time.time())}})
                 else:
                    self.device_values_cache[uid].update({parameter: (value, time.time())})

    def get_last_cached(self, uid, param):
      try:
         return self.device_values_cache[uid][param]
      except KeyError:
         print("Keyerror detected, returning zero as last cached")
         return 0

    def get_uids_and_types(self):
      list = []
      for uid in self.uids:
          list.append((uid, hm.uid_to_device_name(uid)))
      return list

    def enumerate(self):
        self.pipe_to_child.send(["enumerate_all", []])

    def subscribe(self, uid, delay, params):
        self.pipe_to_child.send(["subscribe_device", [uid, delay, params]])

    def write(self, uid, params_and_values):
        self.pipe_to_child.send(["write_params", [uid, params_and_values]])

    def read(self, uid, params):
        self.pipe_to_child.send(["read_params", [uid, params]])

    def disable(self):
        self.pipe_to_child.send(["disable_all", []])

def run_test():
   comms = HibikeCommunicator()
   time.sleep(3)
   device_info = comms.get_uids_and_types()
   a set of commands in a cycle
   for uid_type_tuple in device_info:
      uid = uid_type_tuple[0]
      type = uid_type_tuple[1]
      print("Device info packet: ", uid_type_tuple)
      print("Type: ", type)
      if type == "LimitSwitch":
         while True:
            comms.subscribe(uid, 100, ["switch0", "switch1", "switch2", "switch3"])
            time.sleep(0.05)
            print("Uid: ", uid,"\n", "Last cached, swich1 and switch2: ", comms.get_last_cached(uid, "switch0"), "\n", comms.get_last_cached(uid, "switch1"), "\n")
            time.sleep(0.5)

      elif type == "LineFollower":
         while True:
            comms.subscribe(uid, 100, ["left", "center", "right"])
            time.sleep(0.05)
            print("Uid: ", uid,"\n", "Last cached, all params: ", comms.get_last_cached(uid, "left"), "\n", comms.get_last_cached(uid, "right"), "\n")
            time.sleep(0.5)

      elif type == "Potentiometer":
         while True:
            comms.subscribe(uid, 100, ["pot0" , "pot1", "pot2", "pot3"])
            time.sleep(0.05)
            print("Uid: ", uid,"\n", "Last cached, pot0 and pot2: ", comms.get_last_cached(uid, "pot0"), "\n", comms.get_last_cached(uid, "pot2"), "\n")
            time.sleep(0.5)

      elif type == "Encoder":
         while True:
            comms.read(uid, ["rotation"])
            time.sleep(0.05)
            comms.read(uid, ["rotation"])
            time.sleep(0.05)
            comms.read(uid, ["rotation"])
            time.sleep(0.5)

      elif type == "BatteryBuzzer":
         while True:
            comms.subscribe(uid, 100, ["cell1", "cell2", "cell3", "calibrate"])
            time.sleep(0.05)
            comms.write(uid, ("calibrate", True))
            time.sleep(0.05)
            comms.write(uid, ("calibrate", False))
            time.sleep(0.05)
            print("Uid: ", uid,"\n", "Last cached, calibrate and cell2: ", comms.get_last_cached(uid, "calibrate"), "\n", comms.get_last_cached(uid, "cell2"), "\n")
            time.sleep(0.5)

      elif type == "TeamFlag":
         while True:
            comms.subscribe(uid, 100, ["led1", "led2", "led3", "led4", "blue", "yellow"])
            time.sleep(0.05)
            comms.write(uid, [("led1", True), ("led2", True), ("led3", False), ("led4", False), ("blue", True), ("yellow", False)])
            time.sleep(0.05)
            comms.write(uid, [("led1", False), ("led2", False), ("led3", True), ("led4", True), ("blue", False), ("yellow", True)])
            time.sleep(0.05)
            print("Uid: ", uid,"\n", "Last cached, blue and yellow: ", comms.get_last_cached(uid, "blue"), "\n", comms.get_last_cached(uid, "yellow"), "\n")
            time.sleep(0.5)

      elif type == "YogiBear":
         while True:
            comms.subscribe(uid, 100, ["duty", "forward"])
            time.sleep(0.05)
            comms.write(uid, [("duty", 100),  ("forward", False)])
            time.sleep(0.05)
            comms.write(uid, [("duty", 50),  ("forward", True)])
            time.sleep(0.05)
            print("Uid: ", uid,"\n", "Last cached, all params: ", comms.get_last_cached(uid, "duty"), "\n", comms.get_last_cached(uid, "forward"), "\n")
            time.sleep(0.5)

      elif type == "ServoControl":
         while True:
            comms.subscribe(uid, 100, ["servo0", "enable0", "servo1", "enable1", "servo2", "enable2", "servo3", "enable3"])
            time.sleep(0.05)
            comms.write(uid, [("servo0", 3), ("enable0", False), ("servo1", 3), ("enable1", False), ("servo2", 3), ("enable2", True), ("servo3", 3), ("enable3", False)])
            time.sleep(0.05)
            comms.write(uid, [("servo0", 1), ("enable0", True), ("servo1", 26), ("enable1", True), ("servo2", 30), ("enable2", False), ("servo3", 17), ("enable3", True)])
            time.sleep(0.05)
            print("Uid: ", uid,"\n", "Last cached, servo1 and enable1: ", comms.get_last_cached(uid, "servo1"), "\n", comms.get_last_cached(uid, "enable1"), "\n")
            time.sleep(0.5)

      elif type == "ExampleDevice":
         while True:
            comms.subscribe(uid, 100, ["kumiko", "hazuki", "sapphire", "reina", "asuka", "haruka", "kaori", "natsuki", "yuko", "mizore", "nozomi", "shuichi", "takuya", "riko", "aoi", "noboru"])
            time.sleep(0.05)
            comms.write(uid, [("kumiko", True), ("hazuki", 19), ("sapphire", 12), ("reina", 210), ("asuka", 105), ("haruka", 1005), ("kaori", 551), ("natsuki", 18002), ("yuko", 9001), ("mizore", 6.45), ("nozomi", 33.2875), ("takuya", 331), ("aoi", 7598)])
            time.sleep(0.05)
            comms.write(uid, [("kumiko", False), ("hazuki", 0), ("sapphire", 0), ("reina", 0), ("asuka", 0), ("haruka", 0), ("kaori", 0), ("natsuki", 0), ("yuko", 0), ("mizore", 0.0), ("nozomi", 0.0), ("takuya", 0), ("aoi", 0)])
            time.sleep(0.05)
            print("Uid: ", uid,"\n","Last cached, kumiko and hazuki: ", comms.get_last_cached(uid, "kumiko"), "\n", comms.get_last_cached(uid, "hazuki"), "\n")
            time.sleep(0.5)
      elif type == "RFID":
         while True:
            comms.subscribe(uid, 100, ["id", "detect_tag"])
            time.sleep(0.05)
            comms.read(uid, ["id"])
            time.sleep(0.05)
            print("Uid: ", uid, "\n", "Last cached, all params: ", comms.get_last_cached(uid, "id"), "\n", comms.get_last_cached(uid, "detect_tag"))
            time.sleep(0.5)
      else:
         raise TypeError("ERROR: unknown device type detected")
