# pylint: disable=invalid-name
# pylint: enable=invalid-name
import sys
import time
import runtime_pb2

from runtimeUtil import *


class StateManager(object): # pylint: disable=too-many-public-methods

    """input is a multiprocessing.Queue object to support multiple
    processes requesting state data
    """

    def __init__(self, badThingsQueue, inputQueue, runtimePipe):
        self.init_robot_state()
        self.bad_things_queue = badThingsQueue
        self.input_ = inputQueue
        self.command_mapping = self.make_command_map()
        self.hibike_mapping = self.make_hibike_map()
        self.hibike_response_mapping = self.make_hibike_response_map()
        self.device_name_to_subscribe_params = self.make_subscription_map()
        self.process_mapping = {PROCESS_NAMES.RUNTIME: runtimePipe}

    @staticmethod
    def make_subscription_map():
        subscription_map = {
            "LimitSwitch": ["switch0", "switch1", "switch2"],
            "LineFollower": ["left", "center", "right"],
            "Potentiometer": ["pot0", "pot1", "pot2"],
            "BatteryBuzzer": ["v_batt", "is_unsafe"],
            "ServoControl": ["servo0", "servo1"],
            "YogiBear": ["duty_cycle", "enc_pos", "enc_vel"],
            "RFID": ["id", "tag_detect"],
            "ExampleDevice": ["hazuki", "sapphire", "reina", "asuka"]
        }
        return subscription_map

    def make_command_map(self):
        command_mapping = {
            SM_COMMANDS.RESET: self.init_robot_state,
            SM_COMMANDS.ADD: self.add_pipe,
            SM_COMMANDS.GET_VAL: self.get_value,
            SM_COMMANDS.SET_VAL: self.set_value,
            SM_COMMANDS.STUDENT_MAIN_OK: self.student_code_tick,
            SM_COMMANDS.CREATE_KEY: self.create_key,
            SM_COMMANDS.SEND_ANSIBLE: self.send_ansible,
            SM_COMMANDS.RECV_ANSIBLE: self.recv_ansible,
            SM_COMMANDS.GET_TIME: self.get_timestamp,
            SM_COMMANDS.EMERGENCY_STOP: self.emergency_stop,
            SM_COMMANDS.EMERGENCY_RESTART: self.emergency_restart,
            SM_COMMANDS.STUDENT_UPLOAD: self.student_upload,
            SM_COMMANDS.SEND_CONSOLE: self.send_console,
            SM_COMMANDS.SET_ADDR: self.set_addr,
            SM_COMMANDS.SEND_ADDR: self.send_addr,
            SM_COMMANDS.ENTER_IDLE: self.enter_idle,
            SM_COMMANDS.ENTER_TELEOP: self.enter_teleop,
            SM_COMMANDS.ENTER_AUTO: self.enter_auto,
            SM_COMMANDS.END_STUDENT_CODE: self.end_student_code,
            SM_COMMANDS.SET_TEAM: self.set_team,
        }
        return command_mapping

    def make_hibike_map(self):
        hibike_mapping = {
            HIBIKE_COMMANDS.ENUMERATE: self.hibike_enumerate_all,
            HIBIKE_COMMANDS.SUBSCRIBE: self.hibike_subscribe_device,
            HIBIKE_COMMANDS.READ: self.hibike_read_params,
            HIBIKE_COMMANDS.WRITE: self.hibike_write_params,
            HIBIKE_COMMANDS.DISABLE: self.hibike_disable,
        }
        return hibike_mapping

    def make_hibike_response_map(self):
        hibike_response_mapping = {
            HIBIKE_RESPONSE.DEVICE_SUBBED: self.hibike_response_device_subbed,
            HIBIKE_RESPONSE.DEVICE_VALUES: self.hibike_response_device_values,
            HIBIKE_RESPONSE.DEVICE_DISCONNECT: self.hibike_response_device_disconnect
        }
        return {k.value: v for k, v in hibike_response_mapping.items()}

    def init_robot_state(self):
        t = time.time()
        self.state = {
            "studentCodeState": [2, t],
            "limit_switch": [["limit_switch", 0, 123456], t],
            "incrementer": [2, t],
            "int1": [112314, t],
            "float1": [987.123, t],
            "bool1": [True, t],
            "dict1": [{"inner_dict1_int": [555, t], "inner_dict_1_string": ["hello", t]}, t],
            "list1": [[[70, t], ["five", t], [14.3, t]], t],
            "string1": ["abcde", t],
            "runtime_meta": [{"studentCode_main_count": [0, t], "e_stopped": [False, t]}, t],
            "hibike": [{"device_subscribed": [0, t],
                        "devices": [{-1: [{"major": [RUNTIME_CONFIG.VERSION_MAJOR.value, t],
                                           "minor": [RUNTIME_CONFIG.VERSION_MINOR.value, t],
                                           "patch": [RUNTIME_CONFIG.VERSION_PATCH.value, t]},
                                          t]}, t]}, t],
            "dawn_addr": [None, t],
            "gamepads": [{0: {"axes": {0: 0.5, 1: -0.5, 2: 1, 3: -1},
                              "buttons": {0: True, 1: False, 2: True, 3: False, 4: True}}}, t],
            "team_flag_uid": [None, t],
        }

    def add_pipe(self, process_name, pipe):
        self.process_mapping[process_name] = pipe
        pipe.send(RUNTIME_CONFIG.PIPE_READY.value)

    def create_key(self, keys, send=True):
        curr_dict = self.state
        path = []
        for key in keys:
            try:
                if key not in curr_dict:
                    curr_dict[key] = [{}, 0]
                path.append(curr_dict[key])
                curr_dict = curr_dict[key][0]
            except TypeError:
                error = StudentAPIKeyError(
                    "key '{}' is defined, but does not contain a dictionary.".format(key))
                self.process_mapping[PROCESS_NAMES.STUDENT_CODE].send(error)
                return
        curr_time = time.time()
        for item in path:
            item[1] = curr_time
        if send:
            self.process_mapping[PROCESS_NAMES.STUDENT_CODE].send(None)

    def get_value(self, keys):
        result = self.state
        try:
            for i, key in enumerate(keys):
                result = result[key][0]
            self.process_mapping[PROCESS_NAMES.STUDENT_CODE].send(result)
        except:
            error = StudentAPIKeyError(self.dict_error_message(i, keys, result))
            self.process_mapping[PROCESS_NAMES.STUDENT_CODE].send(error)

    def set_value(self, value, keys, send=True):
        curr_dict = self.state
        try:
            path = []
            for i, key in enumerate(keys[:-1]):
                path.append(curr_dict[key])
                curr_dict = curr_dict[key][0]
            if len(keys) > 1:
                i += 1 # pylint: disable=undefined-loop-variable
            else:
                i = 0
            if keys[i] not in curr_dict:
                raise Exception
            path.append(curr_dict[keys[i]])
            curr_dict[keys[i]][0] = value
            curr_time = time.time()
            for item in path:
                item[1] = curr_time
            if send:
                self.process_mapping[PROCESS_NAMES.STUDENT_CODE].send(value)
        except:
            error = StudentAPIKeyError(
                self.dict_error_message(i, keys, curr_dict))
            if send:
                self.process_mapping[PROCESS_NAMES.STUDENT_CODE].send(error)

    def send_ansible(self):
        self.process_mapping[PROCESS_NAMES.UDP_SEND_PROCESS].send(self.state)

    def recv_ansible(self, new_data):
        self.state.update(new_data)

    def set_team(self, team):
        if self.state["team_flag_uid"][0] is not None:
            self.hibike_write_params(self.process_mapping[PROCESS_NAMES.HIBIKE],
                                     self.state["team_flag_uid"][0], [(team, True)])
            self.state["team_flag_uid"] = [None, 0]

    def set_addr(self, new_addr):
        self.state["dawn_addr"] = [new_addr, time.time()]
        self.bad_things_queue.put(BadThing(sys.exc_info(), None, BAD_EVENTS.NEW_IP, False))

    def send_addr(self, process_name):
        self.process_mapping[process_name].send(self.state["dawn_addr"][0])

    def student_upload(self):
        self.bad_things_queue.put(
            BadThing(sys.exc_info(), None, BAD_EVENTS.ENTER_IDLE, False))
        self.process_mapping[PROCESS_NAMES.TCP_PROCESS].send(
            [ANSIBLE_COMMANDS.STUDENT_UPLOAD, True])

    def send_console(self, console_log):
        if PROCESS_NAMES.TCP_PROCESS in self.process_mapping:
            self.process_mapping[PROCESS_NAMES.TCP_PROCESS].send(
                [ANSIBLE_COMMANDS.CONSOLE, console_log])

    def enter_auto(self):
        self.bad_things_queue.put(
            BadThing(sys.exc_info(), None, BAD_EVENTS.ENTER_AUTO, False))
        self.state["studentCodeState"] = [
            runtime_pb2.RuntimeData.AUTO, time.time()]

    def enter_teleop(self):
        self.bad_things_queue.put(
            BadThing(sys.exc_info(), None, BAD_EVENTS.ENTER_TELEOP, False))
        self.state["studentCodeState"] = [
            runtime_pb2.RuntimeData.TELEOP, time.time()]

    def enter_idle(self):
        self.bad_things_queue.put(
            BadThing(sys.exc_info(), None, BAD_EVENTS.ENTER_IDLE, False))
        self.state["studentCodeState"] = [
            runtime_pb2.RuntimeData.STUDENT_STOPPED, time.time()]

    def get_timestamp(self, keys):
        curr_dict = self.state
        timestamp = 0
        try:
            for i, key in enumerate(keys):
                curr_dict, timestamp = curr_dict[key]
            self.process_mapping[PROCESS_NAMES.STUDENT_CODE].send(timestamp)
        except:
            error = StudentAPIKeyError(self.dict_error_message(i, keys, curr_dict))
            self.process_mapping[PROCESS_NAMES.STUDENT_CODE].send(error)

    def student_code_tick(self):
        self.state["runtime_meta"][0]["studentCode_main_count"][0] += 1

    def emergency_stop(self):
        self.state["runtime_meta"][0]["e_stopped"][0] = True
        self.bad_things_queue.put(BadThing(sys.exc_info(
        ), "Emergency Stop Activated", event=BAD_EVENTS.EMERGENCY_STOP, printStackTrace=False))
        self.state["studentCodeState"] = [
            runtime_pb2.RuntimeData.ESTOP, time.time()]

    def emergency_restart(self):
        self.state["runtime_meta"][0]["e_stopped"][0] = False

    def end_student_code(self):
        self.process_mapping[PROCESS_NAMES.UDP_RECEIVE_PROCESS].send(
            runtime_pb2.RuntimeData.STUDENT_STOPPED)

    def hibike_enumerate_all(self, pipe):
        pipe.send([HIBIKE_COMMANDS.ENUMERATE.value, []])

    def hibike_subscribe_device(self, pipe, uid, delay, params):
        pipe.send([HIBIKE_COMMANDS.SUBSCRIBE.value, [uid, delay, params]])

    def hibike_write_params(self, pipe, uid, param_values):
        pipe.send([HIBIKE_COMMANDS.WRITE.value, [uid, param_values]])

    def hibike_read_params(self, pipe, uid, params):
        pipe.send([HIBIKE_COMMANDS.READ.value, [uid, params]])

    def hibike_response_device_subbed(self, uid, delay, params):
        if delay == 0:
            device_name = SENSOR_TYPE[uid >> 72]
            if device_name == "TeamFlag":
                self.set_value(uid, ["team_flag_uid"], send=False)
            if device_name in self.device_name_to_subscribe_params:
                self.hibike_subscribe_device(
                    self.process_mapping[PROCESS_NAMES.HIBIKE], uid, 40,
                    self.device_name_to_subscribe_params[device_name])
        self.create_key(["hibike", "devices", uid], send=False)
        for param in params:
            self.create_key(["hibike", "devices", uid, param], send=False)
            self.set_value(None, ["hibike", "devices", uid, param], send=False)
        self.state["hibike"][0]["device_subscribed"][0] += 1

    def hibike_response_device_values(self, data):
        for uid, params in data.items():
            for key, value in params:
                self.set_value(value, ["hibike", "devices", uid, key], send=False)

    # pylint: disable=invalid-name
    def hibike_response_device_disconnect(self, uid):
        """
        Delete any history of the device at UID.
        """
        devs = self.state["hibike"][0]["devices"][0]
        del devs[uid]

    def hibike_disable(self, pipe):
        pipe.send([HIBIKE_COMMANDS.DISABLE.value, []])

    def dict_error_message(self, errored_index, keys, curr_dict):
        key_chain = ""
        i = 0
        while i < errored_index:
            # Assembles a string representation of the dictionary indexing that
            # occurred
            key_chain += "['" + keys[i] + \
                "']" if (isinstance(keys[i], str)) else "[" + str(keys[i]) + "]"
            i += 1
        keys = [None] if len(keys) == 0 else keys # pylint: disable=bad-option-value, len-as-condition
        errored_key = "'" + keys[errored_index] + "'" if isinstance(
            keys[errored_index], str) else str(keys[errored_index])
        error_message = "KeyError: key " + errored_key + \
            " not found in state" + key_chain + "\n"

        if isinstance(curr_dict, dict):
            # Converts all available keys to strings, and adds commas and
            # spaces at the end of each element
            available_keys = [("'" + el + "', " if isinstance(el, str) else str(el) + ", ")
                              for el in curr_dict.keys()]
            if len(available_keys) > 0: # pylint: disable=bad-option-value, len-as-condition
                # Removes comma and space from last item in available_keys
                available_keys[-1] = available_keys[-1][:-2]
            error_message += "Available keys in state" + \
                key_chain + ": " + "".join(available_keys)
        else:
            error_message += "state" + key_chain + \
                " is of type " + type(curr_dict).__name__

        return error_message

    def start(self):
        while True:
            try:
                request = self.input_.get(block=True)
                cmd_type = request[0]
                args = request[1]
                if len(request) != 2:
                    self.bad_things_queue.put(BadThing(sys.exc_info(),
                                                       "Wrong input size, need list of size 2",
                                                       event=BAD_EVENTS.UNKNOWN_PROCESS,
                                                       printStackTrace=False))
                elif cmd_type in self.command_mapping:
                    command = self.command_mapping[cmd_type]
                    command(*args)
                elif cmd_type in self.hibike_mapping:
                    if not self.state["runtime_meta"][0]["e_stopped"][0]:
                        command = self.hibike_mapping[cmd_type]
                        command(self.process_mapping[PROCESS_NAMES.HIBIKE], *args)
                elif cmd_type in self.hibike_response_mapping:
                    command = self.hibike_response_mapping[cmd_type]
                    command(*args)
                else:
                    self.bad_things_queue.put(BadThing(sys.exc_info(),
                                                       "Unknown process name: %s" % (request,),
                                                       event=BAD_EVENTS.UNKNOWN_PROCESS,
                                                       printStackTrace=False))
            except Exception as e:
                self.bad_things_queue.put(BadThing(sys.exc_info(),
                                                   "State Manager Loop crash with: " + str(e),
                                                   event=BAD_EVENTS.STATE_MANAGER_CRASH,
                                                   printStackTrace=True))
