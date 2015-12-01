# ------
# Robot.py class 
# This runs the robot.
# Copyright 2015. Pioneers in Engineering.
# ------
import memcache

memcache_port = 12357
mc = memcache.Client(['127.0.0.1:%d' % memcache_port]) # connect to memcache

motor = {}

def get_motor(name):
    name_to_value = mc.get('motor_values')
    if name in name_to_value:
        return name_to_value[name]
    return 'Error, motor with that name not found'

def set_motor(name, value):
    name_to_value = mc.get('motor_values')
    if name in name_to_value:
        name_to_value[name] = value
        mc.set('motor_values', name_to_value)
    else:
        print("No motor with that name")

# TODO: implement
def get_sensor(name):
    all_data = mc.get('sensor_values')
    if name in all_data:
        return all_data[name]
    return 'Error, sensor with that name not found'

def get_all_motors():
    return mc.get('motor_values')
