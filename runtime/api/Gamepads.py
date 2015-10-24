# ------
# Gamepad.py class. 
# Copyright 2015. Pioneers in Engineering
# ------
import ansible
import time, threading

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
    gpads[index]['axes']


# Refer to https://w3c.github.io/gamepad/#remapping for standard gamepad buttons
# An array of gamepadButton objects representing the buttons present on the device.
# Takes in gamepad index
def get_buttons(index):
    gpads[index]['buttons']

def get_is_connected(index):
    gpads[index]['connected']


# If the user knows the layout of the device and it corresponds to the Standard Gamepad
# Layout, then the mapping should be set to standard. Otherwise set mapping property to empty string  
def get_mapping(index):
    gpads[index]['mapping']

# Array of Gamepad objects
gpads = []

def update():
    command = ansible.recv()
    if command:
        header = command['header']
        content = command['content']
        if header['msg_type'] == 'gamepad' and content:
            gamepads = content

    for index in range(len(gamepads)):
        try:
            gpads[index] = gamepads[index]
        except:
            gpads.append(gamepads[index])

    threading.Timer(0.02, update).start()   
