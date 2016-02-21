
import subprocess, multiprocessing, time
import memcache, ansible, hibike
from grizzly import *
import usb
import os
from base64 import b64decode

#connect to memcache
memcache_port = 12357
mc = memcache.Client(['127.0.0.1:%d' % memcache_port])
mc.set('gamepad', {'0': {'axes': [0,0,0,0], 'buttons': None, 'connected': None, 'mapping': None}})

# Useful motor mappings
name_to_grizzly, name_to_values, name_to_ids, name_to_modes = {}, {}, {}, {}
student_proc, console_proc = None, None
robot_status = 0 # a boolean for whether or not the robot is executing
battery_UID = 0 #TODO, what if no battery buzzer, what if not safe battery buzzer
battery_safe = False
mc.set('flag_values',[]) #set flag color initial status
mc.set('servo_values',[])
mc.set('PID_constants',[("P", 1), ("I", 0), ("D", 0)])
mc.set('control_mode', ["default", "all"])
mc.set('drive_mode', ["brake", "all"])
mc.set('drive_distance', [])
gear_to_tick = {19: 1200.0/360, 67: 4480/360}
all_modes = {"default": ControlMode.NO_PID, "speed": ControlMode.SPEED_PID, "position": ControlMode.POSITION_PID,
        "brake": DriveMode.DRIVE_BRAKE, "coast": DriveMode.DRIVE_COAST}
PID_constants = {"P": 1, "I": 0, "D": 0}



if 'HIBIKE_SIMULATOR' in os.environ and os.environ['HIBIKE_SIMULATOR'] in ['1', 'True', 'true']:
    import hibike_simulator
    h = hibike_simulator.Hibike()
else:
    h = hibike.Hibike()

connectedDevices = h.getEnumeratedDevices()
uid_to_type = {uid: device_type for (uid, device_type) in connectedDevices}
print connectedDevices
# TODO: delay should not always be 50
h.subToDevices([(device, 50) for (device, device_type) in connectedDevices])

def init_battery():
    global battery_UID
    global battery_safe
    print(connectedDevices)
    for UID, dev in connectedDevices:
        if h.getDeviceName(int(dev)) == "BatteryBuzzer":
            battery_UID = UID
    print(battery_UID)
    if not bool(battery_UID):
        stop_motors()
        ansible.send_message('Add_ALERT', {
        'payload': {
            'heading': "Battery Error",
            'message': "Battery buzzer not connected. Please connect and restart the robot" #TODO Implement On UI Side
            }
	})
        time.sleep(1)
        raise Exception('Battery buzzer not connected')
    print(h.getData(battery_UID,"dataUpdate"))
    battery_safe = bool(h.getData(battery_UID,"dataUpdate")[0][0])

def get_all_data(connectedDevices):
    all_data = {}
    for uid, device_type in connectedDevices:
        if uid == battery_UID: # battery value testing is special-cased
            continue
        tup_nest = h.getData(uid, "dataUpdate")
        if device_type == 9: # XXX
            #just for color sensor, put all data into one list
            all_data["5" + str(t[0])] = h.getData(t[0], "dataUpdate")
        count = 1
        tup_nest = h.getData(t[0], "dataUpdate")
        if not tup_nest:
            continue
        values, timestamps = tup_nest
        for value, device_id in zip(values, uid_to_device_id(uid, len(values))):
            all_data[device_id] = value
    return all_data


def set_flags(values):
    for i in range(1,values.length):
        light = values[i]
        if light != -1:
            if light == 1:
                light = -1
            elif light == 2:
                light = -64
            elif light == 3:
                light = -128
            h.writeValue(int(values[0]), "s" + string(i), light)

def set_servos(values):
    for i in range(0,values.length-1):
        if values[i+1] != -1:
            h.writeValue(int(values[0]),"servo" + string(i), values[i+1])
    mc.set("servo_value",[])

def drive_set_distance(list_tuples):
    for item in list_tuples:
        grizzly = name_to_grizzly[item[0]]
        try:
            grizzly.write_encoder(0)
            grizzly.set_mode(ControlMode.POSITION_PID, DriveMode.DRIVE_BRAKE)
            grizzly.set_target(item[1] * gear_to_tick[item[2]])
            control_mode = mc.get("control_mode")
            set_control_mode(control_mode)
            drive_mode = mc.get("drive_mode")
            set_control_mode(control_mode)
        except:
            stop_motors()

def set_control_mode(mode):
    new_mode = all_modes[mode[0]]
    if mode[1] == "all":
        for motor, old_mode in name_to_modes.items():
            grizzly = name_to_grizzly[motor]
            grizzly.set_mode(new_mode, old_mode[1])
    else:
        grizzly = name_to_grizzly[motor]
        grizzly.set_mode(new_mode, old_mode[1])

def set_drive_mode(mode):
    new_mode = all_modes[mode[0]]
    if mode[1] == "all":
        for motor, old_mode in name_to_modes.items():
            grizzly = name_to_grizzly[motor]
            grizzly.set_mode(old_mode[0], new_mode)
    else:
        grizzly = name_to_grizzly[motor]
        grizzly.set_mode(old_mode[0], new_mode)

def set_PID(constants):
    PID_constants[constants[0]] = constants[1]
    p = PID_constants["P"]
    i = PID_constants["I"]
    d = PID_constants["D"]
    for motor, grizzly in name_to_grizzly.items():
        grizzly.init_pid(p, i, d)

def test_battery():
    if battery_UID not in list(zip(*connectedDevices))[0]:
        print(battery_UID)
        print(list(zip(*connectedDevices))[0])
        stop_motors()
        ansible.send_message('Add_ALERT', {
        'payload': {
            'heading': "Battery Error", # TODO: Make this not a lie
            'message': "Battery buzzer not connected. Please connect and restart the robot" #TODO Implement On UI Side
            }
        })
        time.sleep(1)
        raise Exception('Battery buzzer not connected') #TODO Send to UI
    if not battery_safe:
        stop_motors()
        ansible.send_message('Add_ALERT', {
        'payload': {
            'heading': "Battery Error", # TODO: Make this not a lie
            'message': "Battery level crucial. Reconnect a safe battery and restart the robot" #TODO Implement On UI Side
            }
        })
        time.sleep(1)
        raise Exception('Battery unsafe')
# Called on starte of student code, finds and configures all the connected motors
def initialize_motors():
    try:
        addrs = Grizzly.get_all_ids()
    except usb.USBError:
        print("WARNING: no Grizzly Bear devices found")
        addrs = []

    # Brute force to find all
    for index in range(len(addrs)):
        # default name for motors is motor0, motor1, motor2, getEnumeratedDevices
        grizzly_motor = Grizzly(addrs[index])
        grizzly_motor.set_mode(ControlMode.NO_PID, DriveMode.DRIVE_BRAKE)
        grizzly_motor.set_target(0)
        grizzly_motor._set_as_int(0x80, 500, 2)

        name_to_grizzly['motor' + str(index)] = grizzly_motor
        name_to_values['motor' + str(index)] = 0
        name_to_ids['motor' + str(index)] = addrs[index]
        name_to_modes['motor' + str(index)] = (ControlMode.NO_PID, DriveMode.DRIVE_BRAKE)

    mc.set('motor_values', name_to_values)

# Called on end of student code, sets all motor values to zero
def stop_motors():
    for name, grizzly in name_to_grizzly.iteritems():
        grizzly.set_target(0)
        name_to_values[name] = 0

    mc.set('motor_values', name_to_values)

# A process for sending the output of student code to the UI
def log_output(stream):
    #TODO: figure out a way to limit speed of sending messages, so
    # ansible is not overflowed by printing too fast
    for line in stream:
        ansible.send_message('UPDATE_CONSOLE', {
            'console_output': {
                'value': line
            }
        })

def msg_handling(msg):
    global robot_status, student_proc, console_proc
    msg_type, content = msg['header']['msg_type'], msg['content']
    if msg_type == 'execute' and not robot_status:
        filename = "student_code/student_code.py"
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open('student_code/student_code.py', 'w+') as f:
            f.write(msg['content']['code'])
        student_proc = subprocess.Popen(['python', '-u', 'student_code/student_code.py'],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # turns student process stdout into a stream for sending to frontend
        lines_iter = iter(student_proc.stdout.readline, b'')
        # start process for watching for student code output
        console_proc = multiprocessing.Process(target=log_output, args=(lines_iter,))
        console_proc.start()
        initialize_motors()
        robot_status= 1
    elif msg_type == 'stop' and robot_status:
        student_proc.terminate()
        console_proc.terminate()
        stop_motors()
        robot_status = 0
    elif msg_type == 'update':
        #initiate necessary shutdown procedures
        student_proc.terminate()
        console_proc.terminate()
        stop_motor()
        robot_status = 0

        #remove everything that is like tar currently in the update folder
        os.system('rm -f ~/updates/*tar*')

        update = b64decode(msg['content']['update'])
        signature = b64decode(msg['content']['signature'])
        filename = msg['content']['filename']
        signature_filename = filename + '.asc'
        update_f = open(filename, 'wb')
        update_f.write(bytearray(update))
        update_f.flush()
        update_f.close()
        signature_f = open(signature_filename, 'wb')
        signature_f.write(bytearray(signature))
        signature_f.flush()
        signature_f.close()

        #put signature_f and update_f in ~/updates
        os.system('mv ' + filename + ' ~/updates')
        os.system('mv ' + signature_filename + ' ~/updates')

        #run ./update.sh
        os.system('sh ~/updates/update.sh')

peripheral_data_last_sent = 0
def send_peripheral_data(data):
    global peripheral_data_last_sent
    # TODO: This is a hack. Should put this into a separate process
    if time.time() < peripheral_data_last_sent + 1:
        return
    peripheral_data_last_sent = time.time()

    # Send sensor data
    for device_id, value in data.items():
        ansible.send_message('UPDATE_PERIPHERAL', {
            'peripheral': {
                'name': 'sensor_{}'.format(device_id),
                'peripheralType':h.getDeviceName(uid_to_type[device_id_to_uid(device_id)]),
                'value': value,
                'id': device_id
                }
            })

def uid_to_device_id(uid, num_devices):
    return [str(device_index) + str(uid) for device_index in range(num_devices)]

def device_id_to_uid(device_id):
    return device_id[1:]

init_battery()
while True:
    test_battery()
    try:
        battery_safe = bool(h.getData(battery_UID,"dataUpdate")[0][0])
    except:
        print("Battery Buzzer not Found")
    msg = ansible.recv()
    # Handle any incoming commands from the UI
    if msg:
        msg_handling(msg)

    # Send whether or not robot is executing code
    ansible.send_message('UPDATE_STATUS', {
        'status': {'value': robot_status}
    })

    # Update sensor values, and send to UI
    all_sensor_data = get_all_data(connectedDevices)
    send_peripheral_data(all_sensor_data)
    mc.set('sensor_values', all_sensor_data)

    # Send battery level
    try:
        ansible.send_message('UPDATE_BATTERY', {
            'battery': {
                'value': h.getData(battery_UID,"dataUpdate")[0][5]
        }
    })
    except:
        print("Can't send data")

    #Set Team Flag
    flag_values = mc.get('flag_values')
    if flag_values:
        set_flags(flag_values)

    #Set Servos
    servo_values = mc.get('servo_values')
    if servo_values:
        set_servos(servo_values)

    #Drive distance for grizzlies
    drive_distance = mc.get('drive_distance')
    if drive_distance:
        drive_set_distance(drive_distance)

    #set control mode
    control_mode = mc.get("control_mode")
    if control_mode:
        set_control_mode(control_mode)

    #set drive mode
    drive_mode = mc.get("drive_mode")
    if control_mode:
        set_control_mode(control_mode)

    #rebind PID constants
    PID_rebind= mc.get("PID_constants")
    if PID_rebind:
        set_PID(PID_rebind)

    #refresh PID constants
    mc.set("get_PID", PID_constants)


    # Send motor values to UI, if the robot is running
    if robot_status:
        name_to_value = mc.get('motor_values') or {}
        for name in name_to_value:
            grizzly = name_to_grizzly[name]
            try:
                grizzly.set_target(name_to_value[name])
            except:
                stop_motors()

            ansible.send_message('UPDATE_PERIPHERAL', {
                'peripheral': {
                    'name': name,
                    'peripheralType':'MOTOR_SCALAR',
                    'value': name_to_value[name],
                    'id': name_to_ids[name]
                }
            })

    time.sleep(0.05)
