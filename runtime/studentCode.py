right_motor = "47257694863303572622996"
left_motor = "56692491028743135592595"
servo_controller = "33083708407374743778514"
rfid_sensor = "51967350706562744010830"
wrist_servo = "servo0"
elbow_servo = "servo1"

HIGH_FIVE_START_ANGLE = .8
HIGH_FIVE_BACK_ANGLE = -1

# Joystick input values less than this will be rounded to 0
JOYSTICK_DEAD_ZONE = .15

import math

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


"""
def tennis_ball(n):
    return 1

def remove_duplicates(n):
    return 1

def rotate(n):
    return 1

def next_fib(n):
    return 1

def most_common(n):
    return 1

def get_coins(n):
    return 1
"""


def rotate(numbers):
    copy = numbers
    max_num = 0
    while copy:
        num = copy % 10
        copy = copy // 10
        size = math.log(numbers)//math.log(10)
        max_num = num if num > max_num else max_num
    for i in range(max_num):
        lsd = numbers % 10
        numbers = numbers // 10
        msd = (lsd) * 10**(size)
        numbers = numbers + msd
    return int(numbers)

def tennis_ball(num):
    index = 5
    while index > 0:
        if num % 3 == 0:
            num = num // 3
        elif num % 2 == 1:
            num = num * 4 + 2
        else:
            num += 1
        index -= 1
    return num

def most_common(num):
    parse = []
    while num != 0:
        parse.append(num % 10)
        num = num // 10
    parse.reverse()
    l = list(set(parse))
    if len(l) <= 4:
        l = sorted(l, reverse=True)
    else:
        ret = []
        d = {}
        for n in parse:
            if n in d.keys():
                d[n] += 1
            else:
                d[n] = 1
        final = []
        boolean = {}
        for key, value in sorted(d.items(), key=lambda kv: kv[1], reverse = True):
            final.append(key)
            boolean[key] = False
        boolean[final[3]] = True
        for key in final:
            if d[key] == d[final[3]]:
                boolean[key] = True
        for i in range(4):
            if boolean[final[i]] == False:
                ret.append(final[i])
        left = 4 - len(ret)
        if left != 0:
            for i in range(len(parse)):
                if boolean[parse[i]] == True and parse[i] not in ret:
                    print(parse[i])
                    ret.append(parse[i])
                    left -= 1
                    if left == 0:
                        break
        l = sorted(ret, reverse=True)
    final_num = 0
    while l != []:
        final_num = final_num * 10 + l[0]
        l = l[1:]
    return final_num

def remove_duplicates(num):
    l = []
    while num > 0:
        l = [num % 10] + l
        num = num // 10
    final = []
    for i in range(len(l)):
        y = 0
        exist = False
        while y < i:
            if l[i] == l[y]:
                exist = True
            y += 1
        if not exist:
            final = [l[i]] + final
    n = 0
    while final != []:
        n = 10 * n + final[-1]
        final = final[:-1]
    return n

def next_fib(num):
    first = 0
    second = 1
    sum = 0
    if num == 0:
        return 0
    for i in range(num):
        sum = first + second
        if sum >= num:
            return sum
        first = second
        second = sum

def get_coins(num):
    quarters = num // 25
    nickels = (num - 25 * quarters) // 5
    pennies = num - nickels * 5 - quarters * 25
    return int(str(quarters) + str(nickels) + str(pennies))
