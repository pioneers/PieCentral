import os
import json

config_file = open(os.path.join(os.path.dirname(__file__), 'hibikeDevices.json'), 'r')
devices = json.load(config_file)
paramMap = {device["id"]: {param["name"]: (param["number"], param["type"]) for param in device["params"]} for device in devices}

def uid_to_device_id(uid):
  return uid >> 72
