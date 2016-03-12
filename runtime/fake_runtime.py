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

temporary_send = 20
robotStatus = 0
id_to_name = {'1230': 'MotorA', '1231': 'MotorB', '1232': 'LimitA', '1233': 'LineA', '1234': 'PotentiometerA', '1235': 'EncoderA', 
                '1236': 'ColorThing', '1237': 'MetalDetectorA', '1238': 'ScalarA', '1239': 'ErroredA',
                '1240': 'TempMotor', '1241': 'TempLine'}
while True:
    batteryLevel = random.uniform(0, 12.0)
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
        elif msg_type == 'save' and not robotStatus:
            with open('student_code.py', 'w+') as f:
                f.write(msg['content']['code'])
                f.close()
            robotStatus = 0
            print 'Uploading student code'
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

    if temporary_send > 0:
        ansible.send_message('UPDATE_PERIPHERAL', {
            'peripheral': {
                'name':id_to_name['1240'],
                'peripheralType': 'MOTOR_SCALAR',
                'value': random.uniform(-100, 100),
                'id': '1240'
            }
        })
        ansible.send_message('UPDATE_PERIPHERAL', {
            'peripheral': {
                'name':id_to_name['1241'],
                'peripheralType': 'LineFollower',
                'value': random.uniform(0, 10),
                'id': '1241'
            }
        })
        temporary_send -= 1
    ansible.send_message('UPDATE_PERIPHERAL', {
        'peripheral': {
            'name':id_to_name['1230'],
            'peripheralType': 'MOTOR_SCALAR',
            'value': random.uniform(-100, 100),
            'id': '1230'
        }
    })
    ansible.send_message('UPDATE_PERIPHERAL', {
        'peripheral': {
            'name':id_to_name['1231'],
            'peripheralType': 'MOTOR_SCALAR',
            'value': random.uniform(-100, 100),
            'id': '1231'
        }
    })
    ansible.send_message('UPDATE_PERIPHERAL', {
        'peripheral': {
            'name':id_to_name['1232'],
            'peripheralType': 'LimitSwitch',
            'value': random.randint(0, 1),
            'id': '1232'
        }
    })
    ansible.send_message('UPDATE_PERIPHERAL', {
        'peripheral': {
            'name': id_to_name['1233'],
            'peripheralType': 'LineFollower',
            'value': random.uniform(0, 10),
            'id': '1233'
        }
    })
    ansible.send_message('UPDATE_PERIPHERAL', {
        'peripheral': {
            'name':id_to_name['1234'],
            'peripheralType': 'Potentiometer',
            'value': random.uniform(0, 100),
            'id': '1234'
        }
    })
    ansible.send_message('UPDATE_PERIPHERAL', {
        'peripheral': {
            'name': id_to_name['1235'],
            'peripheralType': 'Encoder',
            'value': random.randint(0, 1000),
            'id': '1235'
       }
    })
    ansible.send_message('UPDATE_PERIPHERAL', {
        'peripheral': {
            'name':id_to_name['1236'],
            'peripheralType': 'ColorSensor',
            'value': [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), random.randint(0, 1), random.randint(0, 360)],
            'id': '1236'
        }
    })
    ansible.send_message('UPDATE_PERIPHERAL', {
        'peripheral': {
            'name':id_to_name['1237'],
            'peripheralType': 'MetalDetector',
            'value': random.uniform(30000, 40000),
            'id': '1237'
        }
    })
    ansible.send_message('UPDATE_PERIPHERAL', {
        'peripheral': {
            'name':id_to_name['1238'],
            'peripheralType': 'SENSOR_SCALAR',
            'value': random.uniform(-100, 100),
            'id': '1238'
        }
    })
    ansible.send_message('UPDATE_PERIPHERAL', {
        'peripheral': {
            'name':id_to_name['1239'],
            'peripheralType': 'Junk',
            'value': random.uniform(-100, 100),
            'id': '1239'
        }
    })

    if batteryLevel == 0:
        batteryLevel = 100
        ansible.send_message('ADD_ALERT', {
            'payload': {
                'heading': 'Error',
                'message': 'Robot battery level crucial!'
                }
            })
    time.sleep(0.5)
