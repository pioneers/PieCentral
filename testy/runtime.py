import multiprocessing
import time
import sys
import traceback

import studentCode

from runtimeUtil import *

STUDENT_PROCESS_NAME = "studentProcess"
STUDENT_PROCESS_HZ = 5 # Number of times to execute studentcode.main per second
DEBUG_DELIMITER_STRING = "****************** RUNTIME DEBUG ******************"
# TODO:
# 0. Set up testing code for the following features.
# 1. Have student code go through api to modify state.
# 2. Imposing timeouts on student code (infinite loop, try-catch)
# 3. Figure out how to kill student thread.
# 4. Integrate with Bob's socket code: spin up a communication process

allProcesses = {}
badThings = multiprocessing.Condition()
globalBadThing = "unititialized globalBadThing"

badThingsQueue = multiprocessing.Queue()

def runtime():
  restartCount = 0
  state = [0]
  try:
    while True:
      if restartCount >= 5:
        print(DEBUG_DELIMITER_STRING)
        print("Too many restarts, terminating")
        break
      print(DEBUG_DELIMITER_STRING)
      print("Starting studentCode attempt: %s" % (restartCount,))
      runStudentCode(state)
      globalBadThing = badThingsQueue.get(block=True)
      print(DEBUG_DELIMITER_STRING)
      print(globalBadThing)
      restartCount += 1
  except:
    print(DEBUG_DELIMITER_STRING)
    print("Funtime Runtime Had Too Much Fun")
    print(traceback.print_exception(*sys.exc_info()))

def initRobotState(state):
  state[0] = 0

def runStudentCode(state):
  initRobotState(state)
  studentProcess = multiprocessing.Process(target=runStudentCodeHelper, name=STUDENT_PROCESS_NAME, args=(state,))
  allProcesses[STUDENT_PROCESS_NAME] = studentProcess
  studentProcess.daemon = True
  studentProcess.start()

def runStudentCodeHelper(state):
  try:
    studentCode.setup(state)
    nextCall = time.time()
    while True:
      studentCode.main(state)
      nextCall += 1.0/STUDENT_PROCESS_HZ
      time.sleep(nextCall - time.time())
  except Exception:
    badThingsQueue.put(BadThing(sys.exc_info(), None))
runtime()