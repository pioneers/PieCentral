LEFT_MOTOR = "47247340194346110374475"
RIGHT_MOTOR = "47251990230774402016707"
ROLLER_1 = "47259875637510041669996"
ROLLER_2 = "47255942494625596366282"
ROLLER_3 = "47252674151435785332705"
EJECTOR = "47245941309177314478533"
RFID = "51976799624964855185866"
SERVO = "33083301126422111083747"


### autonomous mode code #######################################################

# go forward with both motors at full power
def full_speed_ahead():
    Robot.set_value(LEFT_MOTOR, "duty_cycle", 1.0)
    Robot.set_value(RIGHT_MOTOR, "duty_cycle", -1.0)

# stop moving entirely.
def stahhhp():
    Robot.set_value(LEFT_MOTOR, "duty_cycle", 0.0)
    Robot.set_value(RIGHT_MOTOR, "duty_cycle", 0.0)

auto_stop_time = None
def autonomous_setup():
    global auto_stop_time
    auto_stop_time = time.time() + 3

"""
Drives forward at full power for 3 seconds, then stops. It would be nicer to do
more in autonomous mode, obviously, but we're pretty time constrained here...
"""
def autonomous_main():
    if time.time() > auto_stop_time:
        full_speed_ahead()
    else:
        stahhhp()

### teleop mode code ###########################################################
threshold = 0.2
def tank_drive():
    left_y = -Gamepad.get_value("joystick_left_y")
    right_y = Gamepad.get_value("joystick_right_y")

    if abs(left_y) > threshold:
        Robot.set_value(LEFT_MOTOR, "duty_cycle", left_y)
    else:
        Robot.set_value(LEFT_MOTOR, "duty_cycle", 0)
    if abs(right_y) > threshold:
        Robot.set_value(RIGHT_MOTOR, "duty_cycle", right_y)
    else:
        Robot.set_value(RIGHT_MOTOR, "duty_cycle", 0)

def toggle_roller():
    if Gamepad.get_value("r_bumper"):
        Robot.set_value(ROLLER_1, "duty_cycle", 1.0)
        Robot.set_value(ROLLER_2, "duty_cycle", 0.65)
        Robot.set_value(ROLLER_3, "duty_cycle", 0.65)
    elif Gamepad.get_value("l_bumper"):
        Robot.set_value(ROLLER_1, "duty_cycle", -1.0)
        Robot.set_value(ROLLER_2, "duty_cycle", -0.65)
        Robot.set_value(ROLLER_3, "duty_cycle", -0.65)
    else:
        Robot.set_value(ROLLER_1, "duty_cycle", 0.0)
        Robot.set_value(ROLLER_2, "duty_cycle", 0.0)
        Robot.set_value(ROLLER_3, "duty_cycle", 0.0)


GOOD_COIN = 0 # not sure if this should be set to 1 or 0
BAD_COIN = 1 - GOOD_COIN
DOOR_OPEN = -1.0
DOOR_CLOSED = -0.4

def manage_door():
    id_val = Robot.get_value(RFID, "id")
    should_open = (id_val != 0) and (id_val % 2 == GOOD_COIN)
    should_close = (id_val != 0) and (id_val % 2 == BAD_COIN)

    # hurry up and get the door open so a coin can get inside
    if should_open:
        Robot.set_value(SERVO, "servo0", DOOR_OPEN)
        Robot.set_value(SERVO, "servo1", -DOOR_OPEN)
        return

    # close the door to block out an incoming bad coin
    if should_close:
        Robot.set_value(SERVO, "servo0", DOOR_CLOSED)
        Robot.set_value(SERVO, "servo1", -DOOR_CLOSED)
        return

def shoot_coins():
    if Gamepad.get_value("r_trigger") or Gamepad.get_value("l_trigger"):
        Robot.set_value(EJECTOR, "duty_cycle", -1.0)
    else:
        Robot.set_value(EJECTOR, "duty_cycle", 0.0)

def teleop_main():
    # Just call our handler functions...
    # all of the hard work is done at this point
    tank_drive()
    toggle_roller()
    manage_door()
    shoot_coins()

def teleop_setup():
    print("teleop mode has started!")
    Robot.set_value(SERVO, "servo0", DOOR_CLOSED)
    Robot.set_value(SERVO, "servo1", -DOOR_CLOSED)
