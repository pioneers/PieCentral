import ansible
import time
import random

while True:
    time.sleep(0.5)

    ansible.send_message('UPDATE_PERIPHERAL', {
        'peripheral': {
            'id': 1234,
            'peripheralType': 'SENSOR_SCALAR',
            'value': random.randint(0, 100)
        }
    })
