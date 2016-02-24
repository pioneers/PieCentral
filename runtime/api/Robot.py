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

from uid_did_conversions import *

motor = {}

def _lookup(name):
    return name

def get_motor(name):
    """Returns the current power value for a motor.

    :param name: A string that identifies the motor
    :returns: A value between -1 and 1, which is the power level of that motor.

    :Examples:

    >>> motor = Robot.get_motor(motor1)

    """
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
    name_to_value = mc.get('motor_values')
    try:
        name_to_value[name] = value*100
        mc.set('motor_values', name_to_value)
    except KeyError:
        raise KeyError("No motor with that name")


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

def set_LED(name,value):
    """Sets the brightness of a specific LED on the team flag.

    Each LED has four levels, represented by enums. Each light is set to an enum: Flag.OFF,
    Flag.LOW, Flag.MED, or Flag.HIGH.

    :param name: A string that identifies the LED on the team flag.
    :param value: An enum (OFF,LOW,MED,HIGH) which sets brightness for the specified LED

    :Examples:

    >>> Robot.set_LED("flag12",Flag.OFF)
    >>> Robot.set_LED("flag1",Flag.LOW)
    """
    device_id = _lookup(name)
    assert value in range(4),"Value must be an enum"
    flag_data = [device_id_to_uid(device_id)] + [-1,-1,-1,-1]
    flag_data[name[0]] = value
    mc.set('flag_values', flag_data)

def set_servo(name,value):  #TODO Check with hibike on exact functionality
    """Sets a degree for a specific servo to turn.

    One servo, as specified by its name, is set to turn to an integer amount of degrees (0-180)

    :param name: A string that identifies the servo
    :param value: An integer between 0 and 180 which sets the amount to turn to in degrees

    :Examples:

    >>> Robot.set_servo("servo1",90)
    >>> Robot.set_servo("servo3",150)

    """
    assert value in range(181), "Servo degrees must be between 0 and 180"
    device_id = _lookup(name)
    print(device_id)
    servo_data = [device_id_to_uid(device_id)] + [-1,-1,-1,-1]
    print(device_id_to_uid(device_id))
    # TODO: Sets all servos because we're too lazy to figure out which one it is
    print(servo_data[0])
    for i in range(1, 5):
        servo_data[i] = value
    mc.set('servo_values', servo_data)


def get_color_sensor(name):
    """Returns the value from the color sensor for a specific color.

    Each color sensor senses red, green, and blue, returning a
    number between 0 and 1, where 1 indicates a higher intensity. This function returns
    the result from one specific color sensor.

    :param name: A string that identifies the color sensor
    :param color: A integer that identifies which specific color sensor to return
                  where 0 specifies the red sensor, 1 specifies the green sensor,
                  and 2 specifies the blue sensor
    :returns: A double between 0 and 1, where 1 indicates a higher intensity

    :Examples:

    >>> color = Robot.get_color_sensor("color1",1)
    >>> color
    0.873748

    """
    device_id = _lookup(name)
    return _testConnected(device_id)

def get_luminosity(name):
    """Returns the luminosity for the specified color sensor.

    The color sensor returns the luminosity detected by the color sensor, represnted by
    a decimal between 0 and 1, where 1 indicates higher intensity.

    :param name: A string that identifies the color sensor
    :returns: A double between 0 and 1, where 1 indicates a higher intensity

    :Examples:

    >>> Robot.get_luminosity("color1")
    0.89783

    """
    device_id = _lookup(name)
    return _testConnected(device_id)

def get_hue(name):
    """Returns the hue detected at the specified color sensor.

    This uses the red, green, and blue sensors on the color sensor to return the
    detected hue, which is represented as a double between 0 and 360. See
    https://en.wikipedia.org/wiki/Hue for more information on hue.

    :param name: A string that identifies the color sensor
    :returns: A double between 0 and 360 representing the detected hue

    :Examples:

    >>> hue = Robot.get_hue("color1")
    >>> hue
    254.01

    """
    all_data = mc.get('sensor_values')
    device_id = _lookup(name)
    try:
        r = all_data[name][0]
        g = all_data[name][1]
        b = all_data[name][2]
        denom = max(r,g,b) - min(r,g,b)
        if r > g and r > b:
            return (g - b)/denom
        elif g > r and g > b:
            return 2.0 + (b - r)/denom
        else:
            return 4.0 + (r - g)/denom
    except KeyError:
        raise KeyError("No Sensor with that name")

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

"""def get_metal_detector(name): #TODO metal detector Implementation
    \"""Returns the sensor reading of the specified metal detector

    Each metal detector returns an integer, which changes based on the prescence of metal.

    :param name: A String that identifies the metal detector smart device.
    :returns: An integer (large) which represents whether metal is detected or not.

    \"""
    name = _lookup(name)
    return _testConnected(name)

def calibrate_metal_detector(name): #TODO ask hibike
    \"""Calibrates the specified metal sensor

    Calibrates to set the current reading of the metal detector to air (0)

    :param name: A String that identifies the metal detector smart device.
    \"""
    return null

def get_all_reflecting(name): #TODO hibike implement
    \"""Returns how much light is reflected onto the sensor_values

    A light/reflective material will return higher values, while a dark material
    will return a lower value. Each reflecting sensor returns a list, with each index
    corresponding to a specifie reflecting sensor.

    :param name: A String that identifies the reflecting smart device.
    :returns: A list of decimals which represents how much light is reflected.
    \"""
    return null
"""


def drive_distance_all(degrees, motors, gear_ratios):
    """Drives all motors in the list a set number of degrees set by the corresponding index in the distances list.

    The specified motor will run until it reaches the specified degree of rotation and will hold the motor
    there until a grizzly motor method is called again.
    The gear ratio should be indicated on the physical motor itself. Implementation of this method for users in PID mode:
    this method translates degrees into encoder ticks and then sets the target in said encoder ticks. When this method is called again
    on the same motor, current encoder tick position is reset to 0 and the method reruns.

    :param degrees: A list of integers corresponding to the number of ticks to be moved. The integer at the index of
        this list should match the motor's index.
    :param motor: A list of strings corresponding to the motor names to be rotated. The index of the motor names
        should match the index of the distance.
    :param gear_ratios: A list of integers corresponding to the gear ratios of the motors. The integer at the
        index of this list should match the motor's index.
    """
    assert isinstance(motors, list), "motors must be a list"
    assert isinstance(gear_ratios, list), "gear_ratios must be a list"
    assert isinstance(degrees, list), "degrees must be a list"
    assert len(degrees) == len(motors) and len(degrees) == len(gear_ratios), "List lengths for all 3 parameters must be equal"
    motor_list = mc.get("motor_values")
    for motor in motors:
        assert motor in motor_list, motor + " not found in connected motors"
    zipped = zip(motors, degrees, gear_ratios)
    mc.set("drive_distance", zipped)

  #TODO, need to reset positions each time these two methods are called.
def drive_distance_degrees(degrees, motor, gear_ratio):
    """Drives the specified motor a set number of degrees and holds the motor there.

    The specified motor will run until it reaches the specified degree of rotation and will hold the motor there until a grizzly motor method is called again.
    The gear ratio should be indicated on the physical motor itself. Implementation of this method for users in PID mode:
    this method translates degrees into encoder ticks and then sets the target in said encoder ticks. When this method is called again
    on the same motor, current encoder tick position is reset to 0 and the method reruns.

    :param degrees: An integer corresponding to the number of degrees to be moved
    :param motor: A String corresponding to the motor name to be rotated
    :param gear_ratio: An integer corresponding to the gear ratio of the motor (19 or 67)
    """
    assert isinstance(motors, str), "motor must be an String"
    assert isinstance(gear_ratios, int), "gear_ratio must be an integer"
    assert isinstance(degrees, int), "degrees must be an integer"
    motor_list = mc.get("motor_values")
    assert motor in motor_list, motor + " not found in connected motors"
    assert gear_ratio in [19,67], "Gear ratio must be 19:1 or 67:1"
    sent_list = [(motor, degrees, gear_ratio)]
    mc.set("drive_distance", sent_list)


def drive_distance_rotations(rotations, motor, gear_ratio):
    """Drives the specified motor a set number of rotations and holds the motor there.

    The specified motor will run until it reaches the specified degree of rotation and will hold the motor there until a grizzly motor method is called again.
    The gear ratio should be indicated on the physical motor itself. Implementation of this method for users in PID mode:
    this method translates degrees into encoder ticks and then sets the target in said encoder ticks. When this method is called again
    on the same motor, current encoder tick position is reset to 0 and the method reruns.

    :param rotations: An integer corresponding to the number of rotations to be moved
    :param motor: A String corresponding to the motor name to be rotated
    :param gear_ratio: An integer corresponding to the gear ratio of the motor (19 or 67)
    """
    assert isinstance(motors, str), "motor must be a String"
    assert isinstance(gear_ratios, int), "gear_ratio must be an integer"
    assert isinstance(rotations, int), "degrees must be an integer"
    motor_list = mc.get("motor_values")
    assert motor in motor_list, motor + " not found in connected motors"
    assert gear_ratio in [19,67], "Gear ratio must be 19:1 or 67:1"
    sent_list = [(motor, rotations*360, gear_ratio)]
    mc.set("drive_distance", sent_list)


def set_drive_mode(mode):
    """Sets the drive mode of all the motors between coasting and full breaking.

    Enter a string ("coast" or "brake") to specify if the motors should fully break after movement or coast to a stop. Default mode is breaking after
    movement

    :param mode: A String ("coast" or "brake") corresponding to the selected drive mode.
    """
    mode = mode.lower()
    assert mode in ["coast", "brake"], mode + " is not a valid drive mode"
    assert gear_ratio in [19,67], "Gear ratio must be 19:1 or 67:1"
    mc.set("drive_mode", [mode, "all"])

def change_control_mode_all(mode):
    """Changes PID mode for all motors connected to the robot

    This changes the control mode for inputing values into all of the motors.
    Default mode - No_PID which means one inputs a range of floats from -1 to 1 and the motor runs at a proportion corresponding to that range.

    Speed PID - Motors run at encoder ticks per second instead of an integer range. Encoder ticks are a proportion of a rotation, similar to degrees
    to check for encoder ticks for each motor, see this website: https://www.pololu.com/category/116/37d-mm-gearmotors

    Position PID - Motors run until at a certain position, using encoder ticks as units. See above website for number of ticks per degree of rotation.

    :param mode: A String ("default", "speed", "position") corresponding to the wanted control mode for all motors.

    """
    mode = mode.lower()
    assert mode in ["default", "speed", "position"], mode + " is not a valid control mode"
    mc.set("control_mode", [mode, "all"])

def change_control_mode(mode, motor):
    """Changes PID mode for specified motors connected to the robot

    This changes the control mode for inputing values into the specified motors.

    Default mode - No_PID which means one inputs a range of integers from -1 to 1 and the motor runs at a proportion corresponding to that range.

    Speed PID - Motors run at encoder ticks per second instead of an integer range. Encoder ticks are a proportion of a rotation, similar to degrees
    to check for encoder ticks for each motor, see this website: https://www.pololu.com/category/116/37d-mm-gearmotors

    Position PID - Motors run until at a certain position, using encoder ticks as units. See above website for number of ticks per degree of rotation.

    :param mode: A String ('default', 'speed', 'position') corresponding to the wanted control mode for the specified motor.

    """
    mode = mode.lower()
    assert mode in ["default", "speed", "position"], mode + " is not a valid control mode"
    motor_list = mc.get("motor_values")
    assert motor in motor_list, motor + " not found in connected motors"
    mc.set("control_mode", [mode, motor])

def change_PID_constants(value, constant):
    """Changes a PID constant which error corrects for motor positions.

    P - Proportion - changes the constant for present error correcting
    I - Integral - changes the constant for past error correcting
    D - Derivative - changes the constant for future errors - decreases response time
    For more information, refer to a mentor or the wiki page: https://en.wikipedia.org/wiki/PID_controller

    :param value: A decimal corresponding to the new coefficient of a PID constant.
    :param constant: A String ("P", "I", "D") corresponding to the constant to be changed.
    """
    constant = constant.upper()
    assert constant in ["P", "I", "D"], "invalid constant" + constant
    mc.set("PID_constant", (constant, value))

def get_PID_constants():
    """Returns a dictionary with the key being the constants and the corresponding item as the value of the constant

    Returns a list of 3 tuples with the key containing a String ("P", "I", or "D") corresponding to each of the constants. The item
    of the dictionary is that constant's current value.
    """
    return mc.get("get_PID")

def _testConnected(device_id): #checks if data exists in sensor values, throws error if doesn't
    all_data = mc.get('sensor_values')
    print(device_id)
    print(all_data)
    try:
        return all_data[device_id]
    except KeyError:
        raise KeyError("No sensor with that name")

class SensorValueOutOfBounds(Exception):
    pass
class Flag:
    OFF = 0
    LOW = 1
    MED = 2
    HIGH = 3

# pololu.com. 19:1 and 67:1 motors 37D motors geared. Be able to change PID constants. Move and stay - set point. once it is called again, reset and redo function.

"""Old functions

def set_flag(name,light0,light1,light2,light3):  #TODO UID convert to int
    \"""Sets the brightness of every LED on the team flag.

    Each LED has four levels, represented by integers. Each light is set to Flag.OFF,
    Flag.LOW, Flag.MED, Flag.HIGH

    :param name: A string that identifies the team flag.
    :param light0: An enum (OFF,LOW,MED,HIGH) which sets brightness for LED 0
    :param light1: An enum (OFF,LOW,MED,HIGH) which sets brightness for LED 1
    :param light2: An enum (OFF,LOW,MED,HIGH) which sets brightness for LED 2
    :param light3: An enum (OFF,LOW,MED,HIGH) which sets brightness for LED 3

    :Examples:

    >>> set_flag("flag1",Flag.LOW,Flag.LOW,Flag.OFF,Flag.HIGH)

    \"""
    correct_range = range(4)
    assert light1 in correct_range, "Error: input for light0 must be an integer between 0 and 3 inclusive"
    assert light2 in correct_range, "Error: input for light1 must be an integer between 0 and 3 inclusive"
    assert light3 in correct_range, "Error: input for light2 must be an integer between 0 and 3 inclusive"
    assert light4 in correct_range, "Error: input for light3 must be an integer between 0 and 3 inclusive"
    name = _lookup(name)
    flag_data = list(name) + list(light1) + list(light2) + list(light3) + list(light4)
    mc.set('flag_values',flag_data)


    def set_all_servos(name,servo0,servo1,servo2,servo3): #TODO How does the servos specifically work
    \"""Sets a degree for each servo to turn.

    Each servo (0,1,2,3) is set to turn to an interger amount of degrees (0-180)

    :param name: A string that identifies the servos.
    :param servo0: An integer between 0 and 180 which sets the amount to turn to in degrees for servo 0
    :param servo1: An integer between 0 and 180 which sets the amount to turn to in degrees for servo 1
    :param servo2: An integer between 0 and 180 which sets the amount to turn to in degrees for servo 2
    :param servo3: An integer between 0 and 180 which sets the amount to turn to in degrees for servo 3

    :Examples:

    >>> set_all_servos("servo1",90,40,30,20)

    \"""
    name = _lookup(name)
    correct_range = range(181)
    assert servo0 in correct_range, "servo0 must be between 0 and 180 inclusive"
    assert servo1 in correct_range, "servo1 must be between 0 and 180 inclusive"
    assert servo2 in correct_range, "servo2 must be between 0 and 180 inclusive"
    assert servo3 in correct_range, "servo3 must be between 0 and 180 inclusive"
    servo_data = list(name) + list(servo0) + list(servo1) + list(servo2) + list(servo3)
    mc.set('servo_values',servo_data)

    def get_all_switches(name):
    \"""Returns whether each limit switch on the identified device is pressed or not

    Each of the four limit switches on the device return either True (pressed)
    or False (not pressed). Each limit switch is specified with an intger,
    either 0, 1, 2, 3.

    :param name: A String that identifies the limit switch smart device (contains four limit switches)
    :returns: A list of boolean values, where True is pressed and False is not pressed.
              The value at index 0 corresponds to limit switch 0, index 1 to switch 1, and so forth.

    :Examples:

    >>> switches = get_all_switches("switch1")
    >>> switches
    [True,True,False,True]

    \"""
    all_data = mc.get('sensor_values')
    name = _lookup(name)
    try:
        return all_data[name]
    except KeyError:
        raise KeyError("No Sensor with that name")

    def get_all_potentiometers(name):
    \"""Returns the sensor reading of all potentiometers on the specified smart device

    Each potentiometer has an index of either 0,1,2,3. The potentiometer returns
    a decimal between 0 and 1, indicating the angle detected, where 0 and 1
    are the two extremes.

    :param name: A string that identifies the potentiometer smart device (contains four potentiometers)
    :returns: A list of decimals, each number between 0 and 1 representing the angle. Each potentiometer
              corresponds to a certain index (0,1,2,3)

    \"""
    all_data = mc.get('sensor_values')
    name = _lookup(name)
    try:
        return all_data[name]
    except KeyError:
        raise KeyError("No Sensor with that name")
"""
