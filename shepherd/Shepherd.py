import queue
from Alliance import *
from Goal import *
from LCM import *
from Timer import *
from Utils import *
import random


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
        elif game_state == STATE.TELEOP:
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
    b1_name, b1_num, b2_name, b2_num, g1_name, g1_num, g2_name, g2_num =
        args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7]

    if game_state == STATE.END:
        flush_scores()

    reset()
    alliances[ALLIANCE_COLOR.BLUE] = Alliance(ALLIANCE_COLOR.BLUE, b1_name,
                                              b1_num, b2_name, b2_num)
    alliances[ALLIANCE_COLOR.GOLD] = Alliance(ALLIANCE_COLOR.GOLD, g1_name,
                                              g1_num, g2_name, g2_num)
    goals[GOAL.BLUE].set_owner(alliances[ALLIANCE_COLOR.BLUE])
    goals[GOAL.GOLD].set_owner(alliances[ALLIANCE_COLOR.GOLD])

    powerup_functions = [None, None, None, None, None, None]
    indexies = [0, 1, 2]
    for powerup in [POWERUP_TYPES.ZERO_X, POWERUP_TYPES.TWO_X,
                    POWERUP_TYPES.STEAL]:
        i = indexies.pop(random.randint(0, len(indexies))-1)
        powerup_functions[i] = powerup
    powerup_functions[3:6] = powerup_functions[0:3]

    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.TEAMS, b1_name, b1_num,
             b2_name, b2_num, g1_name, g1_num, g2_name, g2_num)
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
    global game_state
    game_state = STATE.WAIT
    #TODO: send message to Dawn to disable robots
    print("ENTERING WAIT STATE")

def to_teleop(args):
    '''
    Move to teleoperated stage where robots are enabled and controlled manually.
    By the end, should be in teleop state and the teleop match timer should be started.
    '''
    global game_state
    game_state = STATE.TELEOP

    for goal in goals.values():
    	goal.set_teleop()

    game_timer.start_timer(CONSTANTS.TELEOP_TIME)
    #TODO: send message to enable robots in teleop
    print("ENTERING TELEOP STATE")

def to_end(args):
    '''
    Move to end stage after the match ends. Robots should be disabled here
    and final score adjustments can be made.
    '''
    global game_state
    game_state = STATE.END
    #TODO: send message to disable robots
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
    events = queue.Queue()
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.RESET_TIMERS)
    for alliance in alliances.values():
        if alliance is not None:
            alliance.reset()
            lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.SCORE,
                     [alliance.name, alliance.score])
                     #alliance mul
    for goal in goals.values():
        goal.reset()
        lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.GOAL_OWNED,
                 [goal.name, None])
        lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.BID_AMOUNT,
                 [goal.name,goal.current_bid_team,goal.current_bid])

    #TODO: Send reset info to scoreboard

    print("RESET MATCH, MOVE TO SETUP")

def score_adjust(args):
    '''
    Allow for score to be changed based on referee decisions
    '''
    blue_score, gold_score = args[0], args[1]
    alliances[ALLIANCE_COLOR.BLUE].score = blue_score
    alliances[ALLIANCE_COLOR.GOLD].score = gold_score
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.SCORE,
             [alliances[ALLIANCE_COLOR.BLUE].name,
             alliances[ALLIANCE_COLOR.BLUE].score])
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.SCORE,
             [alliances[ALLIANCE_COLOR.GOLD].name,
             alliances[ALLIANCE_COLOR.GOLD].score])

def flush_scores():
    '''
    Send scores to the spreadsheet for the current match
    '''
    #TODO all of it
    pass


###########################################
# Game Specific Methods (Solar Scramble)
###########################################

def generate_rfids(args):
    '''
    Select the set of 6 RFIDs to be used until this method is called again
    RFIDs should be sent to the UI to be displayed for field reset
    '''
    rfids = open("rfid.txt")
    rfid_list = []
    numbers = rfids.readlines()
    for i in numbers:
        i = i.strip()
        rfid_list.append(i)
    return_value = []
    for i in range(6):
        temp = random.choice(rfid_list)
        rfid_list.remove(temp)
        return_value.append(temp)
    return return_value

def goal_score(args):
    '''
    Update state for a goal being scored and push information to scoreboard
    '''
    alliance = args[0]
    goal_name = args[1]
    goals.get(goal_name).score(alliances.get(alliance))

def goal_bid(args):
    '''
    Update state for a goal being bid on and push information to scoreboard
    and to sensors
    '''
    alliance = args[0]
    goal_name = args[1]
    goals.get(goal_name).bid(alliances.get(alliance))

    #TODO: Push bid timer, bid amount, curr bid owner to scoreboard (maybe this is done now??)

def powerup_application(args):
    '''
    Update state for a code being input, return information to sensors
    to display result of code being decoded.
    Apply a powerup to a goal. Does not need to say result.
    '''
    alliance = args[0]
    goal = goals.get(args[1])
    index = CodeGen.check_code(args[2], curr_rfids)
    if index == -1:
        lcm_send(LCM_TARGETS.SENSORS,
                 SENSOR_HEADER.FAILED_POWERUP, alliance)
        return
    if game_state == STATE.AUTO:
        alliance.increment_multiplier()
    elif game_state = STATE.TELEOP:
        powerup = powerup_functions[index]
        goal.apply_powerup(powerup, alliance)

def bid_complete(args):
    '''
    Update state when a bid timer ends and a bid is complete
    Update scoreboard and sensors with this information as well
    '''
    goal_name = args[0]
    goals.get(goal_name).set_owner(goals.get(goal_name).current_bid_team)

###########################################
# Event to Function Mappings for each Stage
###########################################

setup_functions = {
    SHEPHERD_HEADER.GENERATE_RFID : generate_rfids,
    SHEPHERD_HEADER.SETUP_MATCH: to_setup,
    SHEPHERD_HEADER.START_NEXT_STAGE: to_auto
}

auto_functions = {
    SHEPHERD_HEADER.GOAL_SCORE : goal_score,
    SHEPHERD_HEADER.GOAL_BID : goal_bid,
    SHEPHERD_HEADER.BID_TIMER_END : bid_complete,
    SHEPHERD_HEADER.RESET_MATCH : reset,
    SHEPHERD_HEADER.STAGE_TIMER_END : to_wait,
    SHEPHERD_HEADER.POWERUP_APPLICATION : powerup_application
}

wait_functions = {
    SHEPHERD_HEADER.GOAL_BID : goal_bid,
    SHEPHERD_HEADER.BID_TIMER_END : bid_complete,
    SHEPHERD_HEADER.RESET_MATCH : reset,
    SHEPHERD_HEADER.SCORE_ADJUST : score_adjust,
    SHEPHERD_HEADER.START_NEXT_STAGE : to_teleop
}

teleop_functions = {
    SHEPHERD_HEADER.GOAL_SCORE : goal_score,
    SHEPHERD_HEADER.GOAL_BID : goal_bid,
    SHEPHERD_HEADER.BID_TIMER_END : bid_complete,
    SHEPHERD_HEADER.RESET_MATCH : reset,
    SHEPHERD_HEADER.STAGE_TIMER_END : to_end,
    SHEPHERD_HEADER.POWERUP_APPLICATION : powerup_application
}

end_functions = {
    SHEPHERD_HEADER.RESET_MATCH : reset,
    SHEPHERD_HEADER.SCORE_ADJUST : score_adjust,
    SHEPHERD_HEADER.SETUP_MATCH : to_setup
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
powerup_functions = [None,None,None,None,None,None]

if __name__ == '__main__':
    start()
