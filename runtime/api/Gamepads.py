# ------
# Gamepad.py class.
# Copyright 2015. Pioneers in Engineering
# ------
import memcache

memcache_port = 12357
mc = memcache.Client(['127.0.0.1:%d' % memcache_port]) # connect to memcache

def get_all():
    return mc.get('gamepad')

# An array representing the controls with axes present on the device
# On a standard gamepad, axes[0] is negative left, positive right on one
# axes[1] is negative up, positive down on that same one
# axes[2] is negative left, positive right on another
# axes[3] is negative up, positive down on that same other
 # Takes in gamepad index
def get_joysticks(index):
    return mc.get('gamepad')[index]['axes']


# Refer to https://w3c.github.io/gamepad/#remapping for standard gamepad buttons
# An array of gamepadButton objects representing the buttons present on the device.
# Takes in gamepad index
def get_buttons(index):
    return mc.get('gamepad')[index]['buttons']

def get_is_connected(index):
    return mc.get('gamepad')[index]['connected']


# If the user knows the layout of the device and it corresponds to the Standard Gamepad
# Layout, then the mapping should be set to standard. Otherwise set mapping property to empty string
def get_mapping(index):
    return mc.get('gamepad')[index]['mapping']
