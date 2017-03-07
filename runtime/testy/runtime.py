import multiprocessing
import time
import os
import signal
import sys
import traceback
import re
import filecmp
import argparse
import inspect
import asyncio

import stateManager
import studentAPI
import Ansible
import runtime_pb2

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

def runtime(testName=""):
  testMode = testName != ""
  maxIter = 3 if testMode else None

  def nonTestModePrint(*args):
    """Prints only if we are NOT in testMode"""
    if not testMode:
      print(args)

  badThingsQueue = multiprocessing.Queue()
  stateQueue = multiprocessing.Queue()
  spawnProcess = processFactory(badThingsQueue, stateQueue)
  restartCount = 0
  emergency_stopped = False

  try:
    spawnProcess(PROCESS_NAMES.STATE_MANAGER, startStateManager)
    spawnProcess(PROCESS_NAMES.UDP_RECEIVE_PROCESS, startUDPReceiver)
    spawnProcess(PROCESS_NAMES.HIBIKE, startHibike)
    controlState = "idle"
    dawn_connected = False

    while True:
      if testMode:
        # Automatically enter telop mode when running tests
        badThingsQueue.put(BadThing(sys.exc_info(),
            "Sending initial command to enter teleop",
            event=BAD_EVENTS.ENTER_TELEOP,
            printStackTrace=False))
      if restartCount >= 3:
        nonTestModePrint(RUNTIME_CONFIG.DEBUG_DELIMITER_STRING.value)
        nonTestModePrint("Too many restarts, terminating")
        break
      if emergency_stopped:
        nonTestModePrint(RUNTIME_CONFIG.DEBUG_DELIMITER_STRING.value)
        nonTestModePrint("terminating due to E-Stop")
        break
      nonTestModePrint(RUNTIME_CONFIG.DEBUG_DELIMITER_STRING.value)
      nonTestModePrint("Starting studentCode attempt: %s" % (restartCount,))
      while True:
        newBadThing = badThingsQueue.get(block=True)
        if newBadThing.event == BAD_EVENTS.NEW_IP and not dawn_connected:
          spawnProcess(PROCESS_NAMES.UDP_SEND_PROCESS, startUDPSender)
          spawnProcess(PROCESS_NAMES.TCP_PROCESS, startTCP)
          dawn_connected = True
          continue
        elif newBadThing.event == BAD_EVENTS.DAWN_DISCONNECTED and dawn_connected:
          #TODO Impelement Dawn Timeout in Ansible.py
          terminate_process(PROCESS_NAMES.UDP_RECEIVE_PROCESS)
          terminate_process(PROCESS_NAMES.UDP_SEND_PROCESS)
          terminate_process(PROCESS_NAMES.TCP_PROCESS)
          spawnProcess(PROCESS_NAMES.UDP_RECEIVE_PROCESS, startUDPReceiver)
          dawn_connected = False
          controlState = "idle"
          break
        elif newBadThing.event == BAD_EVENTS.ENTER_TELEOP and controlState != "teleop":
          terminate_process(PROCESS_NAMES.STUDENT_CODE)
          name = testName or "teleop"
          spawnProcess(PROCESS_NAMES.STUDENT_CODE, runStudentCode, name, maxIter)
          controlState = "teleop"
          continue
        elif newBadThing.event == BAD_EVENTS.ENTER_AUTO and controlState != "auto":
          terminate_process(PROCESS_NAMES.STUDENT_CODE)
          spawnProcess(PROCESS_NAMES.STUDENT_CODE, runStudentCode, "autonomous")
          controlState = "auto"
          continue
        elif newBadThing.event == BAD_EVENTS.ENTER_IDLE and controlState != "idle":
          controlState = "idle"
          break
        print(newBadThing.event)
        nonTestModePrint(newBadThing.data)
        if newBadThing.event in restartEvents:
          if newBadThing.event in studentErrorEvents:
            stateQueue.put([SM_COMMANDS.SEND_CONSOLE, [str(newBadThing)]])
          controlState = "idle"
          restartCount += 1
          if not emergency_stopped and newBadThing.event is BAD_EVENTS.EMERGENCY_STOP:
            emergency_stopped = True #somehow kill student code using other method? right now just restarting on e-stop
          break
      if testMode:
        stateQueue.put([SM_COMMANDS.RESET, []])
      terminate_process(PROCESS_NAMES.STUDENT_CODE)
      stateQueue.put([SM_COMMANDS.SET_VAL, [runtime_pb2.RuntimeData.STUDENT_STOPPED, ["studentCodeState"], False]])
    nonTestModePrint(RUNTIME_CONFIG.DEBUG_DELIMITER_STRING.value)
    print("Funtime Runtime is done having fun.")
    print("TERMINATING")
  except Exception as e:
    print(RUNTIME_CONFIG.DEBUG_DELIMITER_STRING.value)
    print("Funtime Runtime had too much fun.")
    print(e)
    print("".join(traceback.format_tb(sys.exc_info()[2])))


def runStudentCode(badThingsQueue, stateQueue, pipe, testName="", maxIter=None):
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
    try:
      setupFunc = getattr(studentCode, testName + "setup")
    except AttributeError:
      raise RuntimeError("Student code failed to define '{}'".format(test_name + "setup"))
    try:
      mainFunc = getattr(studentCode, testName + "main")
    except AttributeError:
      raise RuntimeError("Student code failed to define '{}'".format(test_name + "main"))

    ensure_is_function(testName + "setup", setupFunc)
    ensure_is_function(testName + "main", mainFunc)
    ensure_not_overridden(studentCode, "Robot")

    studentCode.Robot = studentAPI.Robot(stateQueue, pipe)
    studentCode.Gamepad = studentAPI.Gamepad(stateQueue, pipe)
    studentCode.Actions = studentAPI.Actions
    studentCode.print = studentCode.Robot._print

    checkTimedOut(setupFunc)

    exception_cell = [None]
    clarify_coroutine_warnings(exception_cell)

    async def main_loop():
      execCount = 0
      while not terminated and (exception_cell[0] is None) and (maxIter is None or execCount < maxIter):
        next_call = loop.time() + 1. / RUNTIME_CONFIG.STUDENT_CODE_HZ.value
        checkTimedOut(mainFunc)

        sleep_time = max(next_call - loop.time(), 0.)
        stateQueue.put([SM_COMMANDS.STUDENT_MAIN_OK, []])
        execCount += 1
        await asyncio.sleep(sleep_time)
      if not terminated:
        badThingsQueue.put(BadThing(sys.exc_info(), "Process Ended", event=BAD_EVENTS.END_EVENT))
      if exception_cell[0] is not None:
        raise exception_cell[0]

    loop = asyncio.get_event_loop()

    def my_exception_handler(loop, context):
      if exception_cell[0] is None:
        exception_cell[0] = context["exception"]

    loop.set_exception_handler(my_exception_handler)
    loop.run_until_complete(main_loop())

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
    badThingsQueue.put(BadThing(sys.exc_info(), str(e), event=BAD_EVENTS.STATE_MANAGER_CRASH))

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

def startTCP(badThingsQueue, stateQueue, smPipe):
  try:
    recvClass = Ansible.TCPClass(badThingsQueue, stateQueue, smPipe)
    recvClass.start()
  except Exception as e:
    badThingsQueue.put(BadThing(sys.exc_info(), str(e), event=BAD_EVENTS.TCP_ERROR))

def processFactory(badThingsQueue, stateQueue, stdoutRedirect=None):
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

def terminate_process(processName):
  if processName not in allProcesses:
    return
  process = allProcesses.pop(processName)
  process.terminate()
  for _ in range(100): # Gives 1 sec for process to terminate but allows it to terminate quicker
    time.sleep(.01) # Give the OS a chance to terminate the other process
    if not process.is_alive():
      break
  if process.is_alive():
    print("Terminating with EXTREME PREJUDICE")
    print("Queue state is probably boned and we should restart entire runtime")
    print("Boned Process:", processName)
    os.kill(process.pid, signal.SIGKILL)
    raise NotImplementedError

def runtimeTest(testNames):
  # Normally dangerous. Allowed here because we put testing code there.
  import studentCode

  testNameRegex = re.compile(".*_setup")
  allTestNames = [testName[:-len("_setup")] for testName in dir(studentCode) if testNameRegex.match(testName)]

  if not testNames:
    print("Running all non-optional tests")
    testNames = [testName for testName in allTestNames if not testName.startswith('optional')]
  else:
    for testName in testNames:
      if testName not in allTestNames:
        print("Error: {} not found.".format(testName))
        return

  failCount = 0
  failedTests = []

  for testName in testNames:
    if testName in ["autonomous", "teleop"]:
      continue
    testFileName = "%s_output" % (testName,)
    with open(testFileName, "w", buffering=1) as testOutput:
      print("Running test: {}".format(testName), end="", flush=True)
      sys.stdout = testOutput

      allProcesses.clear()

      runtime(testName)

      # Terminate Ansible to free up ports for further tests
      terminate_process(PROCESS_NAMES.UDP_RECEIVE_PROCESS)
      if PROCESS_NAMES.UDP_SEND_PROCESS in allProcesses:
        terminate_process(PROCESS_NAMES.UDP_SEND_PROCESS)
      if PROCESS_NAMES.TCP_PROCESS in allProcesses:
        terminate_process(PROCESS_NAMES.TCP_PROCESS)
      sys.stdout = sys.__stdout__
      print("{}DONE!".format(" " * (50-len(testName))))

    if testSuccess(testFileName):
      os.remove(testFileName)
    else:
      # Explicitly set output to terminal, since we overwrote it earlier
      failCount += 1
      failedTests.append(testName)

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
    sys.exit(1)

def testSuccess(testFileName):
  expectedOutput = RUNTIME_CONFIG.TEST_OUTPUT_DIR.value + testFileName
  testOutput = testFileName
  return filecmp.cmp(expectedOutput, testOutput)

def startHibike(badThingsQueue, stateQueue, pipe):
  # badThingsQueue - queue to runtime
  # stateQueue - queue to stateManager
  # pipe - pipe from statemanager
  def addPaths():
    """Modify sys.path so we can find hibike.
    """
    path = os.path.dirname(os.path.abspath(__file__))
    parent_path = path.rstrip("runtime/testy")
    hibike = os.path.join(parent_path, "hibike")
    sys.path.insert(1, hibike)

  try:
    addPaths()
    import hibike_process
    hibike_process.hibike_process(badThingsQueue, stateQueue, pipe)
  except Exception as e:
    badThingsQueue.put(BadThing(sys.exc_info(), str(e)))

def ensure_is_function(tag, val):
  if inspect.iscoroutinefunction(val):
    raise RuntimeError("{} is defined with `async def` instead of `def`".format(tag))
  if not inspect.isfunction(val):
    raise RuntimeError("{} is not a function".format(tag))

def ensure_not_overridden(module, name):
  if hasattr(module, name):
    raise RuntimeError("Student code overrides `{}`, which is part of the API".format(name))

def clarify_coroutine_warnings(exception_cell):
  """
  Python's default error checking will print warnings of the form:
      RuntimeWarning: coroutine '???' was never awaited

  This function will will upgrade such a warning to a fatal error,
  while also injecting a additional clarification message about possible causes.
  """
  import warnings

  default_showwarning = warnings.showwarning

  def custom_showwarning(message, category, filename, lineno, file=None, line=None):
    default_showwarning(message, category, filename, lineno, line)

    if str(message).endswith("was never awaited"):
      coro_name = str(message).split("'")[-2]

      print("""
The PiE API has upgraded the above RuntimeWarning to a runtime error!

This error typically occurs in one of the following cases:

1. Calling `Actions.sleep` or anything in `Actions` without using `await`.

Incorrect code:
    async def my_coro():
        Actions.sleep(1.0)

Consider instead:
    async def my_coro():
        await Actions.sleep(1.0)

2. Calling an `async def` function from inside `setup` or `loop` without using
`Robot.run`.

Incorrect code:
    def loop():
        my_coro()

Consider instead:
    def loop():
        Robot.run(my_coro)
""".format(coro_name=coro_name), file=file)
      exception_cell[0] = message

  warnings.showwarning = custom_showwarning

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test", nargs="*",
        help="Run specified tests. If no arguments, run all tests.")
    args = parser.parse_args()
    if args.test is None:
      runtime()
    else:
      runtimeTest(args.test)
