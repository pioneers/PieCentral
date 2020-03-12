"""Code to just run the motors.

This code requires no gamepad and will only attempt to make the
motors spin. Useful for debugging hardware issues on robots.
"""

# Update motor values below
left_motor = ""
right_motor = ""

def autonomous_setup():
    print("Autonomous mode has started!")

def autonomous_main():
    pass

def teleop_setup():
    print("Tele-operated mode has started!")

def teleop_main():
    Robot.set_value(left_motor, "duty_cycle", 1)
    Robot.set_value(right_motor, "duty_cycle", 1)
