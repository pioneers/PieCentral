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

# pylint: disable=wrong-import-position
import hibike_tester
import hibike_message


HIBIKE_INSTANCE = hibike_tester.Hibike()


@APP.route("/")
def main_interface():
    """
    Render the main interface page.
    """
    HIBIKE_INSTANCE.subscribe_all()
    from collections import namedtuple
    import time
    # Wait for Hibike to read from devices
    time.sleep(0.5)
    devices = []
    for uid in HIBIKE_INSTANCE.uids:
        dev_id = hibike_message.uid_to_device_id(uid)
        dev_name = hibike_message.uid_to_device_name(uid)
        all_params = hibike_message.all_params_for_device_id(dev_id)
        params_list = []
        for param_name in all_params:
            param = namedtuple("Parameter", ("name", "type", "readable", "writeable", "init_value"))
            param.name = param_name
            param.type = hibike_message.param_type(dev_id, param_name)
            param.writeable = hibike_message.writable(dev_id, param_name)
            param.readable = hibike_message.readable(dev_id, param_name)
            param.init_value = HIBIKE_INSTANCE.get_last_cached(uid, param_name)
            params_list.append(param)
        params_list.sort(key=lambda p: p.name)
        device = namedtuple("Device", ("uid", "params", "name"))
        device.uid = uid
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


class DeviceNotFoundError(Exception):
    """
    Exception raised if a device with a given UID is not
    connected.
    """
    pass


def get_device_info(uid):
    """
    Get a dictionary representing information about a device.
    """
    if uid not in HIBIKE_INSTANCE.uids:
        raise DeviceNotFoundError()
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
    return json_map


@APP.route("/devices/info/")
def show_all_devices():
    """
    Get information about all devices.
    """
    uids = set(HIBIKE_INSTANCE.uids)
    devices = {}
    for uid in uids:
        try:
            devices[str(uid)] = get_device_info(uid)
        except DeviceNotFoundError:
            continue

    return json.dumps(devices)


@APP.route("/devices/info/<int:uid>")
def show_device(uid):
    """
    Given a UID, get information about the device.
    """
    try:
        return json.dumps(get_device_info(uid))
    except DeviceNotFoundError:
        abort(404)


@APP.route("/devices/<int:uid>", methods=["GET"])
def read_all_params(uid):
    """
    Read all parameters from a device.
    """
    if uid not in HIBIKE_INSTANCE.uids:
        abort(404)
    dev_id = hibike_message.uid_to_device_id(uid)
    all_params = hibike_message.all_params_for_device_id(dev_id)
    readable_params = [p for p in all_params if hibike_message.readable(dev_id, p)]
    param_values = {}
    for param in readable_params:
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
        params_and_values.append((param, value))
    HIBIKE_INSTANCE.write(uid, params_and_values)
    return "wrote value"
