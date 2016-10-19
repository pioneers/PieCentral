import traceback
import multiprocessing
from enum import Enum, unique

@unique
class BAD_EVENTS(Enum):
  BAD_EVENT                 = "BAD THINGS HAPPENED"
  STUDENT_CODE_ERROR        = "Student Code Crashed"
  STUDENT_CODE_VALUE_ERROR  = "Student Code Value Error"
  STUDENT_CODE_TIMEOUT      = "Student Code Timed Out"
  UNKNOWN_PROCESS           = "Unknown State Manager process name"
  STATE_MANAGER_KEY_ERROR   = "Error accessing key in State Manager"
  END_EVENT                 = "Process terminated" # Used for testing

restartEvents = [BAD_EVENTS.STUDENT_CODE_ERROR, BAD_EVENTS.STUDENT_CODE_TIMEOUT, BAD_EVENTS.END_EVENT]

@unique
class PROCESS_NAMES(Enum):
  STUDENT_CODE        = "studentProcess"
  STATE_MANAGER       = "stateProcess"
  RUNTIME             = "runtime"
  HIBIKE              = "hibike"

@unique
class HIBIKE_COMMANDS(Enum):
  ENUMERATE = "enumerate_all"
  SUBSCRIBE = "subscribe_device"
  WRITE     = "write_params"
  READ      = "read_params"

# TODO: Remove when Hibike is finished
@unique
class HIBIKE_RESPONSE(Enum):
  DEVICE_SUBBED = "device_subscribed"

@unique
class SM_COMMANDS(Enum):
  # Used to autoenumerate
  # Don't ask I don't know how
  # https://docs.python.org/3/library/enum.html#autonumber
  def __new__(cls):
    value = len(cls.__members__) + 1
    obj = object.__new__(cls)
    obj._value_ = value
    return obj

  RESET               = ()
  ADD                 = ()
  STUDENT_MAIN_OK     = ()
  GET_VAL             = ()
  SET_VAL             = ()
  CREATE_KEY          = ()

class RUNTIME_CONFIG(Enum):
  STUDENT_CODE_TIMEOUT        = 3
  STUDENT_CODE_HZ             = 20 # Number of times to execute studentCode.main per second
  DEBUG_DELIMITER_STRING      = "****************** RUNTIME DEBUG ******************"
  PIPE_READY                  = ["ready"]
  TEST_OUTPUT_DIR             = "test_outputs/"

class BadThing:
  def __init__(self, exc_info, data, event=BAD_EVENTS.BAD_EVENT, printStackTrace=True):
    self.name = multiprocessing.current_process().name
    self.data = data
    self.event = event
    self.errorType, self.errorValue, tb = exc_info
    self.stackTrace = self.genStackTrace(tb)
    self.printStackTrace = printStackTrace

  def genStackTrace(self, tb):
    badThingDump = \
      ("Fatal Error in thread: %s\n"
      "Bad Event: %s\n"
      "Error Type: %s\n"
      "Error Value: %s\n"
      "Traceback: \n%s") % \
      (self.name, self.event, self.errorType, self.errorValue, "".join(traceback.format_tb(tb)))
    return badThingDump

  def __str__(self):
    if self.printStackTrace:
      return self.stackTrace
    else:
      return str(self.data)

class StudentAPIError(Exception):
  pass

class StudentAPIKeyError(StudentAPIError):
  pass

class TimeoutError(Exception):
  pass
