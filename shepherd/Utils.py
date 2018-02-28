# pylint: disable=invalid-name
class SHEPHERD_HEADER():
    GOAL_SCORE = "goal_score"
    GOAL_BID = "goal_bid"
    #CODE_INPUT = "code_input"
    POWERUP_APPLICATION = "powerup_application"

    START_MATCH = "start_match"
    SETUP_MATCH = "setup_match"
    START_NEXT_STAGE = "start_next_stage"
    RESET_CURRENT_STAGE = "reset_current_stage"
    RESET_MATCH = "reset_match"
    SCORE_ADJUST = "score_adjust"

    GENERATE_RFID = "generate_rfid"

    BID_TIMER_END = "bid_timer_end"
    STAGE_TIMER_END = "stage_timer_end"

# pylint: disable=invalid-name
class SENSOR_HEADER():
    CODE_RESULT = "code_result"
    GOAL_OWNERS = "bid_owners"
    TEAM_SCORE = "team_score"
    BID_PRICE = "bid_price"

class DAWN_HEADER():
    ROBOT_STATE = "robot_state"
    CODES = "codes"

# pylint: disable=invalid-name
class SCOREBOARD_HEADER():
    SCORE = "score"
    TEAMS = "teams"
    BID_TIMER = "bid_timer"
    BID_AMOUNT = "bid_amount"
    GOAL_OWNED = "bid_win"
    STAGE = "stage"
    STAGE_TIMER_START = "stage_timer_start"
    POWERUPS = "powerups"
    ALLIANCE_MULTIPLIER = "alliance_multiplier"
    RESET_TIMERS = "reset_timers"

# pylint: disable=invalid-name
class GUI_HEADER():
    SEND_RFIDS = "send_rfids"
    SEND_SCORES = "send_scores"

# pylint: disable=invalid-name
class CONSTANTS():
    AUTO_TIME = 30
    TELEOP_TIME = 180
    BID_TIME_INCREASE = 2
    BID_TIME_INITIAL = 5
    TWO_X_COOLDOWN = 5
    ZERO_X_COOLDOWN = 5
    STEAL_COOLDOWN = 5
    CODE_COOLDOWN = 5
    BID_INCREASE_CONSTANT = 5
    GOAL_BASE_VALUE = 1
    GOAL_LOW_VALUE = 5
    GOAL_MED_VALUE = 10
    GOAL_HIGH_VALUE = 25
    GOAL_LOW_COST = 20
    GOAL_MED_COST = 40
    GOAL_HIGH_COST = 100
    MULTIPLIER_INCREASES = [1.1, 1.25, 1.5]
    SPREADSHEET_ID = "1ikEY2pnESr_e7okP9H5KZiJYK29RI5ISPSaCgQU41RU"
    CSV_FILE_NAME = "PIE test sheet - qual_matches.csv"



# pylint: disable=invalid-name
class ALLIANCE_COLOR():
    GOLD = "gold"
    BLUE = "blue"

# pylint: disable=invalid-name
class LCM_TARGETS():
    SHEPHERD = "lcm_target_shepherd"
    SCOREBOARD = "lcm_target_scoreboard"
    SENSORS = "lcm_target_sensors"
    UI = "lcm_target_ui"
    DAWN = "lcm_target_dawn"

# pylint: disable=invalid-name
class TIMER_TYPES():
    BID = "bid"
    MATCH = "match"
    COOLDOWN = "cooldown"
    CODE_COOLDOWN = "code_cooldown"
    DURATION = "duration"

# pylint: disable=invalid-name
class POWERUP_TYPES():
    ZERO_X = "zero_x"
    TWO_X = "two_x"
    STEAL = "steal"

# pylint: disable=invalid-name
class GOAL():
    A = "a"
    B = "b"
    C = "c"
    D = "d"
    E = "e"
    BLUE = "blue_goal"
    GOLD = "gold_goal"

# pylint: disable=invalid-name
class STATE():
    SETUP = "setup"
    AUTO = "auto"
    WAIT = "wait"
    TELEOP = "teleop"
    END = "end"
