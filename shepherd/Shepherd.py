import queue
import random
from Alliance import *
from Goal import *
from LCM import *
from Timer import *
from Utils import *
import Sheet


###########################################
# Evergreen Methods
###########################################

def start():
    '''
    Main loop which processes the event queue and calls the appropriate function
    based on game state and the dictionary of available functions
    '''
    global events
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
    global match_number, powerup_functions
    b1_name, b1_num = args["b1name"], args["b1num"]
    b2_name, b2_num = args["b2name"], args["b2num"]
    g1_name, g1_num = args["g1name"], args["g2num"]
    g2_name, g2_num = args["g2name"], args["g2num"]

    if game_state == STATE.END:
        flush_scores()

    match_number = args["match_num"]

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

    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.TEAMS, {
        "b1name" : b1_name, "b1num" : b1_num,
        "b2name" : b2_name, "b2num" : b2_num,
        "g1name" : g1_name, "g1num" : g1_num,
        "g2name" : g2_name, "g2num" : g2_num})

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
    enable_robots(True)
    print("ENTERING AUTO STATE")

def to_wait(args):
    '''
    Move to the waiting stage, between autonomous and teleop periods.
    By the end, should be in wait state and the robots should be disabled.
    Some years, there might be methods that can be called once in the wait stage
    '''
    global game_state
    game_state = STATE.WAIT
    disable_robots()
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
    enable_robots(False)
    print("ENTERING TELEOP STATE")

def to_end(args):
    '''
    Move to end stage after the match ends. Robots should be disabled here
    and final score adjustments can be made.
    '''
    global game_state
    lcm_send(LCM_TARGETS.UI, GUI_HEADER.SEND_SCORES,
             {"blue_score" : alliances[ALLIANCE_COLOR.BLUE].score,
              "gold_score" : alliances[ALLIANCE_COLOR.GOLD].score})
    game_state = STATE.END
    disable_robots()
    print("ENTERING END STATE")

def reset(args=None):
    '''
    Resets the current match, moving back to the setup stage but with the current teams loaded in.
    Should reset all state being tracked by Shepherd.
    ****THIS METHOD MIGHT NEED UPDATING EVERY YEAR BUT SHOULD ALWAYS EXIST****
    '''
    global game_state, events
    game_state = STATE.SETUP
    Timer.reset_all()
    events = queue.Queue()
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.RESET_TIMERS)
    for alliance in alliances.values():
        if alliance is not None:
            alliance.reset()
    for goal in goals.values():
        goal.reset()

    print("RESET MATCH, MOVE TO SETUP")

def score_adjust(args):
    '''
    Allow for score to be changed based on referee decisions
    '''
    blue_score, gold_score = args["blue_goal"], args["gold_score"]
    alliances[ALLIANCE_COLOR.BLUE].score = blue_score
    alliances[ALLIANCE_COLOR.GOLD].score = gold_score
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.SCORE,
             {"alliance" : alliances[ALLIANCE_COLOR.BLUE].name,
              "score" : alliances[ALLIANCE_COLOR.BLUE].score})
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.SCORE,
             {"alliance" : alliances[ALLIANCE_COLOR.GOLD].name,
              "score" : alliances[ALLIANCE_COLOR.GOLD].score})

def flush_scores():
    '''
    Sends the most recent match score to the spreadsheet if connected to the internet
    '''
    Sheet.write_scores(match_number, alliances[ALLIANCE_COLOR.BLUE].score,
                       alliances[ALLIANCE_COLOR.GOLD].score)

def enable_robots(autonomous):
    '''
    Sends message to Dawn to enable all robots. The argument should be a boolean
    which is true if we are entering autonomous mode
    '''
    msg = {"autonomous": autonomous, "enabled": True}

    lcm_send(LCM_TARGETS.DAWN, DAWN_HEADER.ROBOT_STATE, msg)

def disable_robots():
    '''
    Sends message to Dawn to disable all robots
    '''
    msg = {"autonomous": False, "enabled": False}
    lcm_send(LCM_TARGETS.DAWN, DAWN_HEADER.ROBOT_STATE, msg)

###########################################
# Game Specific Methods (Solar Scramble)
###########################################

def generate_rfids(args):
    '''
    Select the set of 6 RFIDs to be used until this method is called again
    RFIDs should be sent to the UI to be displayed for field reset
    '''
    global curr_rfids
    rfids = open("rfid.txt")
    rfid_list = []
    numbers = rfids.readlines()
    for i in numbers:
        i = i.strip()
        rfid_list.append(int(i))
    rfids = []
    for i in range(6):
        temp = random.choice(rfid_list)
        rfid_list.remove(temp)
        rfids.append(temp)
    curr_rfids = rfids

def goal_score(args):
    '''
    Update state for a goal being scored and push information to scoreboard
    '''
    alliance = args["alliance"]
    goal_name = args["goal"]
    goals.get(goal_name).score(alliances.get(alliance))
    #TODO: send score update to scoreboard and sensors

def goal_bid(args):
    '''
    Update state for a goal being bid on and push information to scoreboard
    and to sensors
    '''
    alliance = args["alliance"]
    goal_name = args["goal"]
    goals.get(goal_name).bid(alliances.get(alliance))


def powerup_application(args):
    '''
    Update state for a code being input, return information to sensors
    to display result of code being decoded.
    Apply a powerup to a goal. Does not need to say result.
    '''
    alliance = args["alliance"]
    goal = goals.get(args["goal"])
    #TODO index = CodeGen.check_code(args["code"], curr_rfids)
    index = -1
    if index == -1:
        lcm_send(LCM_TARGETS.SENSORS,
                 SENSOR_HEADER.FAILED_POWERUP, {"alliance" : alliance.name})
        return
    if game_state == STATE.AUTO:
        alliance.increment_multiplier()
    elif game_state == STATE.TELEOP:
        powerup = powerup_functions[index]
        goal.apply_powerup(powerup, alliance)

    #TODO: if the powerup didnt work we also need to send the info back to sensors

def bid_complete(args):
    '''
    Update state when a bid timer ends and a bid is complete
    Update scoreboard and sensors with this information as well
    '''
    goal_name = args["goal"]
    alliance = goals.get(goal_name).current_bid_team
    goals.get(goal_name).set_owner(alliance)

    for goal in goals.values():
        if goal.owner is not None:
            continue
        if goal.current_bid_team == alliance and alliance.score < goal.current_bid:
            goal.current_bid = goal.previous_bid
            goal.current_bid_team = goal.previous_bid_team
            goal.previous_bid = goal.start_bid
            goal.previous_bid_team = None
            #TODO: send current bid team to scoreboard
        if goal.current_bid_team is None:
            goal.bid_timer.reset()
            #TODO: send reset timer message to scoreboard

    #TODO: send owner info and bid leader info to sensors and scoreboard

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

match_number = -1
alliances = {ALLIANCE_COLOR.GOLD: None, ALLIANCE_COLOR.BLUE: None}

###########################################
# Game Specific Variables
###########################################


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
powerup_functions = [None, None, None, None, None, None]
events = None

if __name__ == '__main__':
    start()
