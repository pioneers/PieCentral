import multiprocessing
import time
import os
import signal
import sys
import traceback

import stateManager
import studentAPI

from runtimeUtil import *


# TODO:
# 0. Set up testing code for the following features.
# DONE 1. Have student code go through api to modify state.
# DONE 2. Imposing timeouts on student code (infinite loop, try-catch)
# 3. Figure out how to kill student thread.
# 4. Integrate with Bob's socket code: spin up a communication process
# 5. stateManager throw badThing on processNameNotFound
# 6. refactor process startup code: higher order function
# 7. Writeup how all this works
# 8. Investigate making BadThing extend exception
# DONE 9. Add count for number of times studentCode.main has run

allProcesses = {}

# TODO:
# 0. Set up testing code for the following features. 
# 1. Have student code throw an exception. Make sure runtime catches gracefully.
# 2. Have student code go through api to modify state. 


def runtime():
  badThingsQueue = multiprocessing.Queue()
  stateQueue = multiprocessing.Queue()
  spawnProcess = processFactory(badThingsQueue, stateQueue)
  restartCount = 0
  try:
    spawnProcess(PROCESS_NAMES.STATE_MANAGER, startStateManager)
    while True:
      if restartCount >= 5:
        print(RUNTIME_CONFIG.DEBUG_DELIMITER_STRING.value)
        print("Too many restarts, terminating")
        break
      print(RUNTIME_CONFIG.DEBUG_DELIMITER_STRING.value)
      print("Starting studentCode attempt: %s" % (restartCount,))
      spawnProcess(PROCESS_NAMES.STUDENT_CODE, runStudentCode)
      while True:
        newBadThing = badThingsQueue.get(block=True)
        print(RUNTIME_CONFIG.DEBUG_DELIMITER_STRING.value)
        print(newBadThing)
        if (newBadThing.event == BAD_EVENTS.STUDENT_CODE_ERROR) or \
            (newBadThing.event == BAD_EVENTS.STUDENT_CODE_TIMEOUT):
          break
      stateQueue.put([SM_COMMANDS.RESET])
      os.kill(allProcesses[PROCESS_NAMES.STUDENT_CODE].pid, signal.SIGKILL)
      restartCount += 1
    print(RUNTIME_CONFIG.DEBUG_DELIMITER_STRING.value)
    print("Funtime Runtime is done having fun.")
    print("TERMINATING")
  except:
    print(RUNTIME_CONFIG.DEBUG_DELIMITER_STRING.value)
    print("Funtime Runtime Had Too Much Fun")
    print(traceback.print_exception(*sys.exc_info()))

def runStudentCode(badThingsQueue, stateQueue, pipe):
  try:
    import signal
    def timed_out_handler(signum, frame):
      raise TimeoutError("studentCode timed out")
    signal.signal(signal.SIGALRM, timed_out_handler)

    signal.alarm(RUNTIME_CONFIG.STUDENT_CODE_TIMEOUT.value)
    import studentCode
    signal.alarm(0)

    r = studentAPI.Robot(stateQueue, pipe)
    studentCode.Robot = r

    signal.alarm(RUNTIME_CONFIG.STUDENT_CODE_TIMEOUT.value)
    studentCode.setup(pipe)
    signal.alarm(0)

    nextCall = time.time()
    while True:
      signal.alarm(RUNTIME_CONFIG.STUDENT_CODE_TIMEOUT.value)
      studentCode.main(stateQueue, pipe)
      signal.alarm(0)
      nextCall += 1.0/RUNTIME_CONFIG.STUDENT_CODE_HZ.value
      # TODO: Replace with count of times we call main
      stateQueue.put([SM_COMMANDS.HELLO])
      time.sleep(nextCall - time.time())
  except TimeoutError:
    badThingsQueue.put(BadThing(sys.exc_info(), None, event=BAD_EVENTS.STUDENT_CODE_TIMEOUT))
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

if __name__ == "__main__":
  runtime()
