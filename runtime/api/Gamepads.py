# ------
# Gamepad.py class.
# Copyright 2015. Pioneers in Engineering
# ------
'''
This module contains functions for getting gamepad data.

To use this module, you must first import it:

>>> from api import Gamepads
'''
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

def get_joysticks(index):
    """Returns a list of axes values corresponding to the specified gamepad.

    Each returned value is between -1 and 1, which represents where the joystick
    is along that axis. For example, if axes[0] is -1, then the left joystick
    has been pushed all the way to the left. In order to get a better sense of
    the joystick mappings, click the 'Details' button next to a gamepad in Dawn
    or refer to https://w3c.github.io/gamepad/#remapping.

    On a standard gamepad:
    - axes[0] represents the horizontal axis of the left joystick.
    - axes[1] represents the vertical axis of the left joystick
    - axes[2] represents the horizontal axis of the right joystick
    - axes[3] represent the vertical axis of the right joystick

    :param index: The index of the gamepad, usually 0, 1, 2, or 3
    :returns: A list of 4 decimal values, each corresponding to a joystick axis.

    :Examples:

    >>> axes = Gamepads.get_joysticks(0)
    """
    return mc.get('gamepad')[index]['axes']

def get_buttons(index):
    """Returns a list of button values corresponding to the specified gamepad.

    Each button value is either a 0 (not pressed) or a 1 (pressed). Unlike
    joysticks, there are no in-between values--it can only be a 0 or a 1. To
    see the exact mapping, click on the 'Details' button next to a gamepad in
    Dawn, or refer to https://w3c.github.io/gamepad/#remapping.

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
    """Returns the mapping of the specified gamepad. Usually this value will be 'standard.'
    """
    return mc.get('gamepad')[index]['mapping']

