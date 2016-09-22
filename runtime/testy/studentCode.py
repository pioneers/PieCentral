import time
from runtimeUtil import *

def setup(pipe):
  pass
  # startupValue = 5
  # print("Setting Up State = %d" % (startupValue,))
  # state[0] = startupValue

def main(stateQueue, pipe):
  # while True:
  #   pass
  stateQueue.put([SM_COMMANDS.GET_VAL, "incrementer"])
  response = pipe.recv()
  print("Get Info:", response)
  response -= 1

  stateQueue.put([SM_COMMANDS.SET_VAL, "incrementer", response])
  response = pipe.recv()
  print("Set info:", response)

  # stateQueue.put([SM_COMMANDS.GET_VAL, "float1"])
  # response = pipe.recv()
  # print("Get Info:", response)

  print("Saying hello to the other side")
  print("DAT:", 1.0/response)
  