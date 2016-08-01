import multiprocessing
import time
import sys
import traceback

import studentCode
import stateManager

from runtimeUtil import *

STUDENT_PROCESS_NAME = "studentProcess"
STUDENT_PROCESS_HZ = 5 # Number of times to execute studentCode.main per second
STATE_PROCESS_NAME = "stateProcess"
DEBUG_DELIMITER_STRING = "****************** RUNTIME DEBUG ******************"
# TODO:
# 0. Set up testing code for the following features.
# 1. Have student code go through api to modify state.
# 2. Imposing timeouts on student code (infinite loop, try-catch)
# 3. Figure out how to kill student thread.
# 4. Integrate with Bob's socket code: spin up a communication process
# 5. stateManager throw badThing on processNameNotFound
# 6. refactor process startup code: higher order function

allProcesses = {}
badThings = multiprocessing.Condition()
globalBadThing = "unititialized globalBadThing"


def runtime():
  badThingsQueue = multiprocessing.Queue()
  stateQueue = multiprocessing.Queue()
  restartCount = 0
  try:
    startStateManager(badThingsQueue, stateQueue)
    while True:
      if restartCount >= 5:
        print(DEBUG_DELIMITER_STRING)
        print("Too many restarts, terminating")
        break
      print(DEBUG_DELIMITER_STRING)
      print("Starting studentCode attempt: %s" % (restartCount,))
      runStudentCode(badThingsQueue, stateQueue)
      while True:
        globalBadThing = badThingsQueue.get(block=True)
        print(DEBUG_DELIMITER_STRING)
        print(globalBadThing)
        if globalBadThing.event == "studentCode":
          break
      stateQueue.put(["reset"])
      restartCount += 1
  except:
    print(DEBUG_DELIMITER_STRING)
    print("Funtime Runtime Had Too Much Fun")
    print(traceback.print_exception(*sys.exc_info()))

def runStudentCode(badThingsQueue, stateQueue):
  pipeToStudent, pipeFromStudent = multiprocessing.Pipe()
  stateQueue.put(["add", pipeToStudent], block=True)
  studentProcess = multiprocessing.Process(target=runStudentCodeHelper, name=STUDENT_PROCESS_NAME, args=(badThingsQueue, stateQueue, pipeFromStudent))
  allProcesses[STUDENT_PROCESS_NAME] = studentProcess
  studentProcess.daemon = True
  studentProcess.start()

def runStudentCodeHelper(badThingsQueue, stateQueue, pipe):
  try:
    studentCode.setup(pipe)
    nextCall = time.time()
    while True:
      studentCode.main(stateQueue, pipe)
      nextCall += 1.0/STUDENT_PROCESS_HZ
      time.sleep(nextCall - time.time())
  except Exception:
    badThingsQueue.put(BadThing(sys.exc_info(), None, event="studentCode"))

def startStateManager(badThingsQueue, stateQueue):
  pipeToState, pipeFromState = multiprocessing.Pipe()
  stateProcess = multiprocessing.Process(target=startStateManagerHelper, name=STATE_PROCESS_NAME, args=(badThingsQueue, stateQueue, pipeFromState))
  allProcesses[STATE_PROCESS_NAME] = stateProcess
  stateProcess.daemon = True
  stateProcess.start()

def startStateManagerHelper(badThingsQueue, stateQueue, runtimePipe):
  try:
    SM = stateManager.StateManager(badThingsQueue, stateQueue, runtimePipe)
    SM.start()
  except Exception:
    badThingsQueue.put(BadThing(sys.exc_info(), str(stateQueue)))

runtime()