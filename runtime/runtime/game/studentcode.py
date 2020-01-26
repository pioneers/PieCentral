import time

# while True:
#     print('You cannot import me')
#     time.sleep(1)

async def autonomous_actions(n=100):
    print('Running autonomous action ...')
    for i in range(n):
        print(f'Doing action computation ({i+1}/{n}) ...')
        await Actions.sleep(0.5)

def autonomous_setup():
    print('Autonomous setup has begun!')
    Robot.run(autonomous_actions)

def autonomous_main():
    print('Running autonomous main ...')
    # start = time.time()
    # print('I wrote an infinite loop')
    # while True:
    #     print(f'Teleop main has been running for {round(time.time() - start, 3)}s')
    #     time.sleep(0.1)
    #
    x()
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
    print('joystick_left_x -> ', Gamepad.get_value('joystick_left_x'))
    print('joystick_right_y -> ', Gamepad.get_value('joystick_right_y'))

def double(x):
    return 2*x
