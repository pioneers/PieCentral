# ------
# Robot.py class 
# This runs the robot.
# Copyright 2015. Pioneers in Engineering.
# ------
import Motors

class Robot:
    
    # Constructor for a generic robot program
    def __init__(self):
        self.motors = []
        for addr in Motor.addrs:
            motor = Motor(addr)
            self.motors.append(motor)
    
    # Takes in a list of speeds in the order of
    # which motors are assigned in the array. 
    # Note: This method does not fix motors being
    # backwards or anything, so YOU have to look at that yourself.
    def drive(self, *args):
        for index in range(len(args)):
            motor[index].set_speed(args[index])
    
    # This method will ensure that everything is multiplied by 100
    # But nothing else.
    def drive_from_controller(self, *args):
        for index in range(len(args)):
            args[index] *= 100
        self.drive(args)
        
    # Used for emergency stop
    def stop(self):
        for motor in self.motors:
            motor.reset_motor()
    
