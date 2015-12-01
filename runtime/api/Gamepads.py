# ------
# Gamepad.py class.
# Copyright 2015. Pioneers in Engineering
# ------
import memcache

# Connect to memcache
memcache_port = 12357
mc = memcache.Client(['127.0.0.1:%d' % memcache_port])

def get_all():
    """Returns a list a list of values for every gamepad connected.

    :returns: A list of axes and button data for each connected gamepad

    :Examples:

    >>> gpads = Gamepads.get_all()
    >>> gamepad0 = gpads[0]
    """
    return mc.get('gamepad')

# An array representing the controls with axes present on the device
# On a standard gamepad, axes[0] is negative left, positive right on one
# axes[1] is negative up, positive down on that same one
# axes[2] is negative left, positive right on another
# axes[3] is negative up, positive down on that same other
 # Takes in gamepad index
def get_joysticks(index):
    """Returns a list of axes values corresponding to the specified gamepad.

    :param index: The index of the gamepad, usually 0, 1, 2, or 3
    :returns: A list of 4 decimal values, each corresponding to a joystick axis.

    :Examples:

    >>> axes = Gamepads.get_joysticks(0)
    """
    return mc.get('gamepad')[index]['axes']

# Refer to https://w3c.github.io/gamepad/#remapping for standard gamepad buttons
# An array of gamepadButton objects representing the buttons present on the device.
# Takes in gamepad index
def get_buttons(index):
    """Returns a list of button values corresponding to the specified gamepad.

    :param index: The index of the gamepad, usually 0, 1, 2, or 3
    :returns: A list of 0's and 1's, each corresponding to a button
    """
    return mc.get('gamepad')[index]['buttons']

def get_is_connected(index):
    """Returns whether or not the specified gamepad is connected.

    :param index: The index of the gamepad, usually 0, 1, 2, or 3
    :returns: A boolean value for whether or not that gamepad is connected
    """
    return mc.get('gamepad')[index]['connected']


# If the user knows the layout of the device and it corresponds to the Standard Gamepad
# Layout, then the mapping should be set to standard. Otherwise set mapping property to empty string
def get_mapping(index):
    """Returns the mapping of the specified gamepad.
    """
    return mc.get('gamepad')[index]['mapping']

