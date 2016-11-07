import multiprocessing
import time
import os
import signal
import sys
import traceback
import re
import filecmp
import argparse

import stateManager
import studentAPI
import Ansible

from runtimeUtil import *

import hibikeSim

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

def runtime():
  badThingsQueue = multiprocessing.Queue()
  stateQueue = multiprocessing.Queue()
  spawnProcess = processFactory(badThingsQueue, stateQueue)
  restartCount = 0
  try:
    spawnProcess(PROCESS_NAMES.STATE_MANAGER, startStateManager)
    spawnProcess(PROCESS_NAMES.UDP_SEND_PROCESS, startUDPSender)
    spawnProcess(PROCESS_NAMES.UDP_RECEIVE_PROCESS, startUDPReceiver)
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
        print(newBadThing.event)
        if newBadThing.event in restartEvents:
          break
      stateQueue.put([SM_COMMANDS.RESET, []])
      terminate_process(allProcesses[PROCESS_NAMES.STUDENT_CODE])
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

    terminated = False
    def sigTermHandler(signum, frame):
      nonlocal terminated
      terminated = True
    signal.signal(signal.SIGTERM, sigTermHandler)

    def timedOutHandler(signum, frame):
      raise TimeoutError("studentCode timed out")
    signal.signal(signal.SIGALRM, timedOutHandler)

    def checkTimedOut(func, *args):
      signal.alarm(RUNTIME_CONFIG.STUDENT_CODE_TIMELIMIT.value)
      func(*args)
      signal.alarm(0)

    signal.alarm(RUNTIME_CONFIG.STUDENT_CODE_TIMELIMIT.value)
    import studentCode
    signal.alarm(0)

    if testName != "":
      testName += "_"
    setupFunc = getattr(studentCode, testName + "setup")
    mainFunc = getattr(studentCode, testName + "main")

    r = studentAPI.Robot(stateQueue, pipe)
    studentCode.Robot = r

    checkTimedOut(setupFunc)

    # TODO: Replace execCount with a value in stateManager
    execCount = 0
    while (not terminated) and (maxIter == 0 or execCount < maxIter):
      checkTimedOut(mainFunc)
      nextCall = time.time()
      nextCall += 1.0/RUNTIME_CONFIG.STUDENT_CODE_HZ.value
      stateQueue.put([SM_COMMANDS.STUDENT_MAIN_OK, []])
      time.sleep(max(nextCall - time.time(), 0))
      execCount += 1

    badThingsQueue.put(BadThing(sys.exc_info(), "Process Ended", event=BAD_EVENTS.END_EVENT))

  except TimeoutError:
    badThingsQueue.put(BadThing(sys.exc_info(), None, event=BAD_EVENTS.STUDENT_CODE_TIMEOUT))
  except StudentAPIError:
    badThingsQueue.put(BadThing(sys.exc_info(), None, event=BAD_EVENTS.STUDENT_CODE_VALUE_ERROR))
  except Exception as e: #something broke in student code
    badThingsQueue.put(BadThing(sys.exc_info(), None, event=BAD_EVENTS.STUDENT_CODE_ERROR))

def startStateManager(badThingsQueue, stateQueue, runtimePipe):
  try:
    SM = stateManager.StateManager(badThingsQueue, stateQueue, runtimePipe)
    SM.start()
  except Exception as e:
    badThingsQueue.put(BadThing(sys.exc_info(), str(e)))

def startUDPSender(badThingsQueue, stateQueue, smPipe):
  try:
    sendClass = Ansible.UDPSendClass(badThingsQueue, stateQueue, smPipe)
    sendClass.start()
  except Exception as e:
    badThingsQueue.put(BadThing(sys.exc_info(), str(e), event=BAD_EVENTS.UDP_SEND_ERROR))

def startUDPReceiver(badThingsQueue, stateQueue, smPipe):
  try:
    recvClass = Ansible.UDPRecvClass(badThingsQueue, stateQueue, smPipe)
    recvClass.start()
  except Exception as e:
    badThingsQueue.put(BadThing(sys.exc_info(), str(e), event=BAD_EVENTS.UDP_RECV_ERROR))

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

def terminate_process(process):
  process.terminate()
  time.sleep(.01) # Give the OS a chance to terminate the other process
  if process.is_alive():
    print("Termintating with EXTREME PREJUDICE")
    print("Queue state is probably boned and we should restart entire runtime")
    os.kill(process.pid, signal.SIGKILL)
    raise NotImplementedError

def runtimeTest(testNames):
  # Normally dangerous. Allowed here because we put testing code there.
  import studentCode

  testNameRegex = re.compile(".*_setup")
  allTestNames = [testName[:-len("_setup")] for testName in dir(studentCode) if testNameRegex.match(testName)]

  if len(testNames) == 0:
    print("Running all tests")
    testNames = allTestNames
  else:
    for testName in testNames:
      if testName not in allTestNames:
        print("Error: {} not found.".format(testName))
        return

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
        spawnProcess(PROCESS_NAMES.HIBIKE, startHibike)
        while True:
          if restartCount >= 3:
            break
          spawnProcess(PROCESS_NAMES.STUDENT_CODE, runStudentCode, testName, 3)
          while True:
            try:
              newBadThing = badThingsQueue.get(block=True)
              print(newBadThing.event)
              if newBadThing.event in restartEvents:
                break
            except Exception as e:
              print(e)
          stateQueue.put([SM_COMMANDS.RESET, []])
          terminate_process(allProcesses[PROCESS_NAMES.STUDENT_CODE])
          restartCount += 1
        print("Funtime Runtime is done having fun.")
        print("TERMINATING")
      except Exception as e:
        print("Funtime Runtime Had Too Much Fun")
        print(e)
        print("".join(traceback.format_tb(sys.exc_info()[2])))

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

def startHibike(badThingsQueue, stateQueue, pipe):
  # badThingsQueue - queue to runtime
  # stateQueue - queue to stateManager
  # pipe - pipe from statemanager
  try:
    hibike = hibikeSim.HibikeSimulator(badThingsQueue, stateQueue, pipe)
    hibike.start()
  except Exception as e:
    badThingsQueue.put(BadThing(sys.exc_info(), str(e)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--test', nargs='*', help='Run specified tests. If no arguments, run all tests.')
    args = parser.parse_args()
    if args.test == None:
      runtime()
    else:
      runtimeTest(args.test)
