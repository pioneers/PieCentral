import queue
from Alliance import *
from Goal import *
from LCM import *
from Timer import *
from Utils import *


###########################################
# Evergreen Methods
###########################################

def start():
    '''
    Main loop which processes the event queue and calls the appropriate function
    based on game state and the dictionary of available functions
    '''
    events = queue.Queue()
    lcm_start_read(LCM_TARGETS.SHEPHERD, events)
    while True:
        payload = events.get(True)
        if game_state == STATE.SETUP:
            func = setup_functions.get(payload[0])
            if func is not None:
                func(payload[1])
            else:
                print("Invalid Event in Setup")
        elif game_state == STATE.AUTO:
            func = auto_functions.get(payload[0])
            if func is not None:
                func(payload[1])
            else:
                print("Invalid Event in Auto")
        elif game_state == STATE.WAIT:
            func = wait_functions.get(payload[0])
            if func is not None:
                func(payload[1])
            else:
                print("Invalid Event in Wait")
        elif game_state == STATE.TELE:
            func = teleop_functions.get(payload[0])
            if func is not None:
                func(payload[1])
            else:
                print("Invalid Event in Teleop")
        elif game_state == STATE.END:
            func = end_functions.get(payload[0])
            if func is not None:
                func(payload[1])
            else:
                print("Invalid Event in End")

def to_setup(args):
    '''
    Move to the setup stage which is should push scores from previous game to spreadsheet,
    load the teams for the upcoming match, reset all state, and send information to scoreboard.
    By the end, should be ready to start match.
    '''
    if game_state == STATE.END:
        flush_scores()

    reset()
    alliances[ALLIANCE_COLOR.BLUE] = Alliance(ALLIANCE_COLOR.BLUE, args[0],
                                              args[1], args[2], args[3])
    alliances[ALLIANCE_COLOR.GOLD] = Alliance(ALLIANCE_COLOR.GOLD, args[4],
                                              args[5], args[6], args[7])
    goals[GOAL.BLUE].set_owner(alliances[ALLIANCE_COLOR.BLUE])
    goals[GOAL.GOLD].set_owner(alliances[ALLIANCE_COLOR.GOLD])
    #TODO: Send teams to scoreboard
    print("ENTERING SETUP STATE")

def to_auto(args):
    '''
    Move to the autonomous stage where robots should begin autonomously.
    By the end, should be in autonomous state, allowing any function from this
    stage to be called and autonomous match timer should have begun.
    '''
    global game_state
    for goal in goals.values():
        goal.set_autonomous()

    game_timer.start_timer(CONSTANTS.AUTO_TIME)
    game_state = STATE.AUTO
    #TODO: Send message to Dawn to start autonomous
    print("ENTERING AUTO STATE")

def to_wait(args):
    '''
    Move to the waiting stage, between autonomous and teleop periods.
    By the end, should be in wait state and the robots should be disabled.
    Some years, there might be methods that can be called once in the wait stage
    '''
    #TODO
    print("ENTERING WAIT STATE")

def to_teleop(args):
    '''
    Move to teleoperated stage where robots are enabled and controlled manually.
    By the end, should be in teleop state and the teleop match timer should be started.
    '''
    #TODO
    print("ENTERING TELEOP STATE")

def to_end(args):
    '''
    Move to end stage after the match ends. Robots should be disabled here
    and final score adjustments can be made.
    '''
    #TODO
    print("ENTERING END STATE")

def reset(args=None):
    '''
    Resets the current match, moving back to the setup stage but with the current teams loaded in.
    Should reset all state being tracked by Shepherd.
    ****THIS METHOD MIGHT NEED UPDATING EVERY YEAR BUT SHOULD ALWAYS EXIST****
    '''
    global game_state
    game_state = STATE.SETUP
    Timer.reset_all()
    for alliance in alliances.values():
        if alliance is not None:
            alliance.reset()
    for goal in goals.values():
        goal.reset()
    #TODO: Send reset info to scoreboard
    print("RESET MATCH, MOVE TO SETUP")

def score_adjust(args):
    '''
    Allow for score to be changed based on referee decisions
    '''
    #TODO

def flush_scores():
    '''
    Send scores to the spreadsheet for the current match
    '''
    pass

###########################################
# Game Specific Methods (Solar Scramble)
###########################################

def generate_rfids(args):
    '''
    Select the set of 6 RFIDs to be used until this method is called again
    RFIDs should be sent to the UI to be displayed for field reset
    '''
    pass

def goal_score(args):
    '''
    Update state for a goal being scored and push information to scoreboard
    '''
    goal_name = args[0]
    alliance = args[1]
    goals.get(goal_name).score(alliances.get(alliance))

def goal_bid(args):
    '''
    Update state for a goal being bid on and push information to scoreboard
    and to sensors
    '''
    pass

def code_input(args):
    '''
    Update state for a code being input, return information to sensors
    to display result of code being decoded
    '''
    pass

def bid_complete(args):
    '''
    Update state when a bid timer ends and a bid is complete
    Update scoreboard and sensors with this information as well
    '''
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
    SHEPHERD_HEADER.SCORE_ADJUST : score_adjust,
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

###########################################
# Evergreen Variables
###########################################

game_state = STATE.END
game_timer = Timer(TIMER_TYPES.MATCH)

###########################################
# Game Specific Variables
###########################################

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

rfid_pool = None
curr_rfids = None

if __name__ == '__main__':
    start()
