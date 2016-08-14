import multiprocessing
import time
import sys
import traceback

import stateManager
import studentAPI

from runtimeUtil import *


# TODO:
# 0. Set up testing code for the following features.
# 1. Have student code go through api to modify state.
# 2. Imposing timeouts on student code (infinite loop, try-catch)
# 3. Figure out how to kill student thread.
# 4. Integrate with Bob's socket code: spin up a communication process
# 5. stateManager throw badThing on processNameNotFound
# 6. refactor process startup code: higher order function
# 7. Writeup how all this works

allProcesses = {}
badThings = multiprocessing.Condition()
globalBadThing = "unititialized globalBadThing"


def runtime():
  badThingsQueue = multiprocessing.Queue()
  stateQueue = multiprocessing.Queue()
  spawnProcess = processFactory(badThingsQueue, stateQueue)
  restartCount = 0
  try:
    spawnProcess(PROCESS_NAMES.STATE_MANAGER, startStateManager)
    while True:
      if restartCount >= 5:
        print(RUNTIME_INFO.DEBUG_DELIMITER_STRING.value)
        print("Too many restarts, terminating")
        break
      print(RUNTIME_INFO.DEBUG_DELIMITER_STRING.value)
      print("Starting studentCode attempt: %s" % (restartCount,))
      spawnProcess(PROCESS_NAMES.STUDENT_CODE, runStudentCode)
      while True:
        globalBadThing = badThingsQueue.get(block=True)
        print(RUNTIME_INFO.DEBUG_DELIMITER_STRING.value)
        print(globalBadThing)
        if globalBadThing.event == BAD_EVENTS.STUDENT_CODE_ERROR:
          break
      stateQueue.put([SM_COMMANDS.RESET])
      restartCount += 1
  except:
    print(RUNTIME_INFO.DEBUG_DELIMITER_STRING.value)
    print("Funtime Runtime Had Too Much Fun")
    print(traceback.print_exception(*sys.exc_info()))

def runStudentCode(badThingsQueue, stateQueue, pipe):
  try:
    import studentCode
    r = studentAPI.Robot(stateQueue, pipe)
    setattr(studentCode, 'Robot', r)
    studentCode.setup(pipe)
    nextCall = time.time()
    while True:
      studentCode.main(stateQueue, pipe)
      nextCall += 1.0/RUNTIME_INFO.STUDENT_CODE_HZ.value
      time.sleep(nextCall - time.time())
  except Exception:
    badThingsQueue.put(BadThing(sys.exc_info(), None, event=BAD_EVENTS.STUDENT_CODE_ERROR))

def startStateManager(badThingsQueue, stateQueue, runtimePipe):
  try:
    SM = stateManager.StateManager(badThingsQueue, stateQueue, runtimePipe)
    SM.start()
  except Exception:
    badThingsQueue.put(BadThing(sys.exc_info(), None))

def processFactory(badThingsQueue, stateQueue):
  def spawnProcessHelper(processName, helper):
    pipeToChild, pipeFromChild = multiprocessing.Pipe()
    if processName != PROCESS_NAMES.STATE_MANAGER:
      stateQueue.put([SM_COMMANDS.ADD, processName, pipeToChild], block=True)
    newProcess = multiprocessing.Process(target=helper, name=processName.value, args=(badThingsQueue, stateQueue, pipeFromChild))
    allProcesses[processName] = newProcess
    newProcess.daemon = True
    newProcess.start()
  return spawnProcessHelper

runtime()