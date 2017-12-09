from enum import Enum, unique

@unique # pylint: disable=invalid-name
class SHEPHERD_HEADER(Enum):
    GOAL_SCORE = "goal_score"
    GOAL_BID = "goal_bid"
    CODE_INPUT = "code_input"

    START_MATCH = "start_match"
    SETUP_MATCH = "setup_match"
    START_NEXT_STAGE = "start_next_stage"
    RESET_CURRENT_STAGE = "reset_current_stage"
    RESET_MATCH = "reset_match"

    GENERATE_RFID = "generate_rfid"

    BID_TIMER_END = "bid_timer_end"
    STAGE_TIMER_END = "stage_timer_end"

@unique # pylint: disable=invalid-name
class SENSOR_HEADER(Enum):
    CODE_RESULT = "code_result"
    FAILED_POWERUP = "failed_powerup"
    CURRENT_BID = "current_bid"

@unique # pylint: disable=invalid-name
class SCOREBOARD_HEADER(Enum):
    SCORE = "score"
    TEAMS = "teams"
    BID_TIMER_START = "bid_timer_start"
    BID_AMOUNT = "bid_amount"
    BID_WIN = "bid_win"
    STAGE = "stage"
    STAGE_TIMER_START = "stage_timer_start"
    POWERUPS = "powerups"
    ALLIANCE_MULTIPLIER = "alliance_multiplier"

# pylint: disable=invalid-name
class CONSTANTS(Enum):
    TWO_X_COOLDOWN = 5
    ZERO_X_COOLDOWN = 5
    STEAL_COOLDOWN = 5
    CODE_COOLDOWN = 5
    BID_INCREASE_CONSTANT = 5

@unique # pylint: disable=invalid-name
class AllIANCE_COLOR(Enum):
    GOLD = "gold"
    BLUE = "blue"

@unique # pylint: disable=invalid-name
class LCM_TARGETS(Enum):
    LCM_TARGET_SHEPHERD = "lcm_target_shepherd"
    LCM_TARGET_SCOREBOARD = "lcm_target_scoreboard"
    LCM_TARGET_SENSORS = "lcm_target_sensors"

@unique # pylint: disable=invalid-name
class TIMER_TYPES(Enum):
    BID = "bid"
    MATCH = "match"
    COOLDOWN = "cooldown"
    CODE_COOLDOWN = "code_cooldown"
    DURATION = "duration"

@unique # pylint: disable=invalid-name
class POWERUP_TYPES(Enum):
    ZERO_X = "zero_x"
    TWO_X = "two_x"
    STEAL = "steal"
