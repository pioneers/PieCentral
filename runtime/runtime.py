import subprocess, multiprocessing
import memcache, ansible
import time
from grizzly import *
from hibike import *
#import deviceContext

name_to_grizzly = {}
name_to_values = {}
addrs = Grizzly.get_all_ids()
#context = deviceContext.DeviceContext()
h = hibike.Hibike()
connectedDevices = h.getEnumeratedDevices()
#context.subToDevices(connectedDevices)
h.subToDevices(connectedDevices)
ansible = ansible.Ansible('dawn')
#dawn_ansible = Ansible('dawn')
#runtime_ansible = Ansible('runtime')
#student_ansible = Ansible('student_code')

robot_status = 0 # a boolean for whether or not the robot is executing code
student_proc, console_proc = None, None
memcache_port = 12357
mc = memcache.Client(['127.0.0.1:%d' % memcache_port]) # connect to memcache

def get_all_data(connectedDevices):
    all_data = {}
    for t in connectedDevices:
        #all_data[t[0]] = context.getData(t[0],"dataUpdate")
        all_data[t[0]] = h.getData(t[0],"dataUpdate")
#    print(all_data)
    return all_data

def init():
    # Brute force to find all 
    for index in range(len(addrs)):
        # default name for motors is motor0, motor1, motor2, etc 
        grizzly_motor = Grizzly(addrs[index])
        grizzly_motor.set_mode(ControlMode.NO_PID, DriveMode.DRIVE_COAST)
        grizzly_motor.limit_acceleration(142)
        grizzly_motor.limit_current(10)
        grizzly_motor.set_target(0)

        #grizzly_ids_to_name[addrs[index]] = 'motor' + str(index)
        name_to_grizzly['motor' + str(index)] = grizzly_motor
        name_to_values['motor' + str(index)] = 0
        #motor['motor' + str(index)] = grizzly_motor.get_target()

    mc.set('motor_values', name_to_values)

# used to non Emergency stop the robot
def clear():
    for index in range(len(addrs)):
        grizzly_motor = Grizzly(addrs[index])
        grizzly_motor.set_target(0)
        name_to_values['motor' + str(index)] = 0

    mc.set('motor_values', name_to_values)

# A process for sending the output of student code to the UI
def log_output(stream):
    for line in stream:
        ansible.send_message('UPDATE_CONSOLE', {
            'console_output': {
                'value': line
            }
        })
        time.sleep(0.5) # need delay to prevent flooding ansible

def msg_handling(msg):
    global robot_status, student_proc, console_proc
    msg_type, content = msg['header']['msg_type'], msg['content']
    if msg_type == 'execute' and not robot_status:
        student_proc = subprocess.Popen(['python', '-u', 'student_code/student_code.py'],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # turns student process stdout into a stream for sending to frontend
        lines_iter = iter(student_proc.stdout.readline, b'')
        # start process for watching for student code output
        console_proc = multiprocessing.Process(target=log_output, args=(lines_iter,))
        console_proc.start()
        init()
        robot_status= 1
    elif msg_type == 'stop' and robot_status:
        student_proc.terminate()
        console_proc.terminate()
        clear()
        robot_status = 0
    elif msg_type == 'gamepad':
        mc.set('gamepad', content)

while True:
    msg = ansible.recv()
    if msg:
        msg_handling(msg)

    # Send whether or not robot is executing code
    ansible.send_message('UPDATE_STATUS', {
        'status': {'value': robot_status}
    })

    # Send battery level
    ansible.send_message('UPDATE_BATTERY', {
        'battery': {
            'value': 100 # TODO: Make this not a lie
        }
    })

    all_sensor_data = get_all_data(connectedDevices)
    # TODO: Don't know if UI is ready to receive this yet
    #ansible.send_message('UPDATE_SENSOR', {
    #    'sensor': {'value': all_sensor_data }
    #})

    # TODO: Handle updating readings from Hibike, motor updates, etc
    mc.set('sensor_values', all_sensor_data)
    # This could cause problems, esp with latency
    # but since grizzlies are going to be integrated with hibike, 
    # we may as well run everything from the main process anyway
    name_to_value = mc.get('motor_values')
    for name in name_to_value:
        grizzly = name_to_grizzly[name]
        grizzly.set_target(name_to_value[name])

    # TODO: Don't know if UI is ready to receive this yet
    #ansible.send_message('UPDATE_MOTORS', {
    #    'motors': {'value': name_to_value}
    #})
    time.sleep(0.05)


    #command = dawn_ansible.recv() 
    #if command:
    #    print("Message received from ansible! " + command['header']['msg_type'])
    #    msg_type, content = command['header']['msg_type'], command['content']
    #    if msg_type == 'execute':
    #    print("Ansible said to start the code")
    #        if not running_code:
    #            p = subprocess.Popen(['python', 'student_code/student_code.py'])
    #            with pobslock:
    #                pobs.add(p)
    #            #makes a deamon thread to supervise the process
    #            #t = threading.Thread(target=p_watch, args=(p,))
    #            #t.daemon = True
    #            #t.start()
    #            running_code = True
    #    elif msg_type == 'stop':
    #    print("Ansible said to stop the code")
    #        if running_code:
    #            with pobslock:
    #                print("killed")
    #                for p in pobs: 
    #                    p.terminate() #ideal way to shut down
    #                    #p.kill()
    #                pobs.clear()
    #                #for p in pobs: p.kill() #brut force stuck processes
    #            #kill all motor values
    #            for addr in Grizzly.get_all_ids():
    ##                Grizzly(addr).set_target(0)
    #            running_code = False
    #    elif msg_type == 'gamepad':
    #        runtime_ansible.send(command)

#connectedDevices = h.getEnumeratedDevices() #get list of devices
#h.subscribeToDevices(connectedDevices)
#while True:
#    command = student_ansible.recv()
#    if command:
#         msg_type, content = command['header']['msg_type'], command['content']
#         if msg_type == "sensor_value":
#            runtime_ansible.sendMessage("sensor_value",h.getData(content)) 

