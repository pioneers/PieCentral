"""                                                                                                         
This program creates a virtual hibike device for testing purposes                                     
                                                                                                            
usage:                                                                                                      
$ socat -d -d pty,raw,echo=0 pty,raw,echo=0                                                                 
2016/09/20 21:29:03 socat[4165] N PTY is /dev/pts/26                                                        
2016/09/20 21:29:03 socat[4165] N PTY is /dev/pts/27                                                        
2016/09/20 21:29:03 socat[4165] N starting data transfer loop with FDs [3,3] and [5,5]                      
$ python3.5 virtual_device.py -d LimitSwitch -p /dev/pts/26                                                 
"""

import struct
import serial
import hibike_message as hm
import sys
import random
import time
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--device', required=True, help='device type')
parser.add_argument('-p', '--port', required=True, help='serial port')
args = parser.parse_args()

device = args.device
port = args.port
print(device, port)
conn = serial.Serial(port, 115200)

for device_num in hm.devices:
    if hm.devices[device_num]["name"] == device:
        device_id = device_num
        break
else:
    raise RuntimeError("Invalid Device Name!!!")

year = 1
id = random.randint(0, 0xFFFFFFFFFFFFFFFF)
delay = 0
updateTime = 0
uid = (device_id << 72) | (year << 64) | id

# Here, the parameters and values to be sent in device datas are set for each device type, the list of subscribed parameters is set to empty,
if device == "LimitSwitch":
    subscribed_params = []
    params_and_values = [("switch0", True), ("switch1", True), ("switch2", False), ("switch3", False)]
if device == "ServoControl":
    subscribed_params = []
    params_and_values = [("servo0", 2), ("enable0", True), ("servo1", 0), ("enable1", True), ("servo2", 5), ("enable2", True), ("servo3", 3), ("enable3", False)]
if device == "Potentiometer":
    subscribed_params = []
    params_and_values = [("pot0", 6.7), ("pot1", 5.5), ("pot2", 34.1), ("pot3", 0.15)]
if device == "YogiBear":
    subscribed_params = []
    params_and_values = [("duty", 20), ("forward", False)]
        
while (True):
    if (updateTime != 0 and delay != 0):
        if((time.time() - updateTime) >= (delay * 0.001)):
#If the time equal to the delay has elapsed since the previous device data, send a device data with the device id and the device's subscribed params and values
            data = [data_tuple for data_tuple in params_and_values if data_tuple[0] in subscribed_params]
            hm.send(conn, hm.make_device_data(device_id, data))
            updateTime = time.time()
            print("Regular data update sent from %s" % device)
             
    msg = hm.read(conn)
    if not msg:
        time.sleep(.005)
        continue
    if msg.getmessageID() in [hm.messageTypes["SubscriptionRequest"]]:
#Update the delay, subscription time, and params, then send a subscription response
        print("Subscription request recieved")
        params, delay = struct.unpack("<HH", msg.getPayload())
             
        subscribed_params = hm.decode_params(device_id, params)
        hm.send(conn, hm.make_subscription_response(device_id, subscribed_params, delay, uid))
        updateTime = time.time()
    if msg.getmessageID() in [hm.messageTypes["Ping"]]: # Send a subscription response 
             print ("Ping recieved")
             hm.send(conn, hm.make_subscription_response(device_id, subscribed_params, delay, uid))
    if msg.getmessageID() in [hm.messageTypes["DeviceRead"]]:
# Send a device data with the requested param and value tuples
        print("Device read recieved")
        params = struct.unpack("<H", msg.getPayload())
        read_params = hm.decode_params(device_id, params)
        read_data = 0
          
        for data_tuple in params_and_values:
            if data_tuple[0] in read_params:
                if not hm.paramMap[device_id][data_tuple[0]][2]:# Raise a syntax error if one of the values to be read is not readable
                        raise SyntaxError("Attempted to read an unreadable value")
                read_data.append(data_tuple)
        hm.send(conn, hm.make_device_data(device_id, read_data))
           
    if msg.getmessageID() in [hm.messageTypes["DeviceWrite"]]:
# Write to requested parameters and return the values of the parameters written to using a device data
        print("Device write recieved")
        write_params_and_values = hm.decode_device_write(msg, device_id)
        write_params = [param_val[0] for param_val in write_params_and_values]
        value_types = [hm.paramMap[device_id][name][1] for name in write_params]
                
        write_tuples = [(write_params[index], write_params_and_values[index][1]) for index in range(len(write_params))]
        for new_tuple in write_tuples:
            if not hm.paramMap[device_id][new_tuple[0]][3]: # Raise a syntax error if the value that the message attempted to write to is not writable
                raise SyntaxError("Attempted to write to an unwritable value")
            params_and_values[hm.paramMap[device_id][new_tuple[0]][0]] = new_tuple

        # Send the written data, make sure you only send data for readable parameters
        index = 0 
        while index < len(write_params):
            if hm.paramMap[device_id][write_tuples[index][0]][2]:
                index += 1
            else:
                del write_tuples[index]
        hm.send(conn, hm.make_device_data(device_id, write_tuples))
           
                
