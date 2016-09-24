import time
from runtimeUtil import *

def setup(pipe):
  pass
  # startupValue = 5
  # print("Setting Up State = %d" % (startupValue,))
  # state[0] = startupValue

def main(stateQueue, pipe):
  print("CODE LOOP")
  # response = Robot.getValue()
  # print("Get Info:", response)
  
  response = Robot.getValue("dict1", "inner_dict1_int")
  print("Get Info:", response)

  response = 1
  Robot.setValue(response, "dict1", "inner_dict1_int")
  response = Robot.getValue("dict1", "inner_dict1_int")
  print("Get Info2:", response)

  print("Saying hello to the other side")
  print("DAT:", 1.0/response)
