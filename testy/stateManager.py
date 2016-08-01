# import multiprocessing
import sys

from runtimeUtil import *

class StateManager(object):

  """input is a multiprocessing.Queue object to support multiple 
  processes requesting state data
  """
  def __init__(self, badThingsQueue, inputQueue, runtimePipe):
    self.initRobotState()
    self.badThingsQueue = badThingsQueue
    self.input = inputQueue
    # map process names to pipes
    self.processMapping = {"runtime": runtimePipe}

  def initRobotState(self):
    self.state = [5]

  def addPipe(self, processName, pipe):
    self.processMapping[processName] = pipe
    pipe.send("ready")

  def start(self):
    while True:
      request = self.input.get(block=True)
      if request[0] == "reset":
        self.initRobotState()
      elif request[0] == "add":
        self.addPipe("studentCode", request[1])
      elif request[0] == "hello":
        self.state[0] -= 1
        self.processMapping["studentCode"].send(self.state[0])
      else:
        self.badThingsQueue.put(BadThing(sys.exc_info(), "Unknown process name: %s" % (request,), printStackTrace = False))
