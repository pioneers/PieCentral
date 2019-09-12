"""An intercomponent communication protocol."""

# pylint: disable=invalid-name,bad-whitespace
from enum import Enum, IntEnum, auto, unique
import traceback
import multiprocessing
import os
import json

__version__ = (1, 4, 0)


class AutoIntEnum(IntEnum):
    """
    An enum with automatically incrementing integer values, starting from zero.

    References:
      * https://docs.python.org/3/library/enum.html#using-automatic-values
    """
    # pylint: disable=no-self-argument
    def _generate_next_value_(name, start, count, last_values):
        return count


class RUNTIME_CONFIG(Enum):
    """Assorted runtime constants."""
    STUDENT_CODE_TIMELIMIT      = 1
    STUDENT_CODE_HZ             = 20 # Number of times to execute studentCode.main per second
    DEBUG_DELIMITER_STRING      = "\n****************** RUNTIME MESSAGE ******************"
    PIPE_READY                  = ["ready"]
    TEST_OUTPUT_DIR             = "test_outputs/"
    VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH = __version__


@unique
class BAD_EVENTS(Enum):
    """Assorted message types for ``BadEvent``s."""
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
    HIBIKE_START_ERROR        = "Hibike Process failed to start"
    ENTER_TELEOP              = "Dawn says enter Teleop"
    ENTER_AUTO                = "Dawn says enter Auto"
    ENTER_IDLE                = "Dawn says enter Idle"
    NEW_IP                    = "Connected to new instance of Dawn"
    DAWN_DISCONNECTED         = "Disconnected to Dawn"
    HIBIKE_NONEXISTENT_DEVICE = "Tried to access a nonexistent device"
    HIBIKE_INSTRUCTION_ERROR  = "Hibike received malformed instruction"

restartEvents = [BAD_EVENTS.STUDENT_CODE_VALUE_ERROR, BAD_EVENTS.STUDENT_CODE_ERROR,
                 BAD_EVENTS.STUDENT_CODE_TIMEOUT, BAD_EVENTS.END_EVENT, BAD_EVENTS.EMERGENCY_STOP]
studentErrorEvents = [BAD_EVENTS.STUDENT_CODE_ERROR, BAD_EVENTS.STUDENT_CODE_TIMEOUT]


@unique
class PROCESS_NAMES(Enum):
    """Names of processes."""
    STUDENT_CODE        = "studentProcess"
    STATE_MANAGER       = "stateProcess"
    RUNTIME             = "runtime"
    UDP_SEND_PROCESS    = "udpSendProcess"
    UDP_RECEIVE_PROCESS = "udpReceiveProcess"
    HIBIKE              = "hibike"
    TCP_PROCESS         = "tcpProcess"


@unique
class HIBIKE_COMMANDS(Enum):
    """Hibike command types."""
    ENUMERATE = "enumerate_all"
    SUBSCRIBE = "subscribe_device"
    WRITE     = "write_params"
    READ      = "read_params"
    DISABLE   = "disable_all"
    TIMESTAMP_DOWN = "timestamp_down"


@unique
class HIBIKE_RESPONSE(Enum):
    """Hibike response types."""
    DEVICE_SUBBED = "device_subscribed"
    DEVICE_VALUES = "device_values"
    DEVICE_DISCONNECT = "device_disconnected"
    TIMESTAMP_UP  = "timestamp_up"


@unique
class ANSIBLE_COMMANDS(Enum):
    """Ansible command types."""
    STUDENT_UPLOAD = "student_upload"
    CONSOLE        = "console"
    TIMESTAMP_UP   = "Get timestamps going up the stack"
    TIMESTAMP_DOWN = "Get timestamps going down the stack"


@unique
class SM_COMMANDS(AutoIntEnum):
    RESET               = auto()
    ADD                 = auto()
    STUDENT_MAIN_OK     = auto()
    GET_VAL             = auto()
    SET_VAL             = auto()
    SEND_ANSIBLE        = auto()
    RECV_ANSIBLE        = auto()
    CREATE_KEY          = auto()
    GET_TIME            = auto()
    EMERGENCY_STOP      = auto()
    EMERGENCY_RESTART   = auto()
    SET_ADDR            = auto()
    SEND_ADDR           = auto()
    STUDENT_UPLOAD      = auto()
    SEND_CONSOLE        = auto()
    ENTER_IDLE          = auto()
    ENTER_TELEOP        = auto()
    ENTER_AUTO          = auto()
    END_STUDENT_CODE    = auto()
    SET_TEAM            = auto()


class BadThing:
    """Message to runtime from one of its components."""
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
        """Get a formatted string for a traceback."""
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
        """Create a human readable error message for students from a traceback."""
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
        return str(self.data)


class StudentAPIError(Exception):
    """Miscellaneous student API error."""
    pass


class StudentAPIKeyError(StudentAPIError):
    """Student accessed something that doesn't exist."""
    pass


class StudentAPIValueError(StudentAPIError):
    """Student stored the wrong value."""
    pass


class StudentAPITypeError(StudentAPIError):
    """Student stored the wrong type."""
    pass


# Sensor type names are CamelCase, with the first letter capitalized as well
# TODO: could we read this ahead of time and not keep the file open?
CONFIG_FILE = open(os.path.join(os.path.dirname(__file__), '../hibike/hibikeDevices.json'), 'r')
SENSOR_TYPE = {device_data["id"]: device_data["name"] for device_data in json.load(CONFIG_FILE)}
SENSOR_TYPE[-1] = "runtime_version"
