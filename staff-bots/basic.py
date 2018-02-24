"""Basic robot control to test motors and drive"""

# Choose whether to test the bot with a controller
IGNORE_CONTROLLER = False

# Update motor values below
left_motor = ""
right_motor = ""
assert left_motor and right_motor, "Insert the motor IDs from Dawn"

def autonomous_setup():
    print("Autonomous mode has started!")

def autonomous_main():
    pass

def teleop_setup():
    print("Tele-operated mode has started!")

def teleop_main():
    if USE_CONTROLLER:
        # Drive straight; ignore controller input
        Robot.set_value(left_motor, "duty_cycle", 1)
        Robot.set_value(right_motor, "duty_cycle", -1)
    else:
        # Use controller input
        left_read = Gamepad.get_value("joystick_left_y")
        right_read = Gamepad.get_value("joystick_right_y")
        Robot.set_value(left_motor, "duty_cycle", right_read)
        Robot.set_value(right_motor, "duty_cycle", -left_read)

async def async_action():
    """Spin the robot for a second.

    Demonstrate the syntax necessary for an async function.
    """
    print("Async action")
    Robot.set_value(left_motor, "duty_cycle", 1)
    Robot.set_value(right_motor, "duty_cycle", 1)
    await Actions.sleep(1.0)
    Robot.set_value(left_motor, "duty_cycle", 0)
    Robot.set_value(right_motor, "duty_cycle", 0)
    print("1 second has passed in autonomous mode")


