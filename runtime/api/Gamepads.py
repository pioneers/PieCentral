# ------
# Gamepad.py class.
# Copyright 2015. Pioneers in Engineering
# ------
'''
This module contains functions for getting gamepad data.

To use this module, you must first import it:

>>> from api import Gamepads
'''


# Connect to memcache
import memcache
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
    gamepad_index = mc.get("gamepad")[index]
    assert gamepad_index != None, "gamepad index not found"
    return gamepad_index['axes']

def get_axis(index,axis):
    """Returns the position of a specified joystick.

    Each returned value is between -1 and 1, which represents where the joystick
    is along that axis. In order to get a better sense of
    the joystick mappings, click the 'Details' button next to a gamepad in Dawn
    or refer to https://w3c.github.io/gamepad/#remapping.

    On a standard gamepad:
    - Joystick.LEFT_X represents the horizontal axis of the left joystick
    - Joystick.LEFT_Y represents the vertical axis of the left joystick
    - Joystick.RIGHT_X represents the horizontal axis of the right joystick
    - Joystick.RIGHT_Y represent the vertical axis of the right joystick

    :param index: The index of the gamepad, usually 0, 1, 2, or 3
    :param axis: An enum (LEFT_X,LEFT_Y,RIGHT_X,RIGHT_Y) which specifies the axis.
    :returns: A list of 4 decimal values, each corresponding to a joystick axis.

    :Examples:

    >>> axis = Gamepads.get_axis(0,Joystick.LEFT_X)
    """
    gamepad_index = mc.get("gamepad")[str(index)]
    assert gamepad_index != None, "gamepad index not found"
    return gamepad_index['axes'][axis]

def get_all_buttons(index):
    """Returns a list of button values corresponding to the specified gamepad.

    Each button value is either False (not pressed) or True (pressed). Unlike
    joysticks, there are no in-between values--it can only be False or True. To
    see the exact mapping, click on the 'Details' button next to a gamepad in
    Dawn, or refer to https://w3c.github.io/gamepad/#remapping.

    :param index: The index of the gamepad, usually 0, 1, 2, or 3
    :returns: A list of booleans, each corresponding to a button being pressed or not pressed

    :Examples:

    >>> all_buttons = Gamepads.get_all_buttons(0)
    >>> all_buttons[1]
    True

    """
    gamepad_index = mc.get("gamepad")[str(index)]
    print(gamepad_index)
    assert gamepad_index != None, "gamepad index not found"
    return [x == 1 for x in gamepad_index['buttons']]

def get_button(index,button):
    """Returns whether a button is pressed or not.

    For a specific button (each button has has a number) the output is either
    True (pressed) or False (not pressed). To see the exact mapping, click on
    the 'Details' button next to a gamepad in Dawn, or refer to
    https://w3c.github.io/gamepad/#remapping.

    :param index: The index of the gamepad, usually 0, 1, 2, or 3
    :param button: Enum of button, see api documentation for more details
    :returns: A boolean either True (pressed) or False (not pressed)

    :Examples:

    >>> button = Gamepads.get_button(0,Button.Y)
    >>> button
    False

    """
    return get_all_buttons(index)[button] == 1;

def get_is_connected(index):
    """Returns whether or not the specified gamepad is connected.

    :param index: The index of the gamepad, usually 0, 1, 2, or 3
    :returns: A boolean value for whether or not that gamepad is connected
    """
    gamepad_index = mc.get("gamepad")[index]
    assert gamepad_index != None, "gamepad index not found"
    return gamepad_index['connected']


# If the user knows the layout of the device and it corresponds to the Standard Gamepad
# Layout, then the mapping should be set to standard. Otherwise set mapping property to empty string
def get_mapping(index):
    """Returns the mapping of the specified gamepad. Usually this value will be 'standard.'
    """
    gamepad_index = mc.get("gamepad")[index]
    assert gamepad_index != None, "gamepad index not found"
    return gamepad_index['mapping']

#class for enums for buttons.
class Button:
    A = 0
    B = 1
    X = 2
    Y = 3
    L_BUMPER = 4
    R_BUMPER = 5
    L_TRIGGER = 6
    R_TRIGGER = 7
    BACK = 8
    START = 9
    L_STICK = 10
    R_STICK = 11
    DPAD_UP = 12
    DPAD_DOWN = 13
    DPAD_LEFT = 14
    DPAD_RIGHT = 15
    XBOX = 16

#class for enums for joysticks
class Joystick:
    LEFT_X = 0
    LEFT_Y = 1
    RIGHT_X = 2
    RIGHT_Y = 3
