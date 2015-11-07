# ------
# Gamepad.py class. 
# Copyright 2015. Pioneers in Engineering
# ------
from ansible import Ansible
import time, threading

student_ansible = Ansible('student_code')

def get_all():
    update()
    return gpads

            
# An array representing the controls with axes present on the device 
# On a standard gamepad, axes[0] is negative left, positive right on one 
# axes[1] is negative up, positive down on that same one
# axes[2] is negative left, positive right on another
# axes[3] is negative up, positive down on that same other
 # Takes in gamepad index
def get_joysticks(index):
   return gpads[index]['axes']

# Refer to https://w3c.github.io/gamepad/#remapping for standard gamepad buttons
# An array of gamepadButton objects representing the buttons present on the device.
# Takes in gamepad index
def get_buttons(index):
    return gpads[index]['buttons']

def get_is_connected(index):
    return gpads[index]['connected']


# If the user knows the layout of the device and it corresponds to the Standard Gamepad
# Layout, then the mapping should be set to standard. Otherwise set mapping property to empty string  
def get_mapping(index):
    return gpads[index]['mapping']

# Array of Gamepad objects
gpads = [{'axes':[0.0, 0.0, 0.0, 0.0], 'buttons':[0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00], 'mapping':'standard'}]


def update():
    command = student_ansible.recv()
    print(str(command) + ' revieced from runtime')
    gamepads = {}
    if command:
        print(command)
        header = command['header']
        content = command['content']
        if header['msg_type'] == 'gamepad' and content:
            gamepads = content
    print('this is the gamepad')
    print(gamepads)
    for index in range(len(gamepads)):
        try:
            gpads[index] = gamepads[str(index)]
        except:
            gpads.append(gamepads[str(index)])

