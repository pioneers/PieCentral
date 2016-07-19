import threading
import time
import sys
import traceback

import studentCode

STUDENT_THREAD_NAME = "studentThread"
STUDENT_THREAD_HZ = 5 # Number of times to execute studentcode.main per second
DEBUG_DELIMITER_STRING = "****************** RUNTIME DEBUG ******************"
# TODO:
# 0. Set up testing code for the following features. 
# 1. Have student code throw an exception. Make sure runtime catches gracefully.
# 2. Have student code go through api to modify state. 
# 3. Create Error class for handling various errors/events

allThreads = []
badThings = threading.Condition()
badEvent = "BAD THINGS HAPPENED"
badThingsData = ["", None]

def runtime():
  restartCount = 0
  state = [0]
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
    print(badThingsData[0])
    print(traceback.print_exception(*badThingsData[1]))
    badThings.release()
    restartCount += 1

def initRobotState(state):
  state[0] = 0

def runStudentCode(state):
  initRobotState(state)
  studentThread = threading.Thread(target=runStudentCodeHelper, name=STUDENT_THREAD_NAME, args=(state,))
  allThreads.append(studentThread)
  studentThread.daemon = True
  studentThread.start()

def runStudentCodeHelper(state):
  try:
    studentCode.setup(state)
    nextCall = time.time()
    while True:
      studentCode.main(state)
      nextCall += 1.0/STUDENT_THREAD_HZ
      time.sleep(nextCall - time.time())
  except Exception:
    badThings.acquire()
    badThingsData[0] = badEvent
    badThingsData[1] = sys.exc_info()
    badThings.notify()
    badThings.release()
runtime()