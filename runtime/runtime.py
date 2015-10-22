import subprocess, signal, sys
import ansible
import threading
import time
#import student_code.student_code as StudentCode
import grizzly
#from api import Robot

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

runningCode = False


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
    command = ansible.recv() 
    if command:
        print("recv msg from ansible")
        msg_type, content = command['header']['msg_type'], command['content']
        if msg_type == 'execute':
            print("exec")
            if not runningCode:
                p = subprocess.Popen('student_code/student_code.py') #may need to change python version
                with pobslock:
                    pobs.add(p)
                #makes a deamon thread to supervise the process
                t = threading.Thread(target=p_watch, args=(p))
                t.daemon=True
                t.start()
                runningCode = True
        elif msg_type == 'stop':
            print("STAPH")
            if runningCode:
                with pobslock:
                    print 'killed'
                    for p in pobs: p.kill()
                #kill all motor values 
                runningCode = False
