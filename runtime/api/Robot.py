# ------
# Robot.py class 
# This runs the robot.
# Copyright 2015. Pioneers in Engineering.
# ------
from grizzly import *
import hibike.hibike as sensors
import Motors 

addrs = Grizzly.get_all_ids()
motors = {}
# This should be a dictionary
name_to_grizzly = {}

for index in range(len(addrs)):
    # default name for motors is motor0, motor1, motor2, etc 
    grizzly_motor = Grizzly(grizzly_id)
    grizzly_motor.set_mode(ControlMode.NO_PID, DriveMode.DRIVE_COAST)
    grizzly_motor.limit_acceleration(142)
    grizzly_motor.limit_current(10)
    grizzly_motor.set_target(0)
 
    name_to_grizzly['motor' + index] = grizzly_motor
    motor['motor' + index] = grizzly_motor.get_target()

# returns motor speed
def get_motor(name):
    return motor[name]            

def set_motor(name, value):
    grizzly = name_to_grizzly[name]
    grizzly.set_target(value)
    motor[name] = value

def get_sensor(name):
    

def get_all_motors():
    return motors

