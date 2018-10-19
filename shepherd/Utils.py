# pylint: disable=invalid-name
class SHEPHERD_HEADER():
    START_NEXT_STAGE = "start_next_stage"
    RESET_CURRENT_STAGE = "reset_current_stage"
    RESET_MATCH = "reset_match"

    GET_MATCH_INFO = "get_match_info"
    SETUP_MATCH = "setup_match"

    STOP_ROBOT = "stop_robot"

    GET_SCORES = "get_scores"
    SCORE_ADJUST = "score_adjust"

    STAGE_TIMER_END = "stage_timer_end"

# pylint: disable=invalid-name
# class SENSOR_HEADER():

# pylint: disable=invalid-name
class DAWN_HEADER():
    ROBOT_STATE = "robot_state"
    HEARTBEAT = "heartbeat"

# pylint: disable=invalid-name
class UI_HEADER():
    TEAMS_INFO = "teams_info"
    SCORES = "scores"

# pylint: disable=invalid-name
class SCOREBOARD_HEADER():
    SCORE = "score"
    TEAMS = "teams"
    STAGE = "stage"
    STAGE_TIMER_START = "stage_timer_start"
    RESET_TIMERS = "reset_timers"
    ALL_INFO = "all_info"

# pylint: disable=invalid-name
class CONSTANTS():
    AUTO_TIME = 30
    TELEOP_TIME = 180
    SPREADSHEET_ID = "1F_fRPZ2Whe3f8ssniqh1uWFfc8dU8LfElY51R4EtJDY"
    CSV_FILE_NAME = "Sheets/schedule.csv"

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
    MATCH = "match"

# pylint: disable=invalid-name
class STATE():
    SETUP = "setup"
    AUTO = "auto"
    WAIT = "wait"
    TELEOP = "teleop"
    END = "end"
