left_motor = 47246689260697394641558
right_motor = 47251723202529841910772
intake = 47254408925743638880954
shooter = 47252346776555950902602
door = 47251015244498422263341


def autonomous_setup():
    #Robot.set_value(right_motor, "duty_cycle", 1)
    #Robot.set_value(left_motor, "duty_cycle", 1)
    #Robot.run(auto_actions)
    pass
def autonomous_main():
    pass
async def auto_actions():
    Robot.set_value(door, "duty_cycle", 0.5)
    await Actions.sleep(10.0)

def teleop_setup():
    # Robot.set_value(intake, "duty_cycle", 0)
    # Robot.set_value(shooter, "duty_cycle", 0)
    print("Teleop has started!")

async def door_action():
    await Actions.sleep(0.6)

async def trigger_action():
    await Actions.sleep(10)
    

dead_zone = 0.2
def teleop_main():
    # Movement
    if Gamepad.get_value("joystick_right_y") > dead_zone:
        Robot.set_value(right_motor, "duty_cycle", -1)
    elif Gamepad.get_value("joystick_right_y") < -dead_zone:
        Robot.set_value(right_motor, "duty_cycle", 1)
    else:
        Robot.set_value(right_motor, "duty_cycle", 0)
    
    if Gamepad.get_value("joystick_left_y") > dead_zone:
        Robot.set_value(left_motor, "duty_cycle", 1)
    elif Gamepad.get_value("joystick_left_y") < -dead_zone:
        Robot.set_value(left_motor, "duty_cycle", -1)
    else:
        Robot.set_value(left_motor, "duty_cycle", 0)
        
    # Intake
    if Gamepad.get_value("button_a"):
        Robot.set_value(intake, "duty_cycle", 1)
        print("intake")
    if Gamepad.get_value("button_b"):
        Robot.set_value(intake, "duty_cycle", -1)
        print("intake (backwards)")
        
    # Shooter
    if Gamepad.get_value("r_trigger"): 
        Robot.set_value(shooter, "duty_cycle", 1)
        print("shooter (up)")
    if Gamepad.get_value("l_trigger"):
        Robot.set_value(shooter, "duty_cycle", -1)
        print("shooter (down)")
        
    # Door
    if Gamepad.get_value("button_x"):
        Robot.set_value(door, "duty_cycle", 0.5)
        Robot.run(door_action)
    elif Gamepad.get_value("button_y"):
        Robot.set_value(door, "duty_cycle", -0.5)
        Robot.run(door_action)
    else:
        Robot.set_value(door, "duty_cycle", 0)