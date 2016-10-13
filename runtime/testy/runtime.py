import multiprocessing
import time
import os
import signal
import sys
import traceback
import re
import filecmp

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
        if newBadThing.event in restartEvents:
          break
      stateQueue.put([SM_COMMANDS.RESET, []])
      os.kill(allProcesses[PROCESS_NAMES.STUDENT_CODE].pid, signal.SIGKILL)
      restartCount += 1
    print(RUNTIME_CONFIG.DEBUG_DELIMITER_STRING.value)
    print("Funtime Runtime is done having fun.")
    print("TERMINATING")
  except:
    print(RUNTIME_CONFIG.DEBUG_DELIMITER_STRING.value)
    print("Funtime Runtime Had Too Much Fun")
    print(traceback.print_exception(*sys.exc_info()))

def runStudentCode(badThingsQueue, stateQueue, pipe, testName = "", maxIter = 0):
  try:
    import signal
    def timedOutHandler(signum, frame):
      raise TimeoutError("studentCode timed out")
    signal.signal(signal.SIGALRM, timedOutHandler)

    def checkTimedOut(func, *args):
      signal.alarm(RUNTIME_CONFIG.STUDENT_CODE_TIMEOUT.value)
      func(*args)
      signal.alarm(0)

    signal.alarm(RUNTIME_CONFIG.STUDENT_CODE_TIMEOUT.value)
    import studentCode
    signal.alarm(0)

    if testName != "":
      testName += "_"
    setupFunc = getattr(studentCode, testName + "setup")
    mainFunc = getattr(studentCode, testName + "main")

    r = studentAPI.Robot(stateQueue, pipe)
    studentCode.Robot = r

    checkTimedOut(setupFunc)

    nextCall = time.time()
    # TODO: Replace execCount with a value in stateManager
    execCount = 0
    while maxIter == 0 or execCount < maxIter:
      checkTimedOut(mainFunc)
      nextCall += 1.0/RUNTIME_CONFIG.STUDENT_CODE_HZ.value
      stateQueue.put([SM_COMMANDS.STUDENT_MAIN_OK, []])
      time.sleep(nextCall - time.time())

      execCount += 1

    badThingsQueue.put(BadThing(sys.exc_info(), "Process Ended", event=BAD_EVENTS.END_EVENT))

  except TimeoutError:
    badThingsQueue.put(BadThing(sys.exc_info(), None, event=BAD_EVENTS.STUDENT_CODE_TIMEOUT))
  except StudentAPIError:
    badThingsQueue.put(BadThing(sys.exc_info(), None, event=BAD_EVENTS.STUDENT_CODE_ERROR))
  except Exception: #something broke in student code
    badThingsQueue.put(BadThing(sys.exc_info(), None, event=BAD_EVENTS.STUDENT_CODE_ERROR))

def startStateManager(badThingsQueue, stateQueue, runtimePipe):
  try:
    SM = stateManager.StateManager(badThingsQueue, stateQueue, runtimePipe)
    SM.start()
  except Exception:
    badThingsQueue.put(BadThing(sys.exc_info(), None))

def processFactory(badThingsQueue, stateQueue, stdoutRedirect = None):
  def spawnProcessHelper(processName, helper, *args):
    pipeToChild, pipeFromChild = multiprocessing.Pipe()
    if processName != PROCESS_NAMES.STATE_MANAGER:
      stateQueue.put([SM_COMMANDS.ADD, [processName, pipeToChild]], block=True)
      pipeFromChild.recv()
    newProcess = multiprocessing.Process(target=helper, name=processName.value, args=[badThingsQueue, stateQueue, pipeFromChild] + list(args))
    allProcesses[processName] = newProcess
    newProcess.daemon = True
    newProcess.start()
  return spawnProcessHelper

def runtimeTest():
  # Normally dangerous. Allowed here because we put testing code there.
  import studentCode

  testNameRegex = re.compile(".*_setup")
  testNames = [testName[:-len("_setup")] for testName in dir(studentCode) if testNameRegex.match(testName)]

  failCount = 0
  failedTests = []

  for testName in testNames:
    testFileName = "%s_output" % (testName,)
    with open(testFileName, "w", buffering = 1) as testOutput:
      sys.stdout = testOutput

      allProcesses.clear()

      badThingsQueue = multiprocessing.Queue()
      stateQueue = multiprocessing.Queue()
      spawnProcess = processFactory(badThingsQueue, stateQueue, sys.stdout)
      restartCount = 0

      try:
        spawnProcess(PROCESS_NAMES.STATE_MANAGER, startStateManager)
        while True:
          if restartCount >= 3:
            break
          spawnProcess(PROCESS_NAMES.STUDENT_CODE, runStudentCode, testName, 3)
          while True:
            newBadThing = badThingsQueue.get(block=True)
            print(newBadThing.event)
            if newBadThing.event in restartEvents:
              break
          stateQueue.put([SM_COMMANDS.RESET, []])
          os.kill(allProcesses[PROCESS_NAMES.STUDENT_CODE].pid, signal.SIGKILL)
          restartCount += 1
        print("Funtime Runtime is done having fun.")
        print("TERMINATING")
      except:
        print("Funtime Runtime Had Too Much Fun")

    if not testSuccess(testFileName):
      # Explicitly set output to terminal, since we overwrote it earlier
      failCount += 1
      failedTests.append(testName)
    else:
      os.remove(testFileName)

  # Restore output to terminal
  sys.stdout = sys.__stdout__
  if failCount == 0:
    print("All {0} tests passed.".format(len(testNames)))
  else:
    print("{0} of the {1} tests failed.".format(failCount, len(testNames)))
    print("Output saved in {{test_name}}_output.")
    print("Inspect with 'diff {{test_name}}_output {0}{{test_name}}_output".format(RUNTIME_CONFIG.TEST_OUTPUT_DIR.value))
    for testName in failedTests:
      print("    {0}".format(testName))


def testSuccess(testFileName):
  expectedOutput = RUNTIME_CONFIG.TEST_OUTPUT_DIR.value + testFileName
  testOutput = testFileName
  return filecmp.cmp(expectedOutput, testOutput)

if __name__ == "__main__":
  runtimeTest()
