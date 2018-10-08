import argparse
import queue
import random
import time
from Alliance import *
from Goal import *
from LCM import *
from Timer import *
from Utils import *
import Codegen
import Sheet

__version__ = (1, 0, 0)


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
        print("GAME STATE OUTSIDE: ", game_state)
        time.sleep(0.1)
        payload = events.get(True)
        print(payload)
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
    global match_number
    global curr_challenge_codes, curr_codegen_solutions
    global game_state

    if curr_rfids is None:
        print("ERROR: Generate RFIDS before setting up the next match")
        return

    b1_name, b1_num = args["b1name"], args["b1num"]
    b2_name, b2_num = args["b2name"], args["b2num"]
    g1_name, g1_num = args["g1name"], args["g1num"]
    g2_name, g2_num = args["g2name"], args["g2num"]

    if game_state == STATE.END:
        flush_scores()

    match_number = args["match_num"]

    if alliances[ALLIANCE_COLOR.BLUE] is not None:
        reset()

    alliances[ALLIANCE_COLOR.BLUE] = Alliance(ALLIANCE_COLOR.BLUE, b1_name,
                                              b1_num, b2_name, b2_num)
    alliances[ALLIANCE_COLOR.GOLD] = Alliance(ALLIANCE_COLOR.GOLD, g1_name,
                                              g1_num, g2_name, g2_num)
    goals[GOAL.BLUE].set_owner(alliances[ALLIANCE_COLOR.BLUE])
    goals[GOAL.GOLD].set_owner(alliances[ALLIANCE_COLOR.GOLD])

    send_goal_owners_sensors()
    send_goal_costs_sensors()
    send_team_scores_sensors()

    _, curr_challenge_codes, curr_codegen_solutions = Codegen.get_original_codes(curr_rfids)
    print("SOLUTIONS: " + str(curr_codegen_solutions))
    lcm_send(LCM_TARGETS.DAWN, DAWN_HEADER.CODES, {"rfids" : curr_rfids,
                                                   "codes" : curr_challenge_codes,
                                                   "solutions" : curr_codegen_solutions})

    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.TEAMS, {
        "b1name" : b1_name, "b1num" : b1_num,
        "b2name" : b2_name, "b2num" : b2_num,
        "g1name" : g1_name, "g1num" : g1_num,
        "g2name" : g2_name, "g2num" : g2_num,
        "match_num" : match_number})

    game_state = STATE.SETUP
    print("ENTERING SETUP STATE")
    print({"blue_score" : alliances[ALLIANCE_COLOR.BLUE].score,
           "gold_score" : alliances[ALLIANCE_COLOR.GOLD].score})

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
    regenerate_codes()
    enable_robots(True)
    send_scoreboard_goals()
    send_goal_costs_sensors()
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.STAGE_TIMER_START,
             {"time" : CONSTANTS.AUTO_TIME})
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

    Timer.reset_all()
    regenerate_codes()
    game_timer.start_timer(CONSTANTS.TELEOP_TIME)
    enable_robots(False)
    send_scoreboard_goals()
    send_goal_costs_sensors()
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.STAGE_TIMER_START,
             {"time" : CONSTANTS.TELEOP_TIME})
    print("ENTERING TELEOP STATE")

def to_end(args):
    '''
    Move to end stage after the match ends. Robots should be disabled here
    and final score adjustments can be made.
    '''
    global game_state
    lcm_send(LCM_TARGETS.UI, UI_HEADER.SCORES,
             {"blue_score" : math.floor(alliances[ALLIANCE_COLOR.BLUE].score),
              "gold_score" : math.floor(alliances[ALLIANCE_COLOR.GOLD].score)})
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
    lcm_start_read(LCM_TARGETS.SHEPHERD, events)
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.RESET_TIMERS)
    for alliance in alliances.values():
        if alliance is not None:
            alliance.reset()
    for goal in goals.values():
        goal.reset()
    disable_robots()
    send_scoreboard_goals()
    send_goal_costs_sensors()
    send_team_scores_sensors()
    send_goal_owners_sensors()
    print("RESET MATCH, MOVE TO SETUP")

def get_match(args):
    '''
    Retrieves the match based on match number and sends this information to the UI
    '''
    match_num = int(args["match_num"])
    info = Sheet.get_match(match_num)
    info["match_num"] = match_num
    lcm_send(LCM_TARGETS.UI, UI_HEADER.TEAMS_INFO, info)

def score_adjust(args):
    '''
    Allow for score to be changed based on referee decisions
    '''
    blue_score, gold_score = args["blue_score"], args["gold_score"]
    alliances[ALLIANCE_COLOR.BLUE].score = blue_score
    alliances[ALLIANCE_COLOR.GOLD].score = gold_score
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.SCORE,
             {"alliance" : alliances[ALLIANCE_COLOR.BLUE].name,
              "score" : math.floor(alliances[ALLIANCE_COLOR.BLUE].score)})
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.SCORE,
             {"alliance" : alliances[ALLIANCE_COLOR.GOLD].name,
              "score" : math.floor(alliances[ALLIANCE_COLOR.GOLD].score)})

def get_score(args):
    '''
    Send the current blue and gold score to the UI
    '''
    if alliances[ALLIANCE_COLOR.BLUE] is None:
        lcm_send(LCM_TARGETS.UI, UI_HEADER.SCORES,
                 {"blue_score" : None,
                  "gold_score" : None})
    else:
        lcm_send(LCM_TARGETS.UI, UI_HEADER.SCORES,
                 {"blue_score" : math.floor(alliances[ALLIANCE_COLOR.BLUE].score),
                  "gold_score" : math.floor(alliances[ALLIANCE_COLOR.GOLD].score)})

def flush_scores():
    '''
    Sends the most recent match score to the spreadsheet if connected to the internet
    '''
    if alliances[ALLIANCE_COLOR.BLUE] is not None:
        Sheet.write_scores(match_number, alliances[ALLIANCE_COLOR.BLUE].score,
                           alliances[ALLIANCE_COLOR.GOLD].score)
    return -1

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
    print(curr_rfids)
    lcm_send(LCM_TARGETS.UI, UI_HEADER.RFID_LIST, {"RFID_list" : rfids})

def send_scoreboard_goals():
    for goal in goals.values():
        if goal.owner is None:
            lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.BID_AMOUNT,
                     {"goal" : goal.name, "alliance" : None, "bid" : goal.next_bid})


def send_goal_owners_sensors():

    goal_a = goals.get(GOAL.A)
    goal_b = goals.get(GOAL.B)
    goal_c = goals.get(GOAL.C)
    goal_d = goals.get(GOAL.D)
    goal_e = goals.get(GOAL.E)


    goal_bidders = [None if goal_a.current_bid_team is None else goal_a.current_bid_team.name,
                    None if goal_b.current_bid_team is None else goal_b.current_bid_team.name,
                    None if goal_c.current_bid_team is None else goal_c.current_bid_team.name,
                    None if goal_d.current_bid_team is None else goal_d.current_bid_team.name,
                    None if goal_e.current_bid_team is None else goal_e.current_bid_team.name]

    goal_owners = [None if goal_a.owner is None else goal_a.owner.name,
                   None if goal_b.owner is None else goal_b.owner.name,
                   None if goal_c.owner is None else goal_c.owner.name,
                   None if goal_d.owner is None else goal_d.owner.name,
                   None if goal_e.owner is None else goal_e.owner.name]

    lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.GOAL_OWNERS,
             {"owners" : goal_owners, "bidders" : goal_bidders})

def send_team_scores_sensors():
    team_scores = {ALLIANCE_COLOR.BLUE: math.floor(alliances.get(ALLIANCE_COLOR.BLUE).score),
                   ALLIANCE_COLOR.GOLD: math.floor(alliances.get(ALLIANCE_COLOR.GOLD).score)}

    lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TEAM_SCORE, {"score": team_scores})

def send_goal_costs_sensors():
    goal_costs = [goals.get(GOAL.A).next_bid,
                  goals.get(GOAL.B).next_bid,
                  goals.get(GOAL.C).next_bid,
                  goals.get(GOAL.D).next_bid,
                  goals.get(GOAL.E).next_bid]

    lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.BID_PRICE, {"price" : goal_costs})

def goal_score(args):
    '''
    Update state for a goal being scored and push information to scoreboard
    '''
    alliance = args["alliance"]
    goal_name = args["goal"]
    goals.get(goal_name).score(alliances.get(alliance))
    send_team_scores_sensors()
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.SCORE,
             {"score" : math.floor(alliances.get(alliance).score), "alliance" : alliance})
    #TODO: send score update to scoreboard

def goal_bid(args):
    '''
    Update state for a goal being bid on and push information to scoreboard
    and to sensors
    '''
    alliance = args["alliance"]
    goal_name = args["goal"]
    if game_state == STATE.WAIT and not goals.get(goal_name).bid_timer.is_running():
        return
    goals.get(goal_name).bid(alliances.get(alliance))
    send_goal_owners_sensors()
    send_goal_costs_sensors()

def regenerate_codes(args=None):
    global curr_challenge_codes, curr_codegen_solutions
    for state, index in enumerate(dirty_codes):
        if state:
            _, curr_challenge_codes, curr_codegen_solutions = \
                    Codegen.get_new_code(curr_rfids, curr_challenge_codes, index)
            dirty_codes[index] = False

    lcm_send(LCM_TARGETS.DAWN, DAWN_HEADER.CODES, {"rfids" : curr_rfids,
                                                   "codes" : curr_challenge_codes,
                                                   "solutions" : curr_codegen_solutions})
    print("new codes")
    print(curr_codegen_solutions)
    print(dirty_codes)

def powerup_application(args):
    '''
    Update state for a code being input, return information to sensors
    to display result of code being decoded.
    Apply a powerup to a goal. Does not need to say result.
    '''
    global curr_challenge_codes, curr_codegen_solutions, dirty_codes
    alliance = alliances.get(args["alliance"])
    goal = goals.get(args["goal"])
    code = args["code"]
    print("code submitted")
    print(code)
    print(curr_codegen_solutions)

    try:
        index = curr_codegen_solutions.index(int(code))
    except ValueError:
        lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.CODE_RESULT, {"alliance" : alliance.name,
                                                                  "result" : 0})
        print("Incorrect code submitted")
        return
    if alliance.name == ALLIANCE_COLOR.BLUE and index > 2 or \
       alliance.name == ALLIANCE_COLOR.GOLD and index < 3:
        lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.CODE_RESULT, {"alliance" : alliance.name,
                                                                  "result" : 0})
        print("Code for wrong side")
        return

    powerup = powerup_functions[index]

    if powerup == POWERUP_TYPES.ZERO_X:
        if alliance.zero_x_cooldown.is_running():
            lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.CODE_RESULT, {"alliance" : alliance.name,
                                                                      "result" : 0})
            print("zero_x")
            return
        alliance.zero_x_cooldown.start_timer(CONSTANTS.CODE_COOLDOWN)
    elif powerup == POWERUP_TYPES.TWO_X:
        if alliance.two_x_cooldown.is_running():
            lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.CODE_RESULT, {"alliance" : alliance.name,
                                                                      "result" : 0})
            print("two_x")
            return
        alliance.two_x_cooldown.start_timer(CONSTANTS.CODE_COOLDOWN)
    elif powerup == POWERUP_TYPES.STEAL:
        if alliance.steal_cooldown.is_running() or \
           ((goal.owner is None or goal.owner == alliance) and game_state != STATE.AUTO):
            lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.CODE_RESULT, {"alliance" : alliance.name,
                                                                      "result" : 0})
            print("steal")
            return
        alliance.steal_cooldown.start_timer(CONSTANTS.CODE_COOLDOWN)

    dirty_codes[index] = True
    print(dirty_codes)
    if game_state == STATE.AUTO:
        alliance.increment_multiplier()
    elif game_state == STATE.TELEOP:
        goal.apply_powerup(powerup, alliance)
        lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.POWERUPS, {"alliance" : alliance.name,
                                                                      "goal" : goal.name,
                                                                      "powerup" : powerup})

    lcm_send(LCM_TARGETS.DAWN, DAWN_HEADER.CODES, {"rfids" : curr_rfids,
                                                   "codes" : curr_challenge_codes,
                                                   "solutions" : curr_codegen_solutions})
    lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.CODE_RESULT, {"alliance" : alliance.name,
                                                              "result" : 1})

def bid_complete(args):
    '''
    Update state when a bid timer ends and a bid is complete
    Update scoreboard and sensors with this information as well
    '''
    goal_name = args["goal"]
    alliance = goals.get(goal_name).current_bid_team
    goals.get(goal_name).set_owner(alliance)
    goals.get(goal_name).current_bid_team = None
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.BID_AMOUNT,
             {"goal" : goal_name, "alliance" : alliance.name, "bid" : 0})
    for goal in goals.values():
        if goal.owner is not None:
            continue
        if goal.current_bid_team == alliance and alliance.score < goal.current_bid:
            goal.current_bid = goal.previous_bid
            goal.current_bid_team = goal.previous_bid_team
            goal.previous_bid = goal.start_bid
            goal.previous_bid_team = None
            goal.next_bid = goal.calc_next_bid()
            lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.BID_AMOUNT,
                     {"goal" : goal.name,
                      "alliance" : goal.current_bid_team.name,
                      "bid" : goal.current_bid})
            #TODO: send current bid team to scoreboard
        if goal.current_bid_team is None:
            goal.bid_timer.reset()
            #TODO: send reset timer message to scoreboard

    send_team_scores_sensors()
    send_goal_owners_sensors()
    #TODO: send owner info and bid leader info to scoreboard

###########################################
# Event to Function Mappings for each Stage
###########################################

setup_functions = {
    SHEPHERD_HEADER.GENERATE_RFID : generate_rfids,
    SHEPHERD_HEADER.SETUP_MATCH: to_setup,
    SHEPHERD_HEADER.GET_MATCH_INFO : get_match,
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
    SHEPHERD_HEADER.GET_SCORES : get_score,
    SHEPHERD_HEADER.START_NEXT_STAGE : to_teleop
}

teleop_functions = {
    SHEPHERD_HEADER.GOAL_SCORE : goal_score,
    SHEPHERD_HEADER.GOAL_BID : goal_bid,
    SHEPHERD_HEADER.BID_TIMER_END : bid_complete,
    SHEPHERD_HEADER.RESET_MATCH : reset,
    SHEPHERD_HEADER.STAGE_TIMER_END : to_end,
    SHEPHERD_HEADER.POWERUP_APPLICATION : powerup_application,
    SHEPHERD_HEADER.CODE_COOLDOWN_END : regenerate_codes,
}

end_functions = {
    SHEPHERD_HEADER.RESET_MATCH : reset,
    SHEPHERD_HEADER.SCORE_ADJUST : score_adjust,
    SHEPHERD_HEADER.GET_SCORES : get_score,
    SHEPHERD_HEADER.SETUP_MATCH : to_setup,
    SHEPHERD_HEADER.GET_MATCH_INFO : get_match,
    SHEPHERD_HEADER.GENERATE_RFID : generate_rfids,
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
    GOAL.GOLD : Goal(GOAL.GOLD, CONSTANTS.GOAL_BASE_VALUE, 0),
}

rfid_pool = None
curr_rfids = None
powerup_functions = [POWERUP_TYPES.ZERO_X,
                     POWERUP_TYPES.TWO_X,
                     POWERUP_TYPES.STEAL,
                     POWERUP_TYPES.ZERO_X,
                     POWERUP_TYPES.TWO_X,
                     POWERUP_TYPES.STEAL]
events = None
curr_challenge_codes = None
curr_codegen_solutions = None
dirty_codes = [False, False, False, False, False, False]


def main():
    parser = argparse.ArgumentParser(description='PiE field control')
    parser.add_argument('--version', help='Prints out the Shepherd version number.',
                        action='store_true')
    flags = parser.parse_args()

    if flags.version:
        print('.'.join(map(str, __version__)))
    else:
        start()


if __name__ == '__main__':
    main()
