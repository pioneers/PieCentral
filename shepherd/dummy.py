import time
import queue
import json
import LCM

q = queue.Queue()
q2 = queue.Queue()

LCM.lcm_start_read('Channel', q, True)

# testing LCMClass.send_message
LCM.lcm_send('Channel', 'header', {'b1#': 4, 'goal': 'goal7vars'})
LCM.lcm_send('Channel', 'header1', {'codes': [323, 5, 2]})
LCM.lcm_send('Channel', 'header2', {'multiplier': 87.87, 'bid': 19009})
# LCM.lcm_send('Channel', 'header3', 'testing_delay', 1)

while True:
    item = q.get()
    # item2 = q2.get()
    if item is None:
        pass
    else:
        print(json.loads(item))
        print(item)
        time.sleep(1)
