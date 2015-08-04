# ------
# Gamepad.py class. 
# Copyright 2015. Pioneers in Engineering
# ------
import ansible
import time, threading

class Gamepad:
    
    # Constructor instantiates a gamepad received from ansible
    def __init__(self, gpad):
        self.gamepad = gpad

    def update(self, gpad):
        self.gamepad = gpad

    # Refer to https://w3c.github.io/gamepad/#remapping for standard gamepad buttons
    # An array of gamepadButton objects representing the buttons present on the device.
    def buttons(self):
        return self.gamepad['buttons']
            
    # An array representing the controls with axes present on the device 
    # On a standard gamepad, axes[0] is negative left, positive right on one 
    # axes[1] is negative up, positive down on that same one
    # axes[2] is negative left, positive right on another
    # axes[3] is negative up, positive down on that same other
    def axes(self):
        return self.gamepad['axes']

    def isConnected(self):
        return self.gamepad['connected']

    # If the user knows the layout of the device and it corresponds to the Standard Gamepad
    # Layout, then the mapping should be set to standard. Otherwise set mapping property to emp    # ty string 
    def mapping(self):
        return self.gamepad['mapping']

# Array of Gamepad objects
gpads = None

# Returns array of Gamepad objects
def get_gamepads():
    update()
    return gpads

def update():
    command = ansible.recv()
    if command:
        header = command['header']
        content = command['content']
        if header['msg_type'] == 'gamepad' and content:
            gamepads = content

    for index in range(len(gamepads)):
        try:
            gpads[index].update(gamepads[index])
        except:
            gpads.append(Gamepad(gamepads[index]))

    threading.Timer(0.02, update).start()     

