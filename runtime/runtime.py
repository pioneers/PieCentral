import ansible
import threading
import time
import student_code.student_code as StudentCode
# import hibike.hibike as sensors
from api import Robot
from api import Gamepads

def execute_student_code(stop_event):
    reload(StudentCode)
    StudentCode.teleop(stop_event)

def get_peripherals():
    while True:
        peripherals = {}
        peripherals['rightLineSensor'] = sensors.getRightLineSensorReading()
        peripherals['leftLineSensor'] = sensors.getLeftLineSensorReading()
        peripheral_readings = ansible.AMessage(
                'peripherals', peripherals)
        ansible.send(peripheral_readings)
        time.sleep(0.05)

peripheral_thread = threading.Thread(target=get_peripherals)
peripheral_thread.daemon = True
peripheral_thread.start()

runningCode = False
while True:
    command = ansible.recv() 
    if command:
        msg_type, content = command['header']['msg_type'], command['content']
        if msg_type == 'code':
            studentCode = open('student_code/student_code.py','w')
            studentCode.write(content)
            studentCode.close()
        elif msg_type == 'execute':
            if not runningCode:
                stop_event = threading.Event()
                student_code_t = threading.Thread(
                        target=execute_student_code,
                        args=( stop_event, ))
                student_code_t.start()
                runningCode = True
        elif msg_type == 'stop':
            if runningCode:
                stop_event.set()
                runningCode = False
        elif msg_type == 'sendCode':
            studentCode = open('student_code/student_code.py','r')
            ansible.send(ansible.AMessage('code', studentCode.read()))
