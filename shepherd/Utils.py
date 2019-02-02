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

    ROBOT_OFF = "robot_off"

    END_EXTENDED_TELEOP = "end_extended_teleop"

    LAUNCH_BUTTON_TRIGGERED = "launch_button_triggered"
    CODE_APPLICATION = "code_application"

    APPLY_PERKS = "apply_perks"
    GAME_PERKS = "game_perks"
    MASTER_ROBOT = "master_robot"

    FINAL_SCORE = "final_score"
    ASSIGN_TEAMS = "assign_teams"
        # ASSIGN_TEAMS{g1num, g2num, b1num, b2num}
    TEAM_RETRIEVAL = "team_retrieval"
        # TEAM_RETRIEVAL{}

# pylint: disable=invalid-name
class SENSORS_HEADER():
    FAILED_POWERUP = "failed_powerup"

# pylint: disable=invalid-name
class DAWN_HEADER():
    ROBOT_STATE = "robot_state"
    CODES = "codes"
        # CODES{codes_solutions}
    HEARTBEAT = "heartbeat"
    DECODE = "decode"
        # DECODE{alliance, tag}
    SPECIFIC_ROBOT_STATE = "specific_robot_state"
        # SPECIFIC_ROBOT_STATE{team_number, autonomous, enabled}
    MASTER = "master"
    	# MASTER{alliance, team_number}


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

    LAUNCH_BUTTON_TIMER_START = "launch_button_timer_start"
        # LAUNCH_BUTTON_TIMER_START{alliance, button}
    PERKS_SELECTED = "perks_selected"
        # PERKS_SELECTED{alliance, perk_1, perk_2, perk_3}
    APPLIED_EFFECT = "applied_effect"
        # APPLIED_EFFECT{alliance, effect}

# pylint: disable=invalid-name
class CONSTANTS():
    PERK_SELECTION_TIME = 15
    AUTO_TIME = 30
    TELEOP_TIME = 180
    SPREADSHEET_ID = "1F_fRPZ2Whe3f8ssniqh1uWFfc8dU8LfElY51R4EtJDY"
    CSV_FILE_NAME = "Sheets/schedule.csv"
    TAFFY_TIME = 15

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
    LAUNCH_BUTTON = "launch_button"
    EXTENDED_TELEOP = "extended_teleop"

# pylint: disable=invalid-name
class STATE():
    SETUP = "setup"
    PERK_SELCTION = "perk_selection"
    AUTO = "auto"
    WAIT = "wait"
    TELEOP = "teleop"
    END = "end"

class EFFECTS():
    BLACKMAIL = "blackmail"
    SPOILED_CANDY = "spoiled_candy"
    ALL_EFFECTS = [BLACKMAIL, SPOILED_CANDY]

class PERKS():
    EMPTY = "empty"
    BUBBLEGUM = "bubblegum"
    TAFFY = "taffy"
    # To be continued
