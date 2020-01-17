import time

# while True:
#     print('You cannot import me')
#     time.sleep(1)

async def autonomous_actions():
    print('Running autonomous action ...')
    for i in range(10):
        print(f'Doing action computation ({i+1}/10) ...')
        await Actions.sleep(0.5)

def autonomous_setup():
    print('Autonomous setup has begun!')
    Robot.run(autonomous_actions)

def autonomous_main():
    print('Running autonomous main ...')
    # x()
    # Robot.run(autonomous_actions)

def teleop_setup():
    print('Teleop setup has begun!')

def teleop_main():
    print('Running teleop main ...')
    start = time.time()
    print('I wrote an infinite loop')
    while True:
        print(f'Teleop main has been running for {round(time.time() - start, 3)}s')
        time.sleep(0.1)
