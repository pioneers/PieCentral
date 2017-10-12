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
          Set up the pipes for communication between the device and the BeagleBone, creates a thread to recieve communications from the device, starts up the process that runs the communication, and sets up a dictionary that caches all device values sent to it.
      """
      
      # This block creates the pipes
      self.pipeToChild, pipeFromChild = multiprocessing.Pipe()
      
      # This block creates the process
      badThingsQueue = multiprocessing.Queue()
      self.stateQueue = multiprocessing.Queue()
      newProcess = multiprocessing.Process(target=hp.hibike_process, name="hibike_sim", args=[badThingsQueue,self.stateQueue, pipeFromChild])
      newProcess.daemon = True
      newProcess.start()
      self.enumerate()
      
      # Creates the list of uids
      self.uids = set()
      
      # This block creates the thread
      outThread =  threading.Thread(target = self.process_output)
      outThread.start()
   
      # Create the device values dictionary cache
      self.device_values_cache = {}

   def process_output(self):
      """
         Processes the output uploaded to the state queue by te devices
         If it's a subscription response from a device whose uid is not in self.uids, the uid will be added to self.uids
         If it's a device disconnection from a device whose uid in self.uids, the uid will be removed from self.uids
         If it's a device value, cache it in the dictionary
      """
      while True:
         output = self.stateQueue.get()
         #print("Output: ", output)

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
            uid = 0
            for key in output[1][0].keys():
                uid = key
                #print ("Key is", uid, "this is key")
                #break
                
            #print("UID: ", uid, "\n")
            try:
                params_values = output[1][0][uid]
            except KeyError:
                #print("No UIDs detected for a device_values request")
                params_values = [{}]
             
            for param_val_tuple in params_values:
                try:
                    parameter = param_val_tuple[0]
                    value = param_val_tuple[1]
                except KeyError: # Treat a tuple with a missing value as if it didn't exist, except to print an error message
                    #print("Error: Params and Values tuple ", param_val_tuple, " has a missing value")
                    continue
                if uid not in self.device_values_cache:
                   self.device_values_cache.update({uid: {parameter: (value, time.time())}})
                else:
                   self.device_values_cache[uid].update({parameter: (value, time.time())})
   
   def get_last_cached(self, uid, param):
      """
         Returns a tuple of the value and the timestamp of the last device_values package recieved from a uid and a parameter
         Precondition: a device_data with a UID, params, and values must have been recieved from the param before calling this function
      """
      #print("Where the error is coming from: ", self.device_values_cache)
      try:
         return self.device_values_cache[uid][param]
      except KeyError:
         print("Keyerror detected, returning zero as last cached")
         return 0

   
   def get_uids_and_types(self):
      """
         Returns a list of tuples of all of the uids of all devices that the HibikeCommunicator talks to
         Tuple structure: (uid, device type name)
      """
      list = []
      for uid in self.uids:
         list.append((uid, hm.uid_to_device_name(uid)))
      return list
   
   def enumerate(self):
      """
          Sends an enumeration order to hibike_process to ping all devices
      """
      self.pipeToChild.send(["enumerate_all", []])

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
# Helper function designed to run a script
#def device_comms(comms, uid_type_tuple, script, item_delay, repeat_delay):
   """
        Given a Hibike_Communicator and a device's UID and type, repeatedly carries out a script given to it by the caller with a user specified delay between each item in the script and each iteration of the script
        Commented out due to an error
        
        comms: the Hibike_Communicator
        uid_type_tuple: a tuple that looks like this: (UID, device type)
        script: a script of commands to send to hibike_communcator
        item_delay: a timed-delay between script items
        repeat_delay: the amount of time after the end of the script that the script is done again
        Precondition: uid_type_tuple must be an element of comms.get_uids_and_types()
        Precondition: script is a list of function calls, usually HibikeCommunicator functions or print (the latter to print out cached data and other output from the various systems
   """
   #print("UID type tuple: ", uid_type_tuple)
   
   #uid = uid_type_tuple[0]
   #type = uid_type_tuple[1]
   
   # Run every item in the user-given script
   #while True:
      #for item in script:
         #try:
            #item()
            #print("Item run")
         #except KeyError:
            #print("Error: no entry for UID :", uid)
         #except TypeError:
            #print("Object not in callable format")
         #time.sleep(item_delay)
      #print("Done with one cycle")
      #time.sleep(repeat_delay)


# What happens when hibike_communicator is called to be tested
# Also a template for how to run hibike_communicator
if __name__ == "__main__":
    # Set up the
   comms = HibikeCommunicator()
   time.sleep(3)
            
   device_info = comms.get_uids_and_types()
        
   # For each device, executes a set of commands in a cycle
   # This function has a set of standard scripts and delays for each device, but you can choose whatever scripts you like
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

      #print(uid_type_tuple)
      #process_thread = threading.Thread(target = device_comms, args = [comms, uid_type_tuple, script, time_delay, repeat_delay])
      #process_thread.start()

