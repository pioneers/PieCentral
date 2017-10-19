
# Values for the cooldowns
from enum import Enum, unique

@unique # pylint: disable=invalid-name
class CONSTANTS(Enum):
    TWO_X_COOLDOWN = 1
    ZERO_X_COOLDOWN = 1
    STEAL_COOLDOWN = 1
    CODE_COOLDOWN = 1
    BID_INCREASE_CONSTANT = 1

@unique # pylint: disable=invalid-name
class TIMER_TYPES(Enum):
    BID = 'bid'
    MATCH = 'match'
    COOLDOWN = 'cooldown'
    CODE_COOLDOWN = 'code_cooldown'
    DURATION = 'duration'
