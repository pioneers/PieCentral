import time
import asyncio
from runtimeUtil import *


def autonomous_setup():
    pass


def autonomous_main():
    pass


def teleop_setup():
    pass


def teleop_main():
    pass


def setup():
    pass


def main():
    pass


def asyncawait_setup():
    Robot.create_key("right")
    Robot.create_key("counter")
    Robot._set_sm_value(3.0, "right")
    Robot._set_sm_value(0.0, "counter")
    Robot.run(asyncawait_helper)


def asyncawait_main():
    Robot._set_sm_value(Robot._get_sm_value("counter") + 1, "counter")
    if Robot._get_sm_value("right") == 4 and Robot._get_sm_value("counter") == 3:
        print("Async Success")


async def asyncawait_helper():
    Robot._set_sm_value(Robot._get_sm_value("right") + 1, "right")


def test0_setup():
    print("test0_setup")


def test0_main():
    print("test0_main")


def mainTest_setup():
    pass


def mainTest_main():
    response = Robot._get_sm_value("incrementer")
    print("Get Info:", response)
    response -= 1

    Robot._set_sm_value(response, "incrementer")

    print("Saying hello to the other side")
    print("DAT:", 1.0 / response)


def nestedDict_setup():
    pass


def nestedDict_main():
    print("CODE LOOP")
    response = Robot._get_sm_value("dict1", "inner_dict1_int")
    print("Get Info:", response)

    response = 1
    Robot._set_sm_value(response, "dict1", "inner_dict1_int")
    response = Robot._get_sm_value("dict1", "inner_dict1_int")
    print("Get Info2:", response)


def studentCodeMainCount_setup():
    pass


def studentCodeMainCount_main():
    print(Robot._get_sm_value("runtime_meta", "studentCode_main_count"))


def createKey_setup():
    Robot.create_key("Restarts")
    Robot._set_sm_value(0, "Restarts")
    if Robot._get_sm_value("Restarts") != 0:
        print("Either getValue or setValue is not working correctly")
    pass


def createKey_main():
    Robot.create_key("Restarts")
    if Robot._get_sm_value("Restarts") == 0:
        try:
            print("Making sure setValue can't create new key")
            Robot._set_sm_value(707, "Klefki")
        except StudentAPIKeyError:
            print("Success!")
        else:
            print("ERROR: setValue can create keys :(")

    print("Creating key 'Klefki' and setting to value 707")
    Robot.create_key("Klefki")
    Robot._set_sm_value(707, "Klefki")
    print("Success!")

    print("Creating nested keys")
    Robot.create_key("Mankey", "EVOLUTION")
    Robot._set_sm_value("Primeape", "Mankey", "EVOLUTION")
    print("Success!")
    restarts = Robot._get_sm_value("Restarts")
    Robot._set_sm_value(restarts + 1, "Restarts")


def timestamp_setup():
    pass


def timestamp_main():
    path = ["dict1", "inner_dict_1_string"]

    print("Getting timestamp")
    initialTime = Robot.get_timestamp(*path)
    print("Success!")

    print("Setting timestamp")
    Robot._set_sm_value("bye", *path)
    print("Success!")

    print("Getting new timestamp")
    newTime = Robot.get_timestamp(*path)
    if newTime > initialTime and time.time() - newTime < 1:
        print("Success!")
    else:
        print("Timestamp did not update correctly")

    print("Testing nested timestamps")
    if newTime == Robot.get_timestamp(*path[:-1]):
        print("Success!")
    else:
        print("Nested timestamps did not update correctly")


def infiniteSetupLoop_setup():
    print("setup")
    while True:
        time.sleep(.1)


def infiniteSetupLoop_main():
    print("main")


def infiniteMainLoop_setup():
    print("setup")


def infiniteMainLoop_main():
    print("main")
    while True:
        time.sleep(.1)


def optionalhibikeSensorMappings_setup():
    pass


def optionalhibikeSensorMappings_main():
    print(Robot._hibike_get_uid('zero'))
    print(Robot._hibike_get_uid('one'))
    print(Robot._hibike_get_uid('two'))
    print(Robot._hibike_get_uid('three'))


def gamepadGetVal_setup():
    pass


def gamepadGetVal_main():
    print("running test")
    print(Gamepad.get_value("button_a"))
    print(Gamepad.get_value("joystick_left_x"))


def asyncIsRunning_setup():
    pass


def asyncIsRunning_main():
    Robot.run(asyncIsRunningHelper)
    print(Robot.is_running(asyncIsRunningHelper))


async def asyncIsRunningHelper():
    await Actions.sleep(1)


def optionalapiGetVal_setup():
    Robot.create_key("hibike", "devices", 47223664828696452136960, "duty_cycle")
    Robot._set_sm_value(0.5, "hibike", "devices",
                      47223664828696452136960, "duty_cycle")


def optionalapiGetVal_main():
    print(Robot.get_value("motor1", "duty_cycle"))


def optionalTestsDisabled_setup():
    assert False, "This optional test should never be run"


def optionalTestsDisabled_main():
    assert False, "This optional test should never be run"


def optionalTestsWork_setup():
    pass


def optionalTestsWork_main():
    pass


def asyncSleep_setup():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncSleepHelper())


def asyncSleep_main():
    pass


async def asyncSleepHelper():
    sleepTestVal = {'test': False}
    Robot.run(asyncSleepHelper2, sleepTestVal)

    await Actions.sleep(.1)
    print('Testing sleep part 1')
    if sleepTestVal['test']:
        print('Success!')
    else:
        print('Failed to sleep for the correct amount of time')

    await Actions.sleep(.5)
    print('Testing sleep part 2')
    if not sleepTestVal['test']:
        print('Success!')
    else:
        print('Failed to sleep for the correct amount of time')


async def asyncSleepHelper2(sleepTestVal):
    sleepTestVal['test'] = True
    await Actions.sleep(.5)
    sleepTestVal['test'] = False
