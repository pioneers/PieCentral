left_motor = "47250246222630351826392"
right_motor = "47242769666972617759775"
servo_controller = "33090094875193840563108"
rfid_sensor = "51977090869270841821982"
wrist_servo = "servo0"
elbow_servo = "servo1"

def autonomous_setup():
    print("Autonomous mode has started!")

def autonomous_main():
    pass

async def autonomous_actions():
    print("Autonomous action sequence started")
    await Actions.sleep(1.0)
    print("1 second has passed in autonomous mode")

def teleop_setup():
    print("Tele-operated mode has started!")

def teleop_main():

    set_left_motor(1 * Gamepad.get_value("joystick_right_y"))
    set_right_motor(1 * Gamepad.get_value("joystick_left_y"))
    # set_right_motor(1)
    # Robot.run(jiggle, .2)
    if Gamepad.get_value("l_bumper"):
        Robot.run(wave)
    if Gamepad.get_value("r_bumper"):
        Robot.run(high_five)
    if Gamepad.get_value("r_trigger"):
        reset_elbow()
    # if Gamepad.get_value("joystick_right_y") > 0.5:
    #     Robot.set_value(left_motor, "duty_cycle", -1.0)
    #     Robot.set_value(right_motor, "duty_cycle", -1.0)
    # else:
    #     Robot.set_value(left_motor, "duty_cycle", 0)
    #     Robot.set_value(right_motor, "duty_cycle", 0)
    if (Robot.get_value(rfid_sensor, "tag_detect")):
        if (Robot.get_value(rfid_sensor, "id") > 100):
            Robot.run(wave)
        else:
            Robot.run(high_five)
    
def set_left_motor(power):
    """Sets the power of the left motor"""
    Robot.set_value(left_motor, "duty_cycle", -1 *power)
    
def set_right_motor(power):
    """Sets the power of the right motor"""
    Robot.set_value(right_motor, "duty_cycle", 1 * power)
    
def set_wrist_servo(angle):
    Robot.set_value(servo_controller, wrist_servo, angle)
    
def set_elbow_servo(angle):
    Robot.set_value(servo_controller, elbow_servo, angle)

def reset_elbow():
    Robot.set_value(servo_controller, elbow_servo, 0)

async def wave():
    set_wrist_servo(0)
    for _ in range(3):
        set_wrist_servo(-1)
        await Actions.sleep(1)
        set_wrist_servo(1)
        await Actions.sleep(1)
    set_wrist_servo(0)

async def high_five():
    set_elbow_servo(0)
    await Actions.sleep(1)
    set_elbow_servo(-1)
    await Actions.sleep(1)
    set_elbow_servo(0)
    print("resetting elbow servo")
    await Actions.sleep(1)

async def wave_and_high_five():
    set_wrist_servo(0)
    for _ in range(2):
        set_elbow_servo(0)
        await Actions.sleep(1)
        set_elbow_servo(-1)
        await Actions.sleep(1)

    set_elbow_servo(.1)
    await Actions.sleep(.3)
    set_elbow_servo(.05)
    await Actions.sleep(.3)
    set_elbow_servo(0)
    await Actions.sleep(1)
    
    for _ in range(3):
        set_wrist_servo(-1)
        await Actions.sleep(1)
        set_wrist_servo(1)
        await Actions.sleep(1)
    
async def jiggle(power):
    set_right_motor(power)
    set_left_motor(power)
    await Actions.sleep(.5)
    set_right_motor(0)
    set_left_motor(0)
    await Actions.sleep(1)
    set_right_motor(-power)
    set_left_motor(-power)
    await Actions.sleep(.9)
    set_right_motor(0)
    set_left_motor(0)
    await Actions.sleep(.5)
    
