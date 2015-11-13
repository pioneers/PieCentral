# ------
# Robot.py class 
# This runs the robot.
# Copyright 2015. Pioneers in Engineering.
# ------
#from grizzly import *
#import hibike.hibike as sensors
#import hibike
#import Motors
import memcache

memcache_port = 12357
mc = memcache.Client(['127.0.0.1:%d' % memcache_port]) # connect to memcache

motor = {}
#name_to_grizzly = {}

#def init():
    #addrs = Grizzly.get_all_ids()
    #h = hibike.Hibike()
    #connectedDevices = h.getEnumeratedDevices() #get list of devices
    #h.subscribeToDevices(connectedDevices) #subscribe to devices

    # Brute force to find all 
    #for index in range(len(addrs)):
    #    # default name for motors is motor0, motor1, motor2, etc 
    #    grizzly_motor = Grizzly(addrs[index])
    #    grizzly_motor.set_mode(ControlMode.NO_PID, DriveMode.DRIVE_COAST)
    #    grizzly_motor.limit_acceleration(142)
    #    grizzly_motor.limit_current(10)
    #    grizzly_motor.set_target(0)

    #    name_to_grizzly['motor' + str(index)] = grizzly_motor
        #motor['motor' + str(index)] = grizzly_motor.get_target()

    #print(name_to_grizzly, addrs)

def get_motor(name):
    #return motor[name]
    name_to_value = mc.get('motor_values')
    if name in name_to_value:
        return name_to_value[name]
    return 'Error, motor with that name not found'

def set_motor(name, value):
    print(name_to_grizzly)
    name_to_value = mc.get('motor_values')
    #grizzly = name_to_grizzly[name]
    if name in name_to_value:
        name_to_value[name] = value
        mc.set('motor_values', name_to_value)
    else:
        print("No motor with that name")
    #grizzly.set_target(value)
    #motor[name] = value

# TODO: implement
def get_sensor(name):
    #return h.getData(name) #return latest sensor value
    all_data = mc.get('sensor_values')
    if name in all_data:
        return all_data[name]
    return 'Error, sensor with that name not found'

def get_all_motors():
    return mc.get('motor_values')
