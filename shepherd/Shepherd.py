from Alliance import *
from Goal import *
from LCM import *
from Timer import *
from Utils import *
import queue

###########################################
# Evergreen Methods
###########################################

def start():
    events = queue.Queue()
    lcm_start_read(LCM_TARGETS.SHEPHERD, events)
    while True:
        payload = events.get(True)
        if game_state == STATE.SETUP:
            setup_functions.get(payload[0])(payload[1])
        elif game_state == STATE.AUTO:
            auto_functions.get(payload[0])(payload[1])
        elif game_state == STATE.WAIT:
            wait_functions.get(payload[0])(payload[1])
        elif game_state == STATE.TELE:
            teleop_functions.get(payload[0])(payload[1])
        elif game_state == STATE.END:
            end_functions.get(payload[0])(payload[1])    

def to_setup(args):
    if game_state == STATE.END:
        flush_scores()

    reset()
    alliances[ALLIANCE_COLOR.BLUE] = Alliance(ALLIANCE_COLOR.BLUE, args[0], args[1], args[2], args[3])
    alliances[ALLIANCE_COLOR.GOLD] = Alliance(ALLIANCE_COLOR.GOLD, args[4], args[5], args[6], args[7])
    goals[GOAL.BLUE].set_owner(alliances[ALLIANCE_COLOR.BLUE])
    goals[GOAL.GOLD].set_owner(alliances[ALLIANCE_COLOR.GOLD])
    print("ENTERING SETUP STATE")

def to_auto(args):
    global game_state
    for goal in goals.values():
        goal.set_autonomous()

    game_timer.start_timer(CONSTANTS.AUTO_TIME)
    game_state = STATE.AUTO
    print("ENTERING AUTO STATE")

def to_wait(args):
    print("ENTERING WAIT STATE")
    pass

def to_teleop(args):
    print("ENTERING TELEOP STATE")
    pass

def to_end(args):
    print("ENTERING END STATE")
    pass

def reset(args=None):
    global game_state
    game_state = STATE.SETUP
    Timer.reset_all()
    for alliance in alliances.values():
        if alliance is not None:
            alliance.reset()
    for goal in goals.values():
        goal.reset()
    print("RESET MATCH, GOING TO SETUP STATE")

def score_adjust(args):
    pass

def flush_scores():
    pass

###########################################
# Game Specific Methods
###########################################

def generate_rfids(args):
    pass

def goal_score(args):
    goal_name = args[0]
    alliance = args[1]
    goals.get(goal_name).score(alliances.get(alliance)) 

def goal_bid(args):
    pass

def code_input(args):
    pass

def bid_complete(args):
    pass

###########################################
# Event to Function Mappings for each Stage
###########################################

setup_functions = {
    SHEPHERD_HEADER.GENERATE_RFID : generate_rfids,
    SHEPHERD_HEADER.SETUP_MATCH: to_setup,
    SHEPHERD_HEADER.START_NEXT_STAGE: to_auto,
}

auto_functions = {
    SHEPHERD_HEADER.GOAL_SCORE : goal_score,
    SHEPHERD_HEADER.GOAL_BID : goal_bid,
    SHEPHERD_HEADER.CODE_INPUT : code_input,
    SHEPHERD_HEADER.BID_TIMER_END : bid_complete,
    SHEPHERD_HEADER.RESET_MATCH : reset,
    SHEPHERD_HEADER.STAGE_TIMER_END : to_wait,
}

wait_functions = {
    SHEPHERD_HEADER.GOAL_BID : goal_bid,
    SHEPHERD_HEADER.BID_TIMER_END : bid_complete,
    SHEPHERD_HEADER.RESET_MATCH : reset,
    SHEPHERD_HEADER.START_NEXT_STAGE : to_teleop,
}

teleop_functions = {
    SHEPHERD_HEADER.GOAL_SCORE : goal_score,
    SHEPHERD_HEADER.GOAL_BID : goal_bid,
    SHEPHERD_HEADER.CODE_INPUT : code_input,
    SHEPHERD_HEADER.BID_TIMER_END : bid_complete,
    SHEPHERD_HEADER.RESET_MATCH : reset,
    SHEPHERD_HEADER.STAGE_TIMER_END : to_end,
}

end_functions = {
    SHEPHERD_HEADER.RESET_MATCH : reset,
    SHEPHERD_HEADER.SCORE_ADJUST : score_adjust,
    SHEPHERD_HEADER.SETUP_MATCH : to_setup,
}

alliances = {ALLIANCE_COLOR.GOLD: None, ALLIANCE_COLOR.BLUE: None}

goals = {
    GOAL.A : Goal(GOAL.A, CONSTANTS.GOAL_LOW_VALUE, CONSTANTS.GOAL_LOW_COST),
    GOAL.B : Goal(GOAL.B, CONSTANTS.GOAL_MED_VALUE, CONSTANTS.GOAL_MED_COST),
    GOAL.C : Goal(GOAL.C, CONSTANTS.GOAL_HIGH_VALUE, CONSTANTS.GOAL_HIGH_COST),
    GOAL.D : Goal(GOAL.D, CONSTANTS.GOAL_MED_VALUE, CONSTANTS.GOAL_MED_COST),
    GOAL.E : Goal(GOAL.E, CONSTANTS.GOAL_LOW_VALUE, CONSTANTS.GOAL_LOW_COST),
    GOAL.BLUE : Goal(GOAL.BLUE, CONSTANTS.GOAL_BASE_VALUE, 0),
    GOAL.GOLD: Goal(GOAL.GOLD, CONSTANTS.GOAL_BASE_VALUE, 0),
}


game_state = STATE.END
game_timer = Timer(TIMER_TYPES.MATCH)
rfid_pool = None
curr_rfids = None

if __name__ == '__main__':
    start()
