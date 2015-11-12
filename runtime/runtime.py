import subprocess, signal, sys
from ansible import Ansible
import threading
import time
from grizzly import *
import hibike
#from api import Robot
#from api import Gamepads

h = hibike.Hibike()
dawn_ansible = Ansible('dawn')
runtime_ansible = Ansible('runtime')
student_ansible = Ansible('student_code')

#Robot.init()

#def get_peripherals():
#    while True:
#        peripherals = {}
#        peripherals['rightLineSensor'] = sensors.getRightLineSensorReading()
#        peripherals['leftLineSensor'] = sensors.getLeftLineSensorReading()
#        peripheral_readings = ansible.AMessage(
#                'peripherals', peripherals)
#        ansible.send(peripheral_readings)
#        time.sleep(0.05)

#peripheral_thread = threading.Thread(target=get_peripherals)
#peripheral_thread.daemon = True
#peripheral_thread.start()

running_code = False


pobs = set() # set of all active processes
pobslock = threading.Lock()  # Ensures that only one processs modifies pobs at a time

def numpobs():
    with pobslock:
        return len(pobs)

#signal handlers
def sigterm_handler(signal, fram):
    with pobslock:
        for p in pobs: p,kill()

def sigint_handler(signal, fram):
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)
signal.signal(signal.SIGTERM, sigterm_handler)


#function to watch processes
def p_watch(p):
    with pobslock:
        pobs.remove(p)


while True:
    command = dawn_ansible.recv() 
    if command:
        print("Message received from ansible! " + command['header']['msg_type'])
        msg_type, content = command['header']['msg_type'], command['content']
        if msg_type == 'execute':
	    print("Ansible said to start the code")
            if not running_code:
                p = subprocess.Popen(['python', 'student_code/student_code.py'])
                with pobslock:
                    pobs.add(p)
                #makes a deamon thread to supervise the process
                t = threading.Thread(target=p_watch, args=(p))
                t.daemon = True
                t.start()
                running_code = True
        elif msg_type == 'stop':
	    print("Ansible said to stop the code")
            if running_code:
                with pobslock:
                    print("killed")
                    for p in pobs: p.terminate() #ideal way to shut down
                    for p in pobs: p.kill() #brut force stuck processes
                #kill all motor values
                for addr in Grizzly.get_all_ids():
                    Grizzly(addr).set_target(0)
                running_code = False
        elif msg_type == 'gamepad':
            runtime_ansible.send(command)

connectedDevices = h.getEnumeratedDevices() #get list of devices
h.subscribeToDevices(connectedDevices)
while True:
    command = student_ansible.recv()
    if command:
         msg_type, content = command['header']['msg_type'], command['content']
         if msg_type == "sensor_value":
            runtime_ansible.sendMessage("sensor_value",h.getData(content)) 
