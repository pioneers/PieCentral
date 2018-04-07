"""Template code to be filled out as desired."""

# Update motor values below
left_motor = ""
right_motor = ""

# Example usage of setting a motor
# Robot.set_value(left_motor, "duty_cycle", 1)

# Example usage of reading a joystick
# Gamepad.get_value("joystick_left_y")

async def async_action():
    """Demonstrate the syntax necessary for an async function."""
    print("Begin async action")
    await Actions.sleep(1.0)
    print("End async action")

def autonomous_setup():
    """Runs once at the beginning of the autonomous period"""
    Robot.run(async_action)
    pass

def autonomous_main():
    """Runs repeatedly after autonomous_setup during the autonomous period"""
    pass

def teleop_setup():
    """Runs once at the beginning of the tele-operated period"""
    pass

def teleop_main():
    """Runs repeatedly after teleop_setup during the tele-operated period"""
    pass
