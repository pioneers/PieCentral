"""Software interface for robot actions."""

import asyncio
import csv
import inspect
import io
import time

from runtimeUtil import *


class Actions:
    @staticmethod
    async def sleep(seconds):
        await asyncio.sleep(seconds)


class StudentAPI:
    """Hidden interface with State Manager."""
    def __init__(self, toManager, fromManager):
        self.from_manager = fromManager
        self.to_manager = toManager

    def _get_sm_value(self, key, *args):
        """Returns the value associated with key.
        """
        self.to_manager.put([SM_COMMANDS.GET_VAL, [[key] + list(args)]])
        message = self.from_manager.recv()
        if isinstance(message, Exception):
            raise message
        return message

    def _set_sm_value(self, value, key, *args):
        """Sets the value associated with key.
        """
        # statemanager passes exception, then check to see if returned value is
        # exception or not
        self.to_manager.put([SM_COMMANDS.SET_VAL, [value, [key] + list(args)]])
        message = self.from_manager.recv()
        if isinstance(message, Exception):
            raise message
        return message


class Field(StudentAPI):
    @property
    def starting_zone(self):
        return self._get_sm_value('starting_zone')

    @property
    def master(self):
        return self._get_sm_value('master')

    @property
    def time(self):
        return time.time()


class Gamepad(StudentAPI):
    """Software interface for accessing a gamepad."""
    buttons = {
        "button_a": 0,
        "button_b": 1,
        "button_x": 2,
        "button_y": 3,
        "l_bumper": 4,
        "r_bumper": 5,
        "l_trigger": 6,
        "r_trigger": 7,
        "button_back": 8,
        "button_start": 9,
        "l_stick": 10,
        "r_stick": 11,
        "dpad_up": 12,
        "dpad_down": 13,
        "dpad_left": 14,
        "dpad_right": 15,
        "button_xbox": 16
    }
    joysticks = {
        "joystick_left_x": 0,
        "joystick_left_y": 1,
        "joystick_right_x": 2,
        "joystick_right_y": 3
    }

    def __init__(self, toManager, fromManager):
        super().__init__(toManager, fromManager)
        self._get_gamepad()

    def _get_gamepad(self):
        """Fetch gamepads from StateManager."""
        self.all_gamepads = self._get_sm_value("gamepads")

    def get_value(self, name, gamepad_number=0):
        """Get a value from a gamepad."""
        gamepad_dict = self.all_gamepads[gamepad_number]
        if name in self.joysticks:
            return gamepad_dict["axes"][self.joysticks[name]]
        elif name in self.buttons:
            return gamepad_dict["buttons"][self.buttons[name]]
        raise StudentAPIKeyError(str(name) + " is not a valid gamepad parameter")


class Robot(StudentAPI):
    """Main software interface for the robot."""
    deviceName_to_writeParams = {
        "ServoControl": ["servo0", "servo1"],
        "YogiBear": ["duty_cycle", "pid_pos_setpoint", "pid_pos_kp", "pid_pos_ki",
                     "pid_pos_kd", "current_thresh", "enc_pos"],
        "PolarBear": ["duty_cycle", "pid_pos_setpoint", "pid_pos_kp", "pid_pos_ki",
                      "pid_pos_kd", "current_thresh", "enc_pos"],
    }
    deviceName_to_readParams = {
        "LimitSwitch": ["switch0", "switch1", "switch2"],
        "LineFollower": ["left", "center", "right"],
        "Potentiometer": ["pot0", "pot1", "pot2"],
        "ServoControl": ["servo0", "servo1"],
        "YogiBear": ["duty_cycle", "enc_pos", "enc_vel"],
        "PolarBear": ["duty_cycle", "enc_pos", "enc_vel"],
        "RFID": ["id", "tag_detect"],
    }
    param_to_valid_values = {
        "servo0": [(float, int), -1, 1],
        "servo1": [(float, int), -1, 1],
        "duty_cycle": [(float, int), -1, 1],
        "pid_pos_setpoint": [(float, int), -float("inf"), float("inf")],
        "pid_pos_kp": [(float, int), 0, float("inf")],
        "pid_pos_ki": [(float, int), 0, float("inf")],
        "pid_pos_kd": [(float, int), 0, float("inf")],
        "current_thresh": [(float, int), 2, 10],
        "enc_pos": [(float, int), 0, 0],
        "led1": [(bool,)],
        "led2": [(bool,)],
        "led3": [(bool,)],
        "led4": [(bool,)],
    }

    def __init__(self, to_manager, from_manager):
        super().__init__(to_manager, from_manager)
        self._create_sensor_mapping()
        self._coroutines_running = set()
        self._stdout_buffer = io.StringIO()
        self._get_all_sensors()

        self.nonexistent_sensors = []
        self.student_code_writes = {}

    def _get_all_sensors(self):
        """Get a list of sensors."""
        self.peripherals = self._get_sm_value('hibike', 'devices')

    def get_value(self, device_name, param):
        """Get a single value from a device."""
        uid = self._hibike_get_uid(device_name)
        self._check_read_params(uid, param)
        return self.peripherals[uid][0][param][0]

    def set_value(self, device_name, param, value):
        """Set a parameter value for device."""
        uid = self._hibike_get_uid(device_name)
        if uid is None:
            return
        self._check_write_params(uid, param)
        self._check_value(param, value)
        self.hibike_write_value(uid, [(param, value)])

    def set_motor(self, device_name, value):
        uid = self._hibike_get_uid(device_name)
        if uid is None:
            return
        self._check_write_params(uid, "duty_cycle")
        self._check_value("duty_cycle", value)
        self.hibike_write_value(uid, [("duty_cycle", value)])

    def stop_motor(self, device_name):
        uid = self._hibike_get_uid(device_name)
        if uid is None:
            return
        self._check_write_params(uid, "duty_cycle")
        self._check_value("duty_cycle", 0)
        self.hibike_write_value(uid, [("duty_cycle", 0)])

    def run(self, func, *args, **kwargs):
        """
        Starts a "coroutine", i.e. a series of actions that proceed
        independently of the main loop of code.

        The first argument must be a function defined with 'async def'.

        The remaining arguments are then passed to that function before it is
        called.

        Multiple simultaneous coroutines that use the same robot actuators will
        lead to surprising behavior. To help guard against errors, calling
        `run` with a `func` argument that is currently running is a no-op.
        """
        if self.is_running(func):
            return

        self._coroutines_running.add(func)

        future = func(*args, **kwargs)

        async def wrapped_future():
            await future
            self._coroutines_running.remove(func)

        asyncio.ensure_future(wrapped_future())

    def is_running(self, func):
        """Check if func is being run by ``Robot.run()``."""
        if not inspect.isfunction(func):
            raise StudentAPIValueError(
                "First argument to Robot.run must be a function")
        elif not inspect.iscoroutinefunction(func):
            raise StudentAPIValueError(
                "First argument to Robot.run must be defined with `async def`, not `def`")

        return func in self._coroutines_running

    def _check_write_params(self, uid, param):
        """Checks that some parameters are valid for the device."""
        device_type = uid >> 72
        valid_params = self.deviceName_to_writeParams[SENSOR_TYPE[device_type]]
        if param not in valid_params:
            raise StudentAPITypeError(
                "Invalid param passed in, valid parameters for this device are: "
                + ", ".join(valid_params))

    def _check_read_params(self, uid, param):
        """Check that ``param`` is supported by ``uid``."""
        device_type = uid >> 72
        valid_params = self.deviceName_to_readParams[SENSOR_TYPE[device_type]]
        if param not in valid_params:
            raise StudentAPITypeError(
                "Invalid param passed in, valid parameters for this device are: "
                + ", ".join(valid_params))

    def _check_value(self, param, value):
        """Check that a value is valid for a parameter."""
        valid_values = self.param_to_valid_values[param]
        # TODO: use descriptive names for `valid_values[0]` and `valid_values[0][0]`
        if not isinstance(value, valid_values[0]):
            raise StudentAPIValueError(
                "Invalid value type passed in, valid types for this param are: "
                + valid_values[0][0].__name__)
        elif isinstance(valid_values[0][0], (float, int)):
            if not valid_values[1] <= value <= valid_values[2]:
                raise StudentAPIValueError(
                    "Invalid value passed in, valid values for this param are: "
                    + str(valid_values[1]) + " to " + str(valid_values[2]))
        # Probably `bool` here

    def _create_sensor_mapping(self, filename="namedPeripherals.csv"):
        with open(filename, "r") as f:
            sensor_mappings = csv.reader(f)
            self.sensor_mappings = {name: int(uid)
                                    for name, uid in sensor_mappings}

    def create_key(self, key, *args):
        """ Creates a new key, or nested keys if more than 1 key is passed in.
            If any nested key does not exist, it will be created.
        """
        self.to_manager.put([SM_COMMANDS.CREATE_KEY, [[key] + list(args)]])
        message = self.from_manager.recv()
        if isinstance(message, StudentAPIKeyError):
            raise message

    def get_timestamp(self, key, *args):
        """Returns the value associated with key.
        """
        self.to_manager.put([SM_COMMANDS.GET_TIME, [[key] + list(args)]])
        message = self.from_manager.recv()
        if isinstance(message, StudentAPIKeyError):
            raise message
        return message

    # pylint: disable=inconsistent-return-statements
    def _hibike_get_uid(self, name):
        # TODO: Implement sensor mappings, right now uid is the number (or string of number)
        try:
            device = int(name)
        except ValueError:
            self._print(f'Device UID must be an integer. Found: "{str(name)}".')
            return
        if device in self.peripherals:
            return device
        if device in self.nonexistent_sensors:
            return
        self.nonexistent_sensors += [device]
        self.to_manager.put([SM_COMMANDS.SEND_CONSOLE,
                             ['Warning: device not found: ' + str(name) + '\n']])

    def emergency_stop(self):
        """Stop the robot."""
        self.to_manager.put([SM_COMMANDS.EMERGENCY_STOP, []])

    def _print(self, *args, sep=' ', end='\n', file=None, flush=False):
        """Handle advanced usage of ``print``."""
        if file is not None:
            return print(*args, sep=sep, end=end, file=file, flush=flush)

        # Print to both stdout and the send-to-dawn buffer
        print(*args, sep=sep, end=end, file=self._stdout_buffer, flush=flush)
        return print(*args, sep=sep, end=end, flush=flush)

    def _send_prints(self):
        """Send console messages to dawn."""
        console_string = self._stdout_buffer.getvalue()
        if console_string:
            self._stdout_buffer = io.StringIO()
            self.to_manager.put([SM_COMMANDS.SEND_CONSOLE, [console_string]])

    def hibike_write_value(self, uid, params):
        """Writes parameters to ``uid``."""
        #create global variable dictionary student_code_writes
        if self.student_code_writes.get(uid) != params:
            self.student_code_writes[uid] = params
            self.to_manager.put([HIBIKE_COMMANDS.WRITE, [uid, params]])

    def _get_gamecodes(self):
        """Get a gamecode."""
        return self._get_sm_value("gamecodes")

    def _get_gamecodes_check(self):
        """Get gamecode answers"""
        return self._get_sm_value("gamecodes_check")
