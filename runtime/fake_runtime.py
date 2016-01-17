import ansible
import time
import random
import subprocess, multiprocessing
import memcache
from datetime import datetime
import eventlet
eventlet.monkey_patch()

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
    ansible.send_message('UPDATE_PERIPHERAL', {
        'peripheral': {
            'name': 'somethingElse',
            'peripheralType': 'SENSOR_SCALAR',
            'value': random.randint(0, 100),
            'id': 1236
        }
    })
    ansible.send_message('UPDATE_BATTERY', {
        'battery': {
            'value': random.randint(0,100)
        }
    })
    ansible.send_message('UPDATE_STATUS', {
        'status': {
            'value': robotStatus
        }
    })
    ansible.send_message('UPDATE_PERIPHERAL', {
        'peripheral': {
            'name': 'myMotor',
            'peripheralType': 'MOTOR_SCALAR',
            'value': random.randint(0, 100),
            'id': 1234
        }
    })
    ansible.send_message('UPDATE_PERIPHERAL', {
        'peripheral': {
            'name': 'something',
            'peripheralType': 'SENSOR_BOOLEAN',
            'value': random.randint(0, 1),
            'id': 1235
        }
    })
    time.sleep(0.5)
