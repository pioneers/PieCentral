import time
import os
import sys
import json
import threading
from multiprocessing import Process
import pigpio #pylint: disable=import-error


sys.path.insert(0, '/home/pi/.local/lib/python2.7/site-packages/')


gpio = pigpio.pi()

class setInterval:
    def __init__(self, action, interval):
        self.interval = interval
        self.action = action
        self.stopEvent = threading.Event()
        thread = threading.Thread(target=self.__setInterval)
        thread.start()

    def __setInterval(self):
        nextTime = time.time() + self.interval
        while not self.stopEvent.wait(nextTime-time.time()):
            nextTime += self.interval
            self.action()

    def cancel(self):
        self.stopEvent.set()


class led:
    def __init__(self, rgbPins):
        self.rgb = rgbPins
    def reset(self):
        for color in self.rgb:
            gpio.write(color, 1)
    def strobe(self, speed):
        flag = False
        print("Strobe")
        def action(self, flag):
            print("Strobing, flag: ", flag)
            setRgb([flag, flag, flag]) #pylint: disable=undefined-variable
            flag = not flag
        return setInterval(action(self, flag), 1 / speed)
    def setRgb(self, vals):
        for i in range(len(vals)):
            if vals[i] % 1 == 0:
                gpio.write(self.rgb[i], not vals[i])
            else:
                gpio.set_PWM_dutycycle(self.rgb[i], 255 * (1 - vals[i]))

strip = led([2, 3, 4])
currentAnimation = None

motor = {
    "config": {
        "drive": 0.5,
        "lift": 1
    },
    "right": {
        "name": "right",
        "pins": [12, 16],
        "value": 0
    },
    "left": {
        "name": "left",
        "pins": [21, 20],
        "value": 0
    },
    "lift": {
        "name": "lift",
        "pins": [19, 26],
        "value": 0
    }
}


auto = {
    "file": "/home/pi/Autonomous/autonomous_motor-paths.json",
    "recording": False,
    "motor": {},
    "foot": 0.73469387748,
    "rotation": 2.45
}


startTime = 0
switchID = "18851477588195929070"
switch0 = False
switch1 = False
switch2 = False
stop_down = 1
stop_up = 1
start_pos_up = 1
def setM(m, speed):
    global startTime
    global motor
    global auto
    if speed != motor[m["name"]]["value"]:
        motor[m["name"]]["value"] = speed
        if auto["recording"]:
            auto["motor"][m["name"]]["path"].append({
                "time": time.time() - startTime,
                "value": speed
            })
        if speed >= 0:
            gpio.write(m["pins"][1], 0)
            gpio.set_PWM_dutycycle(m["pins"][0], 255 * speed)
        else:
            gpio.write(m["pins"][0], 0)
            gpio.set_PWM_dutycycle(m["pins"][1], 255 * -speed)
    # setM(motor, speed)

def resetMotors():
    for m in motor:
        if "pins" in motor[m]:
            gpio.write(motor[m]["pins"][0], 0)
            gpio.write(motor[m]["pins"][1], 0)
resetMotors()

def autonomous_setup():
    print("Autonomous mode has started!")
    Robot.run(autonomous_play) #pylint: disable=undefined-variable

def autonomous_main():
    pass

async def autonomous_actions():
    #Tells robot to move forward:
    Robot.run(autonomous_move()) #pylint: disable=undefined-variable

async def autonomous_play():
    data = json.load(open(auto["file"], 'r'))
    startTime = time.time() #pylint: disable=redefined-outer-name
    mPath = data[len(data) - 1]
    for m in mPath["motor"]:
        mPath["motor"][m]["step"] = 0
    while time.time() - startTime < mPath["time"]:
        for m in mPath["motor"]:
            m = mPath["motor"][m]
            currentTime = time.time() - startTime
            if m["step"] < len(m["path"]) - 1 and currentTime > m["path"][m["step"] + 1]["time"]:
                print('m["step"]: ' + str(m["step"]))
                m["step"] += 1
                setM(m, m["path"][m["step"]]["value"])

#pylint: disable=redefined-outer-name
async def auto_action(motor, time):
    setM(motor, motor["value"])
    await Actions.sleep(time) #pylint: disable=undefined-variable
async def autonomous_move():
    pass

def teleop_setup():
    print("Tele-operated mode has started!")

def teleop_main():
    #pylint: disable=too-many-statements
    global stop_up
    global stop_down
    global start_pos_up
    global auto
    global startTime
    global motor
    global currentAnimation
    # pylint: disable=undefined-variable
    dup = Gamepad.get_value("dpad_up")
    ddown = Gamepad.get_value("dpad_down")
    dleft = Gamepad.get_value("dpad_left")
    dright = Gamepad.get_value("dpad_right")
    if Gamepad.get_value("button_start"):
        if not auto["recording"]:
            print("Recording")
            auto["recording"] = True
            startTime = time.time()
            for m in motor:
                if "name" in motor[m]:
                    auto["motor"][motor[m]["name"]] = motor[m]
                    auto["motor"][motor[m]["name"]]["path"] = [{
                        "time": 0,
                        "value": 0
                    }]
            strip.setRgb([0.5, 0, 0])
        else:
            print("Already recording")
    if Gamepad.get_value("button_back"):
        if auto["recording"]:
            print("Logging Record")
            auto["recording"] = False
            data = json.load(open(auto["file"], 'r'))
            data.append({
                "title": "Untitled",
                "time": time.time() - startTime,
                "motor": auto["motor"]
            })
            # print(json.dumps(data, indent=2))
            json.dump(data, open(auto["file"], 'w'), indent=2)
            for i in range(0, 7):
                strip.setRgb([0, i % 2, 0])
                time.sleep(0.1)
        else:
            print("Not recording")
    if Gamepad.get_value("button_b"):
        #currentAnimation and \
        currentAnimation.cancel()
        currentAnimation = strip.strobe(10)
    if Gamepad.get_value("r_bumper"):
        motor["config"]["drive"] = 1
    if Gamepad.get_value("l_bumper"):
        motor["config"]["drive"] = 0.5
    if dup:
        if dleft:
            setM(motor["left"], 0)
            setM(motor["right"], motor["config"]["drive"])
        elif dright:
            setM(motor["left"], motor["config"]["drive"])
            setM(motor["right"], 0)
        else:
            setM(motor["left"], motor["config"]["drive"])
            setM(motor["right"], motor["config"]["drive"])
    elif ddown:
        if dleft:
            setM(motor["left"], 0)
            setM(motor["right"], -motor["config"]["drive"])
        elif dright:
            setM(motor["left"], -motor["config"]["drive"])
            setM(motor["right"], 0)
        else:
            setM(motor["left"], -motor["config"]["drive"])
            setM(motor["right"], -motor["config"]["drive"])
    elif dright:
        setM(motor["right"], -motor["config"]["drive"])
        setM(motor["left"], motor["config"]["drive"])
    elif dleft:
        setM(motor["right"], motor["config"]["drive"])
        setM(motor["left"], -motor["config"]["drive"])
    else:
        setM(motor["right"], 0)
        setM(motor["left"], 0)
    # setM(motor["left"], (Gamepad.get_value("dpad_up") - Gamepad.get_value("dpad_down") +
    # Gamepad.get_value("dpad_right") - Gamepad.get_value("dpad_left")) * motor["config"]["drive"])
    # setM(motor["right"], (Gamepad.get_value("dpad_up") - Gamepad.get_value("dpad_down") -
    # Gamepad.get_value("dpad_right") + Gamepad.get_value("dpad_left")) * motor["config"]["drive"])
    if Gamepad.get_value("r_bumper"):
        motor["config"]["drive"] = 1
    if Gamepad.get_value("l_bumper"):
        motor["config"]["drive"] = 0.5
    if Gamepad.get_value("r_trigger") == 1:
        stop_down = 1  # clear stop value
        start_pos_up = 1
        if Robot.get_value(switchID, "switch0") and stop_up:
            setM(motor["lift"], motor["config"]["lift"])# keep going UP
        else: # hit top limit switch, stop and reverse motor
            setM(motor["lift"], 0.0)  # stop motor for now
    elif Gamepad.get_value("l_trigger") == 1:
        start_pos_up = 1
        stop_up = 1  # clear stop value
        if Robot.get_value(switchID, "switch2") and stop_down:
            setM(motor["lift"], -motor["config"]["lift"])# keeping going DOWN
        else: # hit bottom limit switch, stop and reverse motor
            setM(motor["lift"], 0.0)  # stop motor for now
    elif Gamepad.get_value("button_a") == 1:
        if Robot.get_value(switchID, "switch1") and start_pos_up:
            setM(motor["lift"], motor["config"]["lift"]) # go up
        elif Robot.get_value(switchID, "switch1") == 0:
            setM(motor["lift"], 0.0)# stop
            start_pos_up = 0
    else:
        start_pos_up = 1
        setM(motor["lift"], 0.0)




# Problem 1
def tennis_balls2(num):
    #pylint: disable=no-else-return
    if num % 3 == 0:
        return num / 3
    elif not num % 2 == 0:
        return num * 4 + 2
    else:
        return num + 1
def tennis_ball(num):
    for _ in range(0, 5):
        num = tennis_balls2(num)
    return num

# Problem 2
def remove_duplicates(num):
    num2 = str(num)
    array = ""
    i = 0
    while i < len(num2):
        #print("I"+str(i))
        if i < len(num2):
            #print("I"+str(i))
            if num2[i] in array:
                #print("in"+num2[i])
                #print(num2)
                if i < len(num2):
                    num2 = num2[:i]+num2[i+1:]
                else:
                    num2 = num2[:i-1]
        #num2 = num2.split(num2[i])
        #print(num2)
            i -= 1
        else:
            #print("Array"+array)
            array += num2[i]
            i += 1
    return int(num2)

# Problem 3
def rotate(num):
    num = str(num)
    big = 0
    for i in num:
        if int(i) > big:
            big = int(i)
    for i in range(big):
        lastnum = num[-1:]
        num = num[:-1]
        num = lastnum + num
    return int(num)

#Problem 4
def next_fib(num):
    i = 0
    j = 1
    #pylint: disable=no-else-return
    if num == 0:
        return 0
    elif num == 1:
        return 1
    while j < num:
        temp = j
        j = i + j
        i = temp
    return j

# Problem 5
def most_common(inputnum):
    outs = []
    zeroArr = []
    for i in range(10):
        outs.append(0)
        zeroArr.append(0)

    for i in str(inputnum):
        outs[int(i)] += 1

# Problem 6
def get_coins(num):
    q = (int)(num / 25)
    num = num % 25
    n = (int)(num / 5)
    num = num % 5
    return int(str(q)+str(n)+str(num))
