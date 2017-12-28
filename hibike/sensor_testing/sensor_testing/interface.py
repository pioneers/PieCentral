"""
Web interface to Hibike's testing module.
"""
import json
from flask import abort, request, render_template
from sensor_testing import APP

def add_paths():
    """
    Modify sys.path so that we can import modules
    from our parent.
    """
    import os
    import sys
    path = os.path.dirname(os.path.abspath(__file__))
    parent_path = os.path.split(os.path.split(path)[0])[0]
    print(parent_path)
    sys.path.insert(1, parent_path)
add_paths()

import hibike_tester
import hibike_message


HIBIKE_INSTANCE = hibike_tester.Hibike()

# FIXME: verification logic should be implemented elsewhere
def validate_range(param_type, value):
    """
    Check that a value is within the allowed range for its type.
    """
    try:
        if param_type == "float":
            return True
        elif param_type == "bool":
            return 0 <= value <= 1
        elif param_type == "double":
            return True
        elif param_type == "uint8_t":
            return 0 <= value <= 255
        elif param_type == "int8_t":
            return -128 <= value <= 127
        elif param_type == "uint16_t":
            return 0 <= value <= 6553
        elif param_type == "int16_t":
            return -32768 <= value <= 32767
        elif param_type == "uint32_t":
            return 0 <= value <= 2 ** 32 - 1
        elif param_type == "int32_t":
            return -(2 ** 31) <= value <= 2 ** 31 - 1
        elif param_type == "uint64_t":
            return 0 <= value <= 2 ** 64 - 1
        elif param_type == "int64_t":
            return -(2 ** 63) <= value <= 2 ** 63 - 1
    except (TypeError, ValueError):
        return False


def validate_value(uid, param, unvalidated_value):
    """
    Check that UNVALIDATED_VALUE is a valid input for PARAM.
    """
    dev_id = hibike_message.uid_to_device_id(uid)
    param_type = hibike_message.param_type(dev_id, param)
    return validate_range(param_type, unvalidated_value)


@APP.route("/")
def main_interface():
    """
    Render the main interface page.
    """
    from collections import namedtuple
    devices = []
    for u in HIBIKE_INSTANCE.uids:
        dev_id = hibike_message.uid_to_device_id(u)
        dev_name = hibike_message.uid_to_device_name(u)
        all_params = hibike_message.all_params_for_device_id(dev_id)
        params_list = []
        for p in all_params:
            param = namedtuple("Parameter", ("name", "type", "writeable"))
            param.name = p
            param.type = hibike_message.param_type(dev_id, p)
            param.writeable = hibike_message.writable(dev_id, p)
            params_list.append(param)
        device = namedtuple("Device", ("uid", "params", "name"))
        device.uid = u
        device.params = params_list
        device.name = dev_name
        devices.append(device)
    return render_template("index.html", devices=devices)


@APP.route("/devices", methods=["GET"])
def list_devices():
    """
    Get a list of UIDs and their associated device types
    in JSON form.
    """
    uids_list = HIBIKE_INSTANCE.get_uids_and_types()
    uids_and_types = {}
    for (uid, dev_type) in uids_list:
        uids_and_types[str(uid)] = dev_type
    return json.dumps({"devices": uids_and_types})


@APP.route("/devices", methods=["DELETE"])
def disable_all_devices():
    """
    Send a disable all message to Hibike.
    """
    HIBIKE_INSTANCE.disable()
    return "devices disabled"


@APP.route("/devices/info/")
def show_all_devices():
    """
    Get information about all devices.
    """
    returned_json = "{"
    for uid in HIBIKE_INSTANCE.uids:
        device_info = show_device(uid)
        returned_json += '"{}":{}'.format(uid, device_info)
    returned_json += "}"
    return returned_json

@APP.route("/devices/info/<int:uid>")
def show_device(uid):
    """
    Given a UID, get information about the device.
    """
    if uid not in HIBIKE_INSTANCE.uids:
        abort(404)
    device_id = hibike_message.uid_to_device_id(uid)
    device_name = hibike_message.device_id_to_name(device_id)
    params = hibike_message.all_params_for_device_id(device_id)
    json_map = {"device_name": device_name, "params": []}
    for param in params:
        readable = hibike_message.readable(device_id, param)
        writeable = hibike_message.writable(device_id, param)
        param_type = hibike_message.param_type(device_id, param)
        json_map["params"].append({"name": param,
                                   "readable": readable,
                                   "writeable": writeable,
                                   "type": param_type})
    return json.dumps(json_map)


@APP.route("/devices/<int:uid>", methods=["GET"])
def read_all_params(uid):
    """
    Read all parameters from a device.
    """
    if uid not in HIBIKE_INSTANCE.uids:
        abort(404)
    params = hibike_message.all_params_for_device_id(hibike_message.uid_to_device_id(uid))
    param_values = {}
    for param in params:
        param_values[param] = HIBIKE_INSTANCE.get_last_cached(uid, param)
    return json.dumps(param_values)


@APP.route("/devices/<int:uid>/<param>", methods=["GET"])
def read_param(uid, param):
    """
    Read a single device parameter.
    """
    if uid not in HIBIKE_INSTANCE.uids:
        abort(404)
    params = hibike_message.all_params_for_device_id(hibike_message.uid_to_device_id(uid))
    if param not in params:
        abort(404)
    return json.dumps({param: HIBIKE_INSTANCE.get_last_cached(uid, param)})


@APP.route("/devices/<int:uid>", methods=["POST"])
def write_params(uid):
    """
    Write values to a device.
    """
    if uid not in HIBIKE_INSTANCE.uids:
        abort(404)
    all_params = set(hibike_message.all_params_for_device_id(hibike_message.uid_to_device_id(uid)))
    params = request.get_json(force=True, cache=False)
    if params is None:
        abort(400)
    params_and_values = []
    for (param, value) in params.items():
        if param not in all_params:
            abort(400)
        if validate_value(uid, param, value):
            params_and_values.append((param, value))
        else:
            abort(400)
    HIBIKE_INSTANCE.write(uid, params_and_values)
    return "wrote value"
