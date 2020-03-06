import time

RFID = '51975776734790250051004'
MOTOR = '56689544289225244464409'

# while True:
#     print('You cannot import me')
#     time.sleep(1)


async def autonomous_actions(n=1000):
    print('Running autonomous action ...')
    for i in range(n):
        print(f'Doing action computation ({i+1}/{n}) ...')
        await Actions.sleep(0.5)


async def set_motor():
    Robot.set_value(MOTOR, 'duty_cycle', 0.2)
    await Actions.sleep(2)
    Robot.set_value(MOTOR, 'duty_cycle', 0)


def autonomous_setup():
    print('Autonomous setup has begun!')
    # Robot.run(autonomous_actions)
    # Robot.run(set_motor)

def autonomous_main():
    Robot.set_value(MOTOR, 'duty_cycle', 0.2)
    print(Robot.get_value(MOTOR, 'duty_cycle'))

    # print('Running autonomous main ...')
    # start = time.time()
    # print('I wrote an infinite loop')
    # while True:
    #     print(f'Teleop main has been running for {round(time.time() - start, 3)}s')
    #     time.sleep(0.1)
    #
    # x()
    #
    # Robot.run(autonomous_actions)


def teleop_setup():
    print('Teleop setup has begun!')


def teleop_main():
    # print('Running teleop main ...')
    # print(Gamepad.get_value('a'))
    # print('A -> ', Gamepad.get_value('button_a'))
    # print('B -> ', Gamepad.get_value('button_b'))
    # print('X -> ', Gamepad.get_value('button_x'))
    # print('Y -> ', Gamepad.get_value('button_y'))
    # print('Xbox -> ', Gamepad.get_value('button_xbox'))
    # print('Dpad up -> ', Gamepad.get_value('dpad_up'))
    # print('joystick_left_x -> ', Gamepad.get_value('joystick_left_x'))
    # print('joystick_right_y -> ', Gamepad.get_value('joystick_right_y'))

    # print('=>', Robot.get_value('my_rfid', 'id'), Robot.get_value('my_rfid2', 'tag_detect'))
    if Gamepad.get_value('button_a'):
        print('Running motor ...')
        Robot.set_value(MOTOR, 'duty_cycle', 1)

# Times out
# def autonomous_main():
#     print('Running autonomous main ...')
#     autonomous_main()


def double(x):
    return 2 * x
