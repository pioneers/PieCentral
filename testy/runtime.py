import threading
import time
import sys
import traceback

import studentCode

from runtimeUtil import *

STUDENT_THREAD_NAME = "studentThread"
STUDENT_THREAD_HZ = 5 # Number of times to execute studentcode.main per second
DEBUG_DELIMITER_STRING = "****************** RUNTIME DEBUG ******************"
# TODO:
# 0. Set up testing code for the following features. 
# 1. Have student code throw an exception. Make sure runtime catches gracefully.
# 2. Have student code go through api to modify state. 
# 3. Create Error class for handling various errors/events

allThreads = {}
badThings = threading.Condition()
globalBadThing = None

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
      badThings.acquire()
      badThings.wait()
      print(DEBUG_DELIMITER_STRING)
      print(globalBadThing)
      badThings.release()
      restartCount += 1
  except:
    print(DEBUG_DELIMITER_STRING)
    print("Funtime Runtime Had Too Much Fun")
    print(traceback.print_exception(*sys.exc_info()))

def initRobotState(state):
  state[0] = 0

def runStudentCode(state):
  initRobotState(state)
  studentThread = threading.Thread(target=runStudentCodeHelper, name=STUDENT_THREAD_NAME, args=(state,))
  allThreads[STUDENT_THREAD_NAME] = studentThread
  studentThread.daemon = True
  studentThread.start()

def runStudentCodeHelper(state):
  global globalBadThing
  try:
    studentCode.setup(state)
    nextCall = time.time()
    while True:
      studentCode.main(state)
      nextCall += 1.0/STUDENT_THREAD_HZ
      time.sleep(nextCall - time.time())
  except Exception:
    badThings.acquire()
    globalBadThing = BadThing(sys.exc_info(), None)
    badThings.notify()
    badThings.release()
runtime()