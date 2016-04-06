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
>>> from api.Robot import *
'''
# Connect to memcache
import memcache
memcache_port = 12357
mc = memcache.Client(['127.0.0.1:%d' % memcache_port]) # connect to memcache

motor = {}

_naming_map_filename = 'student_code/CustomID.txt'
_name_to_id = {} # Mapping from motor name to device_id, both are strings
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

    >>> motor = get_motor("motor1")

    """
    device_id = _lookup(name)
    name_to_value = mc.get('motor_values')
    assert type(device_id) is str, "Type Mismatch: Must pass in a string"
    try:
        return name_to_value[device_id]/100
    except KeyError:
        raise KeyError("Motor name not found.")

def set_motor(name, value):
    """Sets a motor to the specified power value.

    :param name: A string that identifies the motor.
    :param value: A decimal value between -1 and 1, the power level you want to set.

    :Examples:

    >>> set_motor("motor1", .50)

    """
    assert type(name) is str, "Type Mismatch: Must pass in a string to name."
    assert type(value) is int or type(value) is float, "Type Mismatch: Must pass in an integer or float to value."
    assert value <= 1 and value >= -1, "Motor value must be a decimal between -1 and 1 inclusive."
    device_id = _lookup(name)
    name_to_value = mc.get('motor_values')
    if device_id not in name_to_value:
        raise KeyError("No motor with that name")
    name_to_value[device_id] = value*100
    mc.set('motor_values', name_to_value)

def get_sensor(name):
    """Returns the value, or reading corresponding to the specified sensor.

    WARNING: This is a default get method and should only be used if the sensor in question
    does not have a specific get function.
    You should always use a specific sensor's get function if specified in this doc.

    :param name: A string that identifies the sensor.
    :returns: The reading of the sensor at the current point in time.

    :Examples:

    >>> get_sensor("sensor1")

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

    >>> set_LED(0, False)
    >>> set_LED(1, True)
    """
    flag_data = mc.get('flag_values')
    flag_data[num] = value
    mc.set('flag_values', flag_data)

def set_servo(name,value):  #TODO Check with hibike on exact functionality
    """Sets a degree for a specific servo to turn.

    One servo, as specified by its name, is set to turn to an integer amount of degrees (0-180)

    :param name: A string that identifies the servo
    :param value: An integer between 0 and 180 which sets the amount to turn to in degrees

    :Examples:

    >>> set_servo("servo1",90)
    >>> set_servo("servo3",150)

    """
    assert 0 <= value <= 180, "Servo degrees must be between 0 and 180"
    device_id = _lookup(name)
    name_to_value = mc.get('servo_values')
    name_to_value[device_id] = value
    mc.set('servo_values', name_to_value)

def get_servo(name):
    """Gets the degree that a servo is set to.

    Each servo is set to an integer degree value (0-180). This function returns
    what value the servo is currently set to.

    :param name: A string that identifies the servo

    :Examples:

    >>> get_servo("servo1")
    45

    """
    device_id = _lookup(name)
    return _testConnected(device_id)

def get_rgb(name):
    """Returns a list of rgb values from the specified color sensor.

    Each value for red, green, and blue will return a
    number between 0 and 255, where 255 indicates a higher intensity. This function returns
    the result from one specific color sensor.

    :param name: A string that identifies the color sensor
    :returns: A list of integers in the order of values for red, green, blue

    :Examples:

    >>> color = get_color_sensor("color1")
    >>> color
    [100, 240, 150]

    """
    device_id = _lookup(name)
    data = _testConnected(device_id)
    red = data[0]
    green = data[1]
    blue = data[2]
    return [red, green, blue]

def get_luminosity(name):
    """Returns the luminosity for the specified color sensor.

    The color sensor returns the luminosity detected by the color sensor, represnted by
    a decimal where larger numbers indicates higher intensity.

    :param name: A string that identifies the color sensor
    :returns: A double where a larger number indicates a higher intensity

    :Examples:

    >>> lum_berry = get_luminosity("color1")

    """
    device_id = _lookup(name)
    return _testConnected(device_id)[3]

def get_hue(name):
    """Returns the hue detected at the specified color sensor.

    This uses the red, green, and blue sensors on the color sensor to return the
    detected hue, which is represented as a double between 0 and 360. See
    https://en.wikipedia.org/wiki/Hue for more information on hue.

    :param name: A string that identifies the color sensor
    :returns: A double between 0 and 360 representing the detected hue

    :Examples:

    >>> hue = get_hue("color1")
    >>> hue
    254.01

    """
    device_id = _lookup(name)
    return _testConnected(device_id)[4]

def toggle_light(name, status):
    """Turns the light on specfied color sensor on or off.

    Takes in the name of the specified color sensor and a boolean (True for on, False for off).

    :param name: A string that identifies the color sensor.
    :param status: A boolean that determines whether the light should be on (True) or off (False)

    >>> toggle_light("color1", True)
    >>> toggle_light("color2", False)

    """
    device_id = _lookup(name)
    if (status):
        write_value = 1
    else:
        write_value = 0
    mc.set("toggle_light", [device_id, write_value])

def get_distance_sensor(name):
    """Returns the distance away from the sensor an object is, measured in centimeters

    :param name: A String that identifies the distance sensor
    :returns: A double representing how many centimeters away the object is from the sensor

    :Examples:

    >>> distance = get_distance_sensor("distance1")
    >>> distance
    10.76

    """
    device_id = _lookup(name)
    return _testConnected(device_id)


def get_limit_switch(name):
    """Returns whether a specified limit switch on the identified device is pressed or not

    The specified limit switch returns a boolean, either True (pressed) or False (not pressed).

    :param name: A String that identifies the limit switch
    :returns: A boolean value, where True is pressed and False is not pressed.

    :Examples:

    >>> switch = get_limit_switch("switch1")
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

    >>> potentiometer = get_potentiometer("potentiometer1")
    >>> potentiometer
    0.364

    """
    device_id = _lookup(name)
    return _testConnected(device_id)

def get_metal_detector(name): #TODO metal detector Implementation
    """Returns the sensor reading of the specified metal detector

    Each metal detector returns an integer, which changes based on the prescence of metal.
    After callibration, the value should increase in the presence of steel and decrease in
    the presence of aluminum. There is random drift of around 8 so your code should callibrate
    in air often.

    :param name: A String that identifies the metal detector smart device.
    :returns: An integer (large) which represents whether metal is detected or not.

    """
    device_id = _lookup(name)
    return _testConnected(device_id)

def calibrate_metal_detector(name): #TODO test calibration 
    """Calibrates the specified metal sensor

    Calibrates to set the current reading of the metal detector to air (0). It is
    recommended that this is called before every reading to avoid misreading values
    due to drift.

    :param name: A String that identifies the metal detector smart device.

    """
    device_id = _lookup(name)

    mc.set("metal_detector_calibrate",[device_id, True])


def get_line_sensor(name):
    """Returns a value used to determine whether the selected sensor is over a line or not

    If the selected sensor (left, center, or right) is over a line/reflective surface, 
    this will return an double close to 0; 
    Over the ground or dark material, this will return an double close to 1. 

    :param name: A String that identifies the reflecting smart device.
    :returns: An double that specifies whether it is over the tape (0 - 1)

    >>> line_sensor = get_line_sensor("line_sensor_1")
    >>> line_sensor
    0.03

    """
    device_id = _lookup(name)
    return _testConnected(device_id)

def drive_distance_all(degrees, motors, gear_ratios):
    """WARNING: THIS METHOD IS NOT GUARANTEED TO WORK. USE WITH CAUTION.

    Drives all motors in the list a set number of degrees set by the corresponding index in the distances list.

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
    """WARNING: THIS METHOD IS NOT GUARANTEED TO WORK. USE WITH CAUTION.

    Drives the specified motor a set number of degrees and holds the motor there.

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
    """WARNING: THIS METHOD IS NOT GUARANTEED TO WORK. USE WITH CAUTION.

    Drives the specified motor a set number of rotations and holds the motor there.

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

    >>> set_drive_mode("coast")

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
    :param motor: A String corresponding to the motor name whose PID mode is to be changed

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

def _testConnected(device_id): # Returns value if device_id exists, otherwise throws SensorValueOutOFBounds Exception
    all_data = mc.get('sensor_values')
    try:
        return all_data[device_id]
    except KeyError:
        raise KeyError("No sensor with that name")

class SensorValueOutOfBounds(Exception):
    pass

def _get_all():
    return mc.get('sensor_values')

# pololu.com. 19:1 and 67:1 motors 37D motors geared. Be able to change PID constants. Move and stay - set point. once it is called again, reset and redo function.
