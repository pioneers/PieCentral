import ansible
import time
import random

while True:
    time.sleep(0.5)

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
            'value': random.randint(0,1)
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
