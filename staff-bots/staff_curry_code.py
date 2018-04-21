right_motor = "47242591070959169711314"
left_motor = "47253325829118006678227"
servo_controller = "33086700143774713904074"
rfid_sensor = "51967350706562744010830"
wrist_servo = "servo0"
elbow_servo = "servo1"

HIGH_FIVE_START_ANGLE = .8
HIGH_FIVE_BACK_ANGLE = -1

# Joystick input values less than this will be rounded to 0
JOYSTICK_DEAD_ZONE = .15

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
    set_elbow_servo(HIGH_FIVE_START_ANGLE)

def teleop_main():
    deadzone = lambda val : val if abs(val) > JOYSTICK_DEAD_ZONE else 0
    left_joystick = deadzone(Gamepad.get_value("joystick_left_y"))
    right_joystick = deadzone(Gamepad.get_value("joystick_right_y"))
    bound = lambda x : max(-1, min( 1, x))
    left_motor_power = left_joystick
    right_motor_power = right_joystick
    set_right_motor(right_motor_power)
    set_left_motor(left_motor_power)
    if Gamepad.get_value("l_bumper"):
        Robot.run(wave)
    if Gamepad.get_value("r_bumper"):
        Robot.run(high_five)
    if Gamepad.get_value("r_trigger"):
        reset_elbow()
    if (Robot.get_value(rfid_sensor, "tag_detect")):
        if (Robot.get_value(rfid_sensor, "id") % 100 == 25):
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
    Robot.set_value(servo_controller, elbow_servo, HIGH_FIVE_START_ANGLE)

async def wave():
    set_wrist_servo(0)
    for _ in range(3):
        set_wrist_servo(-1)
        await Actions.sleep(.5)
        set_wrist_servo(1)
        await Actions.sleep(.5)
    set_wrist_servo(0)


async def high_five():
    set_elbow_servo(HIGH_FIVE_START_ANGLE)
    await Actions.sleep(.75)
    set_elbow_servo(HIGH_FIVE_BACK_ANGLE)
    await Actions.sleep(.75)
    set_elbow_servo(HIGH_FIVE_START_ANGLE)
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
    
