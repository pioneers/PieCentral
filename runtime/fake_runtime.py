import ansible
import time
import random
import subprocess, multiprocessing
import memcache
from datetime import datetime
from base64 import b64decode

memcache_port = 12357
mc = memcache.Client(['127.0.0.1:%d' % memcache_port]) # connect to memcache

def log_output(stream):
    for line in stream:
        ansible.send_message('UPDATE_CONSOLE', {
            'console_output': {
                'value': line
            }
        })
        time.sleep(0.05) # don't want to flood ansible

robotStatus = 0
batteryLevel = 100
id_to_name = { '1236': 'somethingElse', '1234': 'myMotor', '1235': 'something'}
while True:
    mc.set('gamepad', {'time': datetime.now()}) # sending arbitary data to API
    msg = ansible.recv()
    if msg:
        msg_type = msg['header']['msg_type']
        if msg_type == 'execute' and not robotStatus:
            with open('student_code.py', 'w+') as f:
                f.write(msg['content']['code'])
            student_proc = subprocess.Popen(['python', '-u', 'student_code.py'],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            lines_iter = iter(student_proc.stdout.readline, b'')
            console_proc = multiprocessing.Process(target=log_output, args=(lines_iter,))
            console_proc.start()
            robotStatus = 1
            print 'Running student code'
        elif msg_type == 'stop' and robotStatus:
            student_proc.terminate()
            console_proc.terminate()
            robotStatus = 0
            print 'Stopping student code'
        elif msg_type == 'custom_names':
            sensor_id = msg['content']['id']
            id_to_name[sensor_id] = msg['content']['name']
        elif msg_type == 'update':
            print msg['content']['update_path']
            print msg['content']['signature_path']

    ansible.send_message('UPDATE_PERIPHERAL', {
        'peripheral': {
            'name': id_to_name['1236'],
            'peripheralType': 'SENSOR_SCALAR',
            'value': random.randint(0, 100),
            'id': '1236'
        }
    })
    ansible.send_message('UPDATE_BATTERY', {
        'battery': {
            'value': batteryLevel
        }
    })
    ansible.send_message('UPDATE_STATUS', {
        'status': {
            'value': robotStatus
        }
    })
    ansible.send_message('UPDATE_PERIPHERAL', {
        'peripheral': {
            'name':id_to_name['1234'],
            'peripheralType': 'MOTOR_SCALAR',
            'value': random.randint(-100, 100),
            'id': '1234'
        }
    })
    ansible.send_message('UPDATE_PERIPHERAL', {
        'peripheral': {
            'name': id_to_name['1235'],
            'peripheralType': 'LimitSwitch',
            'value': random.randint(0, 1),
            'id': '1235'
        }
    })
    batteryLevel -= 1
    if batteryLevel == 0:
        batteryLevel = 100
        ansible.send_message('ADD_ALERT', {
            'payload': {
                'heading': 'Error',
                'message': 'Robot battery level crucial!'
                }
            })
    time.sleep(0.5)
