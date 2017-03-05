import time
import asyncio
from runtimeUtil import *

def autonomous_setup():
  pass

def autonomous_main():
  pass

def teleop_setup():
  uids = Robot._getAllUIDs()
  motors = [uid for uid in uids if SENSOR_TYPE[uid >> 72] == "YogiBear"]
  for uid in motors:
    Robot._hibikeSubscribeDevice(uid, 40, ["enable", "duty_cycle", "enc_pos", "enc_pos", "env_vel", "motor_current"])
  time.sleep(.5)
  Robot.motors = motors
  print("motors: ", motors)
  Robot.currTime = time.time()

def teleop_main():
  Robot.state = StudentApi._getSMValue("hibike", "devices")
  currTime = time.time()
  print("main loop ms period: ", int((currTime - Robot.currTime) * 1000))
  Robot.currTime = currTime
  if len(Robot.motors) >= 2:
    Robot.set_value(Robot.motors[0], "duty_cycle", Gamepad.get_value("joystick_left_y"))
    Robot.set_value(Robot.motors[1], "duty_cycle", -1*Gamepad.get_value("joystick_right_y"))
  else:
    for uid in Robot.motors:
      Robot.set_value(uid, "duty_cycle", Gamepad.get_value("joystick_left_y"))
  for _ in range(20):
    x = Robot.state[Robot.motors[0]][0]["enc_pos"][0]

def setup():
  pass

def main():
  pass

def asyncawait_setup():
  Robot.createKey("right")
  Robot.createKey("counter")
  Robot._setSMValue(3.0, "right")
  Robot._setSMValue(0.0, "counter")
  Robot.run(asyncawait_helper)

def asyncawait_main():
  Robot._setSMValue(Robot._getSMValue("counter") + 1, "counter")
  if Robot._getSMValue("right") == 4 and Robot._getSMValue("counter") == 3:
    print("Async Success")

async def asyncawait_helper():
  Robot._setSMValue(Robot._getSMValue("right") + 1, "right")

def test0_setup():
  print("test0_setup")

def test0_main():
  print("test0_main")

def mainTest_setup():
  pass

def mainTest_main():
  response = Robot._getSMValue("incrementer")
  print("Get Info:", response)
  response -= 1

  Robot._setSMValue(response, "incrementer")

  print("Saying hello to the other side")
  print("DAT:", 1.0/response)

def nestedDict_setup():
  pass

def nestedDict_main():
  print("CODE LOOP")
  response = Robot._getSMValue("dict1", "inner_dict1_int")
  print("Get Info:", response)

  response = 1
  Robot._setSMValue(response, "dict1", "inner_dict1_int")
  response = Robot._getSMValue("dict1", "inner_dict1_int")
  print("Get Info2:", response)

def studentCodeMainCount_setup():
  pass

def studentCodeMainCount_main():
  print(Robot._getSMValue("runtime_meta", "studentCode_main_count"))

def createKey_setup():
  Robot.createKey("Restarts")
  Robot._setSMValue(0, "Restarts")
  if Robot._getSMValue("Restarts") != 0:
    print("Either getValue or setValue is not working correctly")
  pass

def createKey_main():
  Robot.createKey("Restarts")
  if Robot._getSMValue("Restarts") == 0:
    try:
      print("Making sure setValue can't create new key")
      Robot._setSMValue(707, "Klefki")
    except StudentAPIKeyError:
      print("Success!")
    else:
      print("ERROR: setValue can create keys :(")

  print("Creating key 'Klefki' and setting to value 707")
  Robot.createKey("Klefki")
  Robot._setSMValue(707, "Klefki")
  print("Success!")

  print("Creating nested keys")
  Robot.createKey("Mankey", "EVOLUTION")
  Robot._setSMValue("Primeape", "Mankey", "EVOLUTION")
  print("Success!")
  restarts = Robot._getSMValue("Restarts")
  Robot._setSMValue(restarts+1, "Restarts")

def timestamp_setup():
  pass

def timestamp_main():
  path = ["dict1", "inner_dict_1_string"]

  print("Getting timestamp")
  initialTime = Robot.getTimestamp(*path)
  print("Success!")

  print("Setting timestamp")
  Robot._setSMValue("bye", *path)
  print("Success!")

  print("Getting new timestamp")
  newTime = Robot.getTimestamp(*path)
  if newTime > initialTime and time.time() - newTime < 1:
    print("Success!")
  else:
    print("Timestamp did not update correctly")

  print("Testing nested timestamps")
  if newTime == Robot.getTimestamp(*path[:-1]):
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

def emergencyStop_setup():
  print("E-Stop setup")

def emergencyStop_main():
  response = Robot._getSMValue("incrementer") - 1
  if response < 0:
    Robot.emergencyStop()

  Robot._setSMValue(response, "incrementer")
  print("HIBIKE LOOP")

def hibikeSensorMappings_setup():
  pass

def hibikeSensorMappings_main():
  print(Robot._hibikeGetUID('zero'))
  print(Robot._hibikeGetUID('one'))
  print(Robot._hibikeGetUID('two'))
  print(Robot._hibikeGetUID('three'))

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
  
def apiGetVal_setup():
  Robot.createKey("hibike", "devices", 47223664828696452136960, "duty_cycle")
  Robot._setSMValue(0.5, "hibike", "devices", 47223664828696452136960, "duty_cycle")

def apiGetVal_main():
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
