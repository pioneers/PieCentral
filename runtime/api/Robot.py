# ------
# Robot.py class 
# This runs the robot.
# Copyright 2015. Pioneers in Engineering.
# ------
from grizzly import *
#import hibike.hibike as sensors
#import Motors

addrs = Grizzly.get_all_ids()
motor = {}
name_to_grizzly = {}

# Brute force to find all 
for index in range(len(addrs)):
    # default name for motors is motor0, motor1, motor2, etc 
    grizzly_motor = Grizzly(addrs[index])
    grizzly_motor.set_mode(ControlMode.NO_PID, DriveMode.DRIVE_COAST)
    grizzly_motor.limit_acceleration(142)
    grizzly_motor.limit_current(10)
    grizzly_motor.set_target(0)

    name_to_grizzly['motor' + str(index)] = grizzly_motor
    motor['motor' + str(index)] = grizzly_motor.get_target()

def get_motor(name):
    return motor[name]

def set_motor(name, value):
    grizzly = name_to_grizzly[name]
    grizzly.set_target(value)
    motor[name] = value

# TODO: implement
def get_sensor(name):
    return None

def get_all_motors():
    return motors
