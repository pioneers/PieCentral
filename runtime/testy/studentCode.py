import time
from runtimeUtil import *

def test0_setup():
  print("test0_setup")

def test0_main():
  print("test0_main")

def mainTest_setup():
  pass

def mainTest_main():
  response = Robot.getValue("incrementer")
  print("Get Info:", response)
  response -= 1

  Robot.setValue(response, "incrementer")

  print("Saying hello to the other side")
  print("DAT:", 1.0/response)

def nestedDict_setup():
  pass

def nestedDict_main():
  print("CODE LOOP")

  response = Robot.getValue("dict1", "inner_dict1_int")
  print("Get Info:", response)

  response = 1
  Robot.setValue(response, "dict1", "inner_dict1_int")
  response = Robot.getValue("dict1", "inner_dict1_int")
  print("Get Info2:", response)