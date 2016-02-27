# ------
# Robot.py class
# This runs the robot.
# Copyright 2015. Pioneers in Engineering.
# ------
'''
This module contains functions for reading data from the robot, and for
manipulating the robot.

To use this module, you must first import it:

>>> from api import Robot
'''
import memcache
memcache_port = 12357
mc = memcache.Client(['127.0.0.1:%d' % memcache_port]) # connect to memcache

motor = {}

_naming_map_filename = 'student_code/CustomID.txt'
_name_to_id = {}
try:
    with open(_naming_map_filename, "r") as f:
        for line in f.readlines():
            line = line.strip()
            device_id, name = line.split(" ", 1)
            _name_to_id[name] = device_id
except:
    print("Could not read naming map")

def _lookup(name):
    if name in _name_to_id:
        return _name_to_id[name]
    return name

def get_motor(name):
    """Returns the current power value for a motor.

    :param name: A string that identifies the motor
    :returns: A value between -1 and 1, which is the power level of that motor.

    :Examples:

    >>> motor = Robot.get_motor(motor1)

    """
    name = _lookup(name)
    name_to_value = mc.get('motor_values')
    assert type(name) is str, "Type Mismatch: Must pass in a string"
    try:
        return name_to_value[name]/100
    except KeyError:
        raise KeyError("Motor name not found.")

def set_motor(name, value):
    """Sets a motor to the specified power value.

    :param name: A string that identifies the motor.
    :param value: A decimal value between -1 and 1, the power level you want to set.

    :Examples:

    >>> Robot.set_motor("motor1", .50)

    """
    assert type(name) is str, "Type Mismatch: Must pass in a string to name."
    assert type(value) is int or type(value) is float, "Type Mismatch: Must pass in an integer or float to value."
    assert value <= 1 and value >= -1, "Motor value must be a decimal between -1 and 1 inclusive."
    name = _lookup(name)
    name_to_value = mc.get('motor_values')
    if name not in name_to_value:
        raise KeyError("No motor with that name")
    name_to_value[name] = value*100
    mc.set('motor_values', name_to_value)

def get_sensor(name):
    """Returns the value, or reading corresponding to the specified sensor.

    :param name: A string that identifies the sensor.
    :returns: The reading of the sensor at the current point in time.
    """
    device_id = _lookup(name)
    all_data = mc.get('sensor_values')
    try:
        return all_data[device_id]
    except KeyError:
        raise KeyError("No Sensor with that name")

def get_all_motors():
    """Returns the current power values for every connected motor.
    """
    return mc.get('motor_values')

def set_led(num, value):
    """Sets a specific LED on the team flag

    :param num: The number of the LED (0, 1, 2, or 3)
    :param value: A boolean value

    :Examples:

    >>> Robot.set_LED(0, False)
    >>> Robot.set_LED(1,True)
    """
    flag_data = mc.get('flag_values')
    flag_data[num] = value
    mc.set('flag_values', flag_data)

def get_distance_sensor(name):
    """Returns the distance away from the sensor an object is, measured in centimeters

    :param name: A String that identifies the distance sensor
    :returns: A double representing how many centimeters away the object is from the sensor

    :Examples:

    >>> distance = Robot.get_distance_sensor("distance1")

    """
    device_id = _lookup(name)
    return _testConnected(device_id)


def get_limit_switch(name):
    """Returns whether a specified limit switch on the identified device is pressed or not

    The specified limit switch returns a boolean, either True (pressed) or False (not pressed).

    :param name: A String that identifies the limit switch
    :returns: A boolean value, where True is pressed and False is not pressed.

    :Examples:

    >>> switch = Robot.get_limit_switch("switch1",3)
    >>> switch
    True

    """
    device_id = _lookup(name)
    return _testConnected(device_id)

def get_potentiometer(name):
    """Returns the sensor reading of a potentiometer

    The potentiometer returns a decimal between 0 and 1, indicating the angle detected,
    where 0 and 1 are the two extreme angles.

    :param name: A string that identifies the potentiometer smart device (contains four potentiometers)
    :returns: A decimal between 0 and 1 representing the angle.

    """
    device_id = _lookup(name)
    return _testConnected(device_id)

def _testConnected(device_id): #checks if data exists in sensor values, throws error if doesn't
    all_data = mc.get('sensor_values')
    try:
        return all_data[device_id]
    except KeyError:
        raise KeyError("No sensor with that name")

class SensorValueOutOfBounds(Exception):
    pass

# pololu.com. 19:1 and 67:1 motors 37D motors geared. Be able to change PID constants. Move and stay - set point. once it is called again, reset and redo function.
