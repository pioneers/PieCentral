import time

def setup(state):
  startupValue = 5
  print("Setting Up State = %d" % (startupValue,))
  state[0] = startupValue

def main(state):
  print("Hello from the other side %d" % (state[0],))
  1.0/state[0]
  state[0] -= 1
