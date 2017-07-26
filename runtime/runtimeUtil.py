# pylint: disable=invalid-name,bad-whitespace
import traceback
import multiprocessing
import os
import json
from enum import Enum, unique


class RUNTIME_CONFIG(Enum):
    STUDENT_CODE_TIMELIMIT      = 1
    STUDENT_CODE_HZ             = 20 # Number of times to execute studentCode.main per second
    DEBUG_DELIMITER_STRING      = "****************** RUNTIME DEBUG ******************"
    PIPE_READY                  = ["ready"]
    TEST_OUTPUT_DIR             = "test_outputs/"
    VERSION_MAJOR               = 1
    VERSION_MINOR               = 1
    VERSION_PATCH               = 0

@unique
class BAD_EVENTS(Enum):
    BAD_EVENT                 = "BAD THINGS HAPPENED"
    STUDENT_CODE_ERROR        = "Student Code Crashed"
    STUDENT_CODE_VALUE_ERROR  = "Student Code Value Error"
    STUDENT_CODE_TIMEOUT      = "Student Code Timed Out"
    UNKNOWN_PROCESS           = "Unknown State Manager process name"
    STATE_MANAGER_KEY_ERROR   = "Error accessing key in State Manager"
    STATE_MANAGER_CRASH       = "State Manager has Crashed"
    EMERGENCY_STOP            = "Robot Emergency Stopped"
    END_EVENT                 = "Process terminated"
    UDP_SEND_ERROR            = "UDPSend Process Crashed"
    UDP_RECV_ERROR            = "UDPRecv Process Crashed"
    TCP_ERROR                 = "TCP Process Crashed"
    ENTER_TELEOP              = "Dawn says enter Teleop"
    ENTER_AUTO                = "Dawn says enter Auto"
    ENTER_IDLE                = "Dawn says enter Idle"
    NEW_IP                    = "Connected to new instance of Dawn"
    DAWN_DISCONNECTED         = "Disconnected to Dawn"

restartEvents = [BAD_EVENTS.STUDENT_CODE_VALUE_ERROR, BAD_EVENTS.STUDENT_CODE_ERROR,
                 BAD_EVENTS.STUDENT_CODE_TIMEOUT, BAD_EVENTS.END_EVENT, BAD_EVENTS.EMERGENCY_STOP]
studentErrorEvents = [BAD_EVENTS.STUDENT_CODE_ERROR, BAD_EVENTS.STUDENT_CODE_TIMEOUT]

@unique
class PROCESS_NAMES(Enum):
    STUDENT_CODE        = "studentProcess"
    STATE_MANAGER       = "stateProcess"
    RUNTIME             = "runtime"
    UDP_SEND_PROCESS    = "udpSendProcess"
    UDP_RECEIVE_PROCESS = "udpReceiveProcess"
    HIBIKE              = "hibike"
    TCP_PROCESS         = "tcpProcess"

@unique
class HIBIKE_COMMANDS(Enum):
    ENUMERATE = "enumerate_all"
    SUBSCRIBE = "subscribe_device"
    WRITE     = "write_params"
    READ      = "read_params"
    DISABLE   = "disable_all"

# TODO: Remove when Hibike is finished
@unique
class HIBIKE_RESPONSE(Enum):
    DEVICE_SUBBED = "device_subscribed"
    DEVICE_VALUES = "device_values"
    DEVICE_DISCONNECT = "device_disconnected"

@unique
class ANSIBLE_COMMANDS(Enum):
    STUDENT_UPLOAD = "student_upload"
    CONSOLE        = "console"

@unique
class SM_COMMANDS(Enum):
    # Used to autoenumerate
    # Don't ask I don't know how
    # https://docs.python.org/3/library/enum.html#autonumber
    def __new__(cls):
        value = len(cls.__members__) + 1 # pylint: disable=no-member
        obj = object.__new__(cls)
        obj._value_ = value # pylint: disable=protected-access
        return obj

    RESET               = ()
    ADD                 = ()
    STUDENT_MAIN_OK     = ()
    GET_VAL             = ()
    SET_VAL             = ()
    SEND_ANSIBLE        = ()
    RECV_ANSIBLE        = ()
    CREATE_KEY          = ()
    GET_TIME            = ()
    EMERGENCY_STOP      = ()
    EMERGENCY_RESTART   = ()
    SET_ADDR            = ()
    SEND_ADDR           = ()
    STUDENT_UPLOAD      = ()
    SEND_CONSOLE        = ()
    ENTER_IDLE          = ()
    ENTER_TELEOP        = ()
    ENTER_AUTO          = ()
    END_STUDENT_CODE    = ()
    SET_TEAM            = ()

class BadThing:
    def __init__(self, exc_info, data, event=BAD_EVENTS.BAD_EVENT, printStackTrace=True):
        self.name = multiprocessing.current_process().name #pylint: disable=not-callable
        self.data = data
        self.event = event
        self.errorType, self.errorValue, tb = exc_info
        self.stackTrace = self.genStackTrace(tb)
        self.printStackTrace = printStackTrace
        if event in restartEvents:
            self.studentError = self.genStudentError(tb)

    def genStackTrace(self, tb):
        badThingDump = \
            ("Fatal Error in thread: %s\n"
             "Bad Event: %s\n"
             "Error Type: %s\n"
             "Error Value: %s\n"
             "Traceback: \n%s") % \
            (self.name, self.event, self.errorType,
             self.errorValue, "".join(traceback.format_tb(tb)))
        return badThingDump

    def genStudentError(self, tb):
        errorList = []
        for error in traceback.format_tb(tb):
            if "studentCode.py" in error:
                index = error.find("line")
                error = error[index:]
                errorList.append(error)
        studentErrorMessage = "Traceback: \n"
        studentErrorMessage += "".join(errorList)
        if self.errorType is not None and self.errorValue is not None:
            studentErrorMessage += str(self.errorType.__name__) + ": " + str(self.errorValue)
        return studentErrorMessage

    def getStudentError(self):
        return self.studentError

    def __str__(self):
        if self.printStackTrace:
            return self.stackTrace
        else:
            return str(self.data)

class StudentAPIError(Exception):
    pass

class StudentAPIKeyError(StudentAPIError):
    pass

class StudentAPIValueError(StudentAPIError):
    pass

class StudentAPITypeError(StudentAPIError):
    pass

# Sensor type names are CamelCase, with the first letter capitalized as well
CONFIG_FILE = open(os.path.join(os.path.dirname(__file__), '../hibike/hibikeDevices.json'), 'r')
SENSOR_TYPE = {device_data["id"]: device_data["name"] for device_data in json.load(CONFIG_FILE)}
SENSOR_TYPE[-1] = "runtime_version"
