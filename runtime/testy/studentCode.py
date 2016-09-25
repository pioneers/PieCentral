import time
from runtimeUtil import *

def setup(pipe):
  pass
  # startupValue = 5
  # print("Setting Up State = %d" % (startupValue,))
  # state[0] = startupValue

def main(stateQueue, pipe):
  response = Robot.getValue("incrementer")
  print("Get Info:", response)
  response -= 1

  Robot.setValue(response, "incrementer")

  print("Saying hello to the other side")
  print("DAT:", 1.0/response)

