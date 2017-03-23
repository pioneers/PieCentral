"""
   This library contains a set of functions that allow the user to manually send and recieve  messages to and from a device by calling functions
"""

import hibike_message as hm
import hibike_process as hp
import multiprocessing
import threading
import time

class HibikeCommunicator:
  
   def __init__(self):
      """
          Set up the pipes for communication between the device and the Beegle Bum Black, creates a thread to recieve communications from the device, starts up the process that runs the communication, and sets up a dictionary that caches all device values sent to it.
      """
      
      # This block creates the pipes
      self.pipeToChild, pipeFromChild = multiprocessing.Pipe()
      
      # This block creates the process
      badThingsQueue = multiprocessing.Queue()
      self.stateQueue = multiprocessing.Queue()
      newProcess = multiprocessing.Process(target=hp.hibike_process, name="hibike_sim", args=[badThingsQueue,self.stateQueue, pipeFromChild])
      newProcess.daemon = True
      newProcess.start()
      self.pipeToChild.send(["enumerate_all", []])
      
      # Creates the list of uids
      self.uids = set()
      
      # This block creates the thread
      outThread =  threading.Thread(target = self.process_output)
      outThread.start()
   
      # Create the device values dictionary cache
      self.device_values_cache = {}

   def process_output(self):
      """
         Prints out messages from the devices that are uploaded by newProcess to stateQueue
         If it's a subscription response from a device whose uid is not in self.uids, the uid will be added to self.uids
         If it's a device disconnection from a device whose uid in self.uids, the uid will be removed from self.uids
      """
      while True:
         output = self.stateQueue.get()
         print(output)

         #Now, get or remove the uid if it is appropriate to do so
         command = output[0]
         if command == "device_subscribed":
            uid = output[1][0]
            if uid not in self.uids:
               self.uids.add(uid)
         if command == "device_disconnected":
            uid = output[1]
            if uid in self.uids:
               self.uids.remove(uid)

   
         #If it is a device value, cache it in the dictionary.
         if command == "device_values":
             uid = output[1][0]
             params_values = output[1][1]
             for param_val_tuple in params_values:
                if uid not in self.device_values_cache:
                   self.device_values_cache.update({uid: {param_val_tuple[0]: (param_val_tuple[1], time.time())}})  
                else:
                   self.device_values_cache[uid].update({param_val_tuple[0]: (param_val_tuple[1], time.time())})
   
   def get_last_cached(self, uid, param):
      """
         Returns a tuple of the value and the timestamp of the last device_values package recieved from a uid and a parameter
         Precondition: a device_data must have been recieved from the param before calling this function
      """
      return self.device_values_cache[uid][param]

   
   def get_uids_and_types(self):
      """
         Returns a list of tuples of all of the uids of all devices that the HibikeCommunicator talks to
         Tuple structure: (uid, device type name)
      """
      list = []
      for uid in self.uids:
         list.append((uid, hm.uid_to_device_name(uid)))
      return list

   def write(self, uid, params_and_values):
       """
          Sends a Device Write to a device
          uid - the device's uid
          params_and_values - an iterable of param (name, value) tuples
       """
       self.pipeToChild.send(["write_params", [uid, params_and_values]])
   
   def read(self, uid, params): 
        """
           Sends a Device Read to a device
        
           uid - the device's uid
           params - an iterable of the names of the params to be read
        """
        self.pipeToChild.send(["read_params", [uid, params]])
        
   def subscribe(self, uid, delay, params):
        """
           Subscribes to the device
           
           uid - the device's uid
           delay - the delay between device datas to be sent
           params - an iterable of the names of the params to be subscribed to
        """
        self.pipeToChild.send(["subscribe_device", [uid, delay, params]])

##############
#  TESTING   #
##############
def device_comms(comms, uid_type_tuple):
   """
        Given a Hibike_Communicator and the subscribed-to device's UID and type, gives it several orders
        
        comms: the Hibike_Communicator
        uid_type_tuple: a tuple that looks like this: (UID, device type)
        Precondition: uid_type_tuple must be an element of comms.get_uids_and_types()
   """
   uid = uid_type_tuple[0]
   type = uid_type_tuple[1]
   
   
   if type == "LimitSwitch":
      comms.subscribe(uid, 100, ["switch0", "switch1", "switch2", "switch3"])
      while True:
         time.sleep(0.5)
         print("Uid: ", uid,"\n", "Last cached: ", comms.get_last_cached(uid, "switch0"), "\n", comms.get_last_cached(uid, "switch1"), "\n")

   elif type == "LineFollower":
      comms.subscribe(uid, 100, ["left", "center", "right"])
      while True:
         time.sleep(0.5)
         print("Uid: ", uid,"\n", "Last cached: ", comms.get_last_cached(uid, "left"), "\n", comms.get_last_cached(uid, "right"), "\n")

   elif type == "Potentiometer":
      comms.subscribe(uid, 100, ["pot0" , "pot1", "pot2", "pot3"])
      while True:
         time.sleep(0.5)
         print("Uid: ", uid,"\n", "Last cached: ", comms.get_last_cached(uid, "pot0"), "\n", comms.get_last_cached(uid, "pot2"), "\n")

   elif type == "Encoder":
      while True:
         comms.read(uid, ["rotation"])
         time.sleep(0.05)
         comms.read(uid, ["rotation"])
         time.sleep(0.05)
         comms.read(uid, ["rotation"])
         time.sleep(0.05)

   elif type == "BatteryBuzzer":
      comms.subscribe(uid, 100, ["cell1", "cell2", "cell3", "calibrate"])
      while True:
         comms.write(uid, ("calibrate", True))
         time.sleep(0.05)
         comms.write(uid, ("calibrate", False))
         time.sleep(0.5)
         print("Uid: ", uid,"\n", "Last cached: ", comms.get_last_cached(uid, "calibrate"), "\n", comms.get_last_cached(uid, "cell2"), "\n")

   elif type == "TeamFlag":
      comms.subscribe(uid, 100, ["led1", "led2", "led3", "led4", "blue", "yellow"])
      while True:
         comms.write(uid, [("led1", True), ("led2", True), ("led3", False), ("led4", False), ("blue", True), ("yellow", False)])
         time.sleep(0.05)
         comms.write(uid, [("led1", False), ("led2", False), ("led3", True), ("led4", True), ("blue", False), ("yellow", True)])
         time.sleep(0.5)
         print("Uid: ", uid,"\n", "Last cached: ", comms.get_last_cached(uid, "blue"), "\n", comms.get_last_cached(uid, "yellow"), "\n")

   elif type == "YogiBear":
      comms.subscribe(uid, 100, ["duty", "forward"])
      while True:
         comms.write(uid, [("duty", 100),  ("forward", False)])
         time.sleep(0.05)
         comms.write(uid, [("duty", 50),  ("forward", True)])
         time.sleep(0.5)
         print("Uid: ", uid,"\n", "Last cached: ", comms.get_last_cached(uid, "duty"), "\n", comms.get_last_cached(uid, "forward"), "\n")

   elif type == "ServoControl":
      comms.subscribe(uid, 100, ["servo0", "enable0", "servo1", "enable1", "servo2", "enable2", "servo3", "enable3"])
      while True:
         comms.write(uid, [("servo0", 3), ("enable0", False), ("servo1", 3), ("enable1", False), ("servo2", 3), ("enable2", True), ("servo3", 3), ("enable3", False)])
         time.sleep(0.05)
         comms.write(uid, [("servo0", 1), ("enable0", True), ("servo1", 26), ("enable1", True), ("servo2", 30), ("enable2", False), ("servo3", 17), ("enable3", True)])
         time.sleep(0.5)
         print("Uid: ", uid,"\n", "Last cached: ", comms.get_last_cached(uid, "servo1"), "\n", comms.get_last_cached(uid, "enable1"), "\n")

   elif type == "ExampleDevice":
      comms.subscribe(uid, 100, ["kumiko", "hazuki", "sapphire", "reina", "asuka", "haruka", "kaori", "natsuki", "yuko", "mizore", "nozomi", "shuichi", "takuya", "riko", "aoi", "noboru"])
      while True:
         comms.write(uid, [("kumiko", True), ("hazuki", 19), ("sapphire", 12), ("reina", 210), ("asuka", 105), ("haruka", 1005), ("kaori", 551), ("natsuki", 18002), ("yuko", 9001), ("mizore", 6.45), ("nozomi", 33.2875), ("takuya", 331), ("aoi", 7598)])
         time.sleep(0.05)
         comms.write(uid, [("kumiko", False), ("hazuki", 0), ("sapphire", 0), ("reina", 0), ("asuka", 0), ("haruka", 0), ("kaori", 0), ("natsuki", 0), ("yuko", 0), ("mizore", 0.0), ("nozomi", 0.0), ("takuya", 0), ("aoi", 0)])
         time.sleep(0.5)
         print("Uid: ", uid,"\n","Last cached: ", comms.get_last_cached(uid, "kumiko"), "\n", comms.get_last_cached(uid, "hazuki"), "\n")


if __name__ == "__main__":
    
   comms = HibikeCommunicator()
   time.sleep(3)
            
   device_info = comms.get_uids_and_types()
   print(device_info)
   limit_switch = None
   team_flag = None
   for uid, name in device_info:
      if name == "LimitSwitch":
        limit_switch = uid
        comms.subscribe(uid, 40, ["switch0", "switch1", "switch2"])
      elif name == "TeamFlag":
        team_flag = uid
      elif name == "ExampleDevice":
        comms.subscribe(uid, 40, ["kumiko", "hazuki", "sapphire", "reina", "asuka", "haruka", "kaori", "natsuki", "yuko", "mizore", "nozomi", "shuichi", "takuya", "riko", "aoi", "noboru"])
   if limit_switch is None or team_flag is None:
      print("failed to enumerate LimitSwitch and/or TeamFlag")
   time.sleep(1)
   while True:
      if comms.get_last_cached(limit_switch, "switch0")[0]:
         comms.write(team_flag, [("led1", True)])
         comms.write(team_flag, [("led2", False)])
         comms.write(team_flag, [("led3", True)])
         comms.write(team_flag, [("led4", False)])
      else:
         comms.write(team_flag, [("led1", True)])
         comms.write(team_flag, [("led2", False)])
         comms.write(team_flag, [("led3", True)])
         comms.write(team_flag, [("led4", False)])
      time.sleep(0.05)
   
