import argparse
import queue
import random
import time
import datetime
import traceback
from Alliance import *
from LCM import *
from Timer import *
from Utils import *
from Code import *
from runtimeclient import RuntimeClientManager
import Sheet
import bot
import audio
import RecipeManager


clients = RuntimeClientManager((), ())

__version__ = (1, 0, 0)


###########################################
# Evergreen Methods
###########################################

#pylint: disable=broad-except
def start():
    '''
    Main loop which processes the event queue and calls the appropriate function
    based on game state and the dictionary of available functions
    '''
    global LAST_HEADER
    global EVENTS
    EVENTS = queue.Queue()
    lcm_start_read(LCM_TARGETS.SHEPHERD, EVENTS)
    while True:
        print("GAME STATE OUTSIDE: ", GAME_STATE)
        time.sleep(0.1)
        payload = EVENTS.get(True)
        LAST_HEADER = payload
        print(payload)
        if GAME_STATE == STATE.SETUP:
            func = SETUP_FUNCTIONS.get(payload[0])
            if func is not None:
                func(payload[1])
            else:
                print("Invalid Event in Setup")
        elif GAME_STATE == STATE.AUTO:
            func = AUTO_FUNCTIONS.get(payload[0])
            if func is not None:
                func(payload[1])
            else:
                print("Invalid Event in Auto")
        elif GAME_STATE == STATE.WAIT:
            func = WAIT_FUNCTIONS.get(payload[0])
            if func is not None:
                func(payload[1])
            else:
                print("Invalid Event in Wait")
        elif GAME_STATE == STATE.TELEOP:
            func = TELEOP_FUNCTIONS.get(payload[0])
            if func is not None:
                func(payload[1])
            else:
                print("Invalid Event in Teleop")
        elif GAME_STATE == STATE.END:
            func = END_FUNCTIONS.get(payload[0])
            if func is not None:
                func(payload[1])
            else:
                print("Invalid Event in End")

#pylint: disable=too-many-locals
def to_setup(args):
    '''
    Move to the setup stage which is should push scores from previous game to spreadsheet,
    load the teams for the upcoming match, reset all state, and send information to scoreboard.
    By the end, should be ready to start match.
    '''
    global MATCH_NUMBER
    global GAME_STATE
    global STARTING_SPOTS

    b1_name, b1_num, b1_starting_spot = args["b1name"], args["b1num"], args["b1_starting_spot"]
    b2_name, b2_num, b2_starting_spot = args["b2name"], args["b2num"], args["b2_starting_spot"]
    g1_name, g1_num, g1_starting_spot = args["g1name"], args["g1num"], args["g1_starting_spot"]
    g2_name, g2_num, g2_starting_spot = args["g2name"], args["g2num"], args["g2_starting_spot"]

    g1_custom_ip = args["g1_custom_ip"] or None
    g2_custom_ip = args["g2_custom_ip"] or None
    b1_custom_ip = args["b1_custom_ip"] or None
    b2_custom_ip = args["b2_custom_ip"] or None

    STARTING_SPOTS = [b1_starting_spot, b2_starting_spot, g1_starting_spot, g2_starting_spot]

    if GAME_STATE == STATE.END:
        flush_scores()

    MATCH_NUMBER = args["match_num"]

    if ALLIANCES[ALLIANCE_COLOR.BLUE] is not None:
        reset()

    #code_setup()

    ALLIANCES[ALLIANCE_COLOR.BLUE] = Alliance(ALLIANCE_COLOR.BLUE, b1_name,
                                              b1_num, b2_name, b2_num, b1_custom_ip, b2_custom_ip)
    ALLIANCES[ALLIANCE_COLOR.GOLD] = Alliance(ALLIANCE_COLOR.GOLD, g1_name,
                                              g1_num, g2_name, g2_num, g1_custom_ip, g2_custom_ip)

    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.TEAMS, {
        "b1name" : b1_name, "b1num" : b1_num,
        "b2name" : b2_name, "b2num" : b2_num,
        "g1name" : g1_name, "g1num" : g1_num,
        "g2name" : g2_name, "g2num" : g2_num,
        "match_num" : MATCH_NUMBER})

    GAME_STATE = STATE.SETUP
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.STAGE, {"stage": GAME_STATE})
    print("ENTERING SETUP STATE")
    print({"blue_score" : ALLIANCES[ALLIANCE_COLOR.BLUE].score,
           "gold_score" : ALLIANCES[ALLIANCE_COLOR.GOLD].score})

def to_auto(args):
    '''
    Move to the autonomous stage where robots should begin autonomously.
    By the end, should be in autonomous state, allowing any function from this
    stage to be called and autonomous match timer should have begun.
    '''
    #pylint: disable= no-member
    global GAME_STATE
    global clients
    try:
        alternate_connections = (ALLIANCES[ALLIANCE_COLOR.BLUE].team_1_custom_ip,
                                 ALLIANCES[ALLIANCE_COLOR.BLUE].team_2_custom_ip,
                                 ALLIANCES[ALLIANCE_COLOR.GOLD].team_1_custom_ip,
                                 ALLIANCES[ALLIANCE_COLOR.GOLD].team_2_custom_ip)

        clients = RuntimeClientManager((
            int(ALLIANCES[ALLIANCE_COLOR.BLUE].team_1_number),
            int(ALLIANCES[ALLIANCE_COLOR.BLUE].team_2_number),
        ), (
            int(ALLIANCES[ALLIANCE_COLOR.GOLD].team_1_number),
            int(ALLIANCES[ALLIANCE_COLOR.GOLD].team_2_number),
        ), *alternate_connections)
        clients.set_MASTER_ROBOTS(MASTER_ROBOTS[ALLIANCE_COLOR.BLUE],
                                  MASTER_ROBOTS[ALLIANCE_COLOR.GOLD])
        clients.set_starting_zones(STARTING_SPOTS)
    except Exception as exc:
        log(exc)
        return
    GAME_TIMER.start_timer(CONSTANTS.AUTO_TIME + 2)
    GAME_STATE = STATE.AUTO
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.STAGE, {"stage": GAME_STATE})
    enable_robots(True)
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.STAGE_TIMER_START,
             {"time" : CONSTANTS.AUTO_TIME})
    print("ENTERING AUTO STATE")

def to_wait(args):
    '''
    Move to the waiting stage, between autonomous and teleop periods.
    By the end, should be in wait state and the robots should be disabled.
    Some years, there might be methods that can be called once in the wait stage
    '''
    global GAME_STATE
    GAME_STATE = STATE.WAIT
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.STAGE, {"stage": GAME_STATE})
    disable_robots()
    print("ENTERING WAIT STATE")

def to_teleop(args):
    '''
    Move to teleoperated stage where robots are enabled and controlled manually.
    By the end, should be in teleop state and the teleop match timer should be started.
    '''
    global GAME_STATE
    global tstart
    tstart = datetime.datetime.now()
    GAME_STATE = STATE.TELEOP
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.STAGE, {"stage": GAME_STATE})

    Timer.reset_all()
    GAME_TIMER.start_timer(CONSTANTS.TELEOP_TIME + 2)

    enable_robots(False)
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.STAGE_TIMER_START,
             {"time" : CONSTANTS.TELEOP_TIME})
    print("ENTERING TELEOP STATE")

def to_end(args):
    '''
    Move to end stage after the match ends. Robots should be disabled here
    and final score adjustments can be made.
    '''
    global GAME_STATE
    lcm_send(LCM_TARGETS.UI, UI_HEADER.SCORES,
             {"blue_score" : math.floor(ALLIANCES[ALLIANCE_COLOR.BLUE].score),
              "gold_score" : math.floor(ALLIANCES[ALLIANCE_COLOR.GOLD].score)})
    GAME_STATE = STATE.END
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.STAGE, {"stage": GAME_STATE})
    disable_robots()
    print("ENTERING END STATE")

def reset(args=None):
    '''
    Resets the current match, moving back to the setup stage but with the current teams loaded in.
    Should reset all state being tracked by Shepherd.
    ****THIS METHOD MIGHT NEED UPDATING EVERY YEAR BUT SHOULD ALWAYS EXIST****
    '''
    global GAME_STATE, EVENTS, clients
    GAME_STATE = STATE.SETUP
    Timer.reset_all()
    EVENTS = queue.Queue()
    lcm_start_read(LCM_TARGETS.SHEPHERD, EVENTS)
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.RESET_TIMERS)
    for alliance in ALLIANCES.values():
        if alliance is not None:
            alliance.reset()
    send_connections(None)
    #STARTING_SPOTS = ["unknown", "unknown", "unknown", "unknown"]
    clients = RuntimeClientManager((), ())
    disable_robots()
    BUTTONS['gold_1'] = False
    BUTTONS['gold_2'] = False
    BUTTONS['blue_1'] = False
    BUTTONS['blue_2'] = False
    lcm_send(LCM_TARGETS.TABLET, TABLET_HEADER.RESET)
    lcm_send(LCM_TARGETS.DAWN, DAWN_HEADER.RESET)
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
    ALLIANCES[ALLIANCE_COLOR.BLUE].score = blue_score
    ALLIANCES[ALLIANCE_COLOR.GOLD].score = gold_score
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.SCORE,
             {"alliance" : ALLIANCES[ALLIANCE_COLOR.BLUE].name,
              "score" : math.floor(ALLIANCES[ALLIANCE_COLOR.BLUE].score)})
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.SCORE,
             {"alliance" : ALLIANCES[ALLIANCE_COLOR.GOLD].name,
              "score" : math.floor(ALLIANCES[ALLIANCE_COLOR.GOLD].score)})

def get_score(args):
    '''
    Send the current blue and gold score to the UI
    '''
    if ALLIANCES[ALLIANCE_COLOR.BLUE] is None:
        lcm_send(LCM_TARGETS.UI, UI_HEADER.SCORES,
                 {"blue_score" : None,
                  "gold_score" : None})
    else:
        lcm_send(LCM_TARGETS.UI, UI_HEADER.SCORES,
                 {"blue_score" : math.floor(ALLIANCES[ALLIANCE_COLOR.BLUE].score),
                  "gold_score" : math.floor(ALLIANCES[ALLIANCE_COLOR.GOLD].score)})

def flush_scores():
    '''
    Sends the most recent match score to the spreadsheet if connected to the internet
    '''
    if ALLIANCES[ALLIANCE_COLOR.BLUE] is not None:
        Sheet.write_scores(MATCH_NUMBER, ALLIANCES[ALLIANCE_COLOR.BLUE].score,
                           ALLIANCES[ALLIANCE_COLOR.GOLD].score)
    return -1

def enable_robots(autonomous):
    '''
    Sends message to Dawn to enable all robots. The argument should be a boolean
    which is true if we are entering autonomous mode
    '''
    try:
        clients.set_mode("auto" if autonomous else "teleop")
    except Exception as exc:
        for client in clients.clients:
            try:
                client.set_mode("auto" if autonomous else "teleop")
            except Exception as exc:
                print("A robot failed to be enabled! Big sad :(")
                log(exc)

def disable_robots():
    '''
    Sends message to Dawn to disable all robots
    '''
    try:
        clients.set_mode("idle")
    except Exception as exc:
        for client in clients.clients:
            try:
                client.set_mode("idle")
            except Exception as exc:
                print("a client has disconnected")
        log(exc)
        print(exc)

#pylint: disable=redefined-builtin
def log(Exception):
    global LAST_HEADER
    # if Shepherd.MATCH_NUMBER <= 0:
    #     return
    now = datetime.datetime.now()
    filename = str(now.month) + "-" + str(now.day) + "-" + str(now.year) +\
               "-match-" + str(MATCH_NUMBER) + ".txt"
    print("a normally fatal exception occured, but Shepherd will continue to run")
    print("all known details are logged to logs/"+filename)
    file = open("logs/"+filename, "a+")
    file.write("\n========================================\n")
    file.write("a normally fatal exception occured.\n")
    file.write("all relevant data may be found below.\n")
    file.write("match: " + str(MATCH_NUMBER)+"\n")
    file.write("game state: " + str(GAME_STATE)+"\n")
    file.write("gold alliance: " + str(ALLIANCES[ALLIANCE_COLOR.GOLD])+"\n")
    file.write("blue alliance: " + str(ALLIANCES[ALLIANCE_COLOR.BLUE])+"\n")
    file.write("game timer running?: " + str(GAME_TIMER.is_running())+"\n")
    file.write("the last received header was:" + str(LAST_HEADER)+"\n")
    file.write("a stacktrace of the error may be found below\n")
    file.write(str(Exception))
    file.write(str(traceback.format_exc()))
    file.close()

###########################################
# Game Specific Methods
###########################################
def disable_robot(args):
    '''
    Send message to Dawn to disable the robots of team
    '''
    try:
        team_number = args["team_number"]
        client = clients.clients[int(team_number)]
        if client:
            client.set_mode("idle")
    except Exception as exc:
        log(exc)


def set_master_robot(args):
    '''
    Set the master robot of the alliance
    '''
    alliance = args["alliance"]
    team_number = args["team_num"]
    MASTER_ROBOTS[alliance] = team_number
    msg = {"alliance": alliance, "team_number": int(team_number)}
    lcm_send(LCM_TARGETS.DAWN, DAWN_HEADER.MASTER, msg)

def final_score(args):
    '''
    send shepherd the final score, send score to scoreboard
    '''
    blue_final = args['blue_score']
    gold_final = args['gold_score']
    ALLIANCES[ALLIANCE_COLOR.GOLD].score = gold_final
    ALLIANCES[ALLIANCE_COLOR.BLUE].score = blue_final
    msg = {"alliance": ALLIANCE_COLOR.GOLD, "amount": gold_final}
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.SCORE, msg)
    msg = {"alliance": ALLIANCE_COLOR.BLUE, "amount": blue_final}
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.SCORE, msg)

def set_connections(args):
    """Set connections"""
    #pylint: disable=undefined-variable, not-an-iterable
    team = args["team_number"]
    connection = boolean(args["connection"])
    dirty = False
    for alliance in ALLIANCES.values:
        if team == alliance.team_1_number:
            if alliance.team_1_connection != connection:
                alliance.team_1_connection = connection
                dirty = True
        if team == alliance.team_2_number:
            if alliance.team_2_connection != connection:
                alliance.team_2_connection = connection
                dirty = True
    if dirty:
        send_connections(None)

def send_connections(args):
    """Send connections"""
    pass #pylint: disable=unnecessary-pass
    # msg = {"g_1_connection" : ALLIANCES[ALLIANCE_COLOR.GOLD].team_1_connection,
    #        "g_2_connection" : ALLIANCES[ALLIANCE_COLOR.GOLD].team_2_connection,
    #        "b_1_connection" : ALLIANCES[ALLIANCE_COLOR.BLUE].team_1_connection,
    #        "b_2_connection" : ALLIANCES[ALLIANCE_COLOR.BLUE].team_2_connection}
    # lcm_send(LCM_TARGETS.UI, UI_HEADER.CONNECTIONS, msg)

def submit_recipe(args):
    """
    Map colors to foods, check recipe correctness, increment the number of
    recipes completed, store time in the recipe_times array, and update the
    scoreboard of the resulting changes
    """
    t_end = datetime.datetime.now()
    tdiff = t_end-tstart
    color1, color2, color3 = args["color1"], args["color2"], args["color3"]
    side = args["side"]
    fcolor1 = CONSTANTS.COLOR_DICTIONARY[color1]
    fcolor2 = CONSTANTS.COLOR_DICTIONARY[color2]
    fcolor3 = CONSTANTS.COLOR_DICTIONARY[color3]
    #pylint: disable=broad-except
    ingredients = [fcolor1, fcolor2, fcolor3]
    #pylint: disable=no-member
    if RecipeManager.check_recipe(side, ingredients):
        ALLIANCES[side].recipe_times.append(tdiff)
        ALLIANCES[side].recipe_count += 1
        msg = {"recipe_count":1, "time_taken":tdiff}
        lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.FINISHED_RECIPE, msg)

def oven_done(args):
    side = args["side"]
    ALLIANCES[side].cooked += 1

def oven_auto(args):
    pass

def oven_teleop(args):
    pass

def rats(side):
    ALLIANCES[side].num_rats += 1
    ALLIANCES[other_side(side)].num_rats -= 1

def king_rat(side):
    other = other_side(side)
    ALLIANCES[side].king_rat = 1
    if ALLIANCES[other].king_rats != 0:
        ALLIANCES[other].king_rat = 0

def other_side(side):
    if side == ALLIANCE_COLOR.GOLD:
        return ALLIANCE_COLOR.BLUE
    return ALLIANCE_COLOR.GOLD

###########################################
# Event to Function Mappings for each Stage
###########################################

SETUP_FUNCTIONS = {
    SHEPHERD_HEADER.SETUP_MATCH: to_setup,
    SHEPHERD_HEADER.SCORE_ADJUST : score_adjust,
    SHEPHERD_HEADER.GET_MATCH_INFO : get_match,
    SHEPHERD_HEADER.START_NEXT_STAGE: to_auto
}

AUTO_FUNCTIONS = {
    SHEPHERD_HEADER.RESET_MATCH : reset,
    SHEPHERD_HEADER.STAGE_TIMER_END : to_wait,
    #SHEPHERD_HEADER.CODE_APPLICATION : auto_apply_code,
    SHEPHERD_HEADER.ROBOT_OFF : disable_robot,
    #SHEPHERD_HEADER.CODE_RETRIEVAL : bounce_code,
    SHEPHERD_HEADER.ROBOT_CONNECTION_STATUS: set_connections,
    SHEPHERD_HEADER.REQUEST_CONNECTIONS: send_connections,
    SHEPHERD_HEADER.OVEN_PRESS: oven_auto

    }

WAIT_FUNCTIONS = {
    SHEPHERD_HEADER.RESET_MATCH : reset,
    SHEPHERD_HEADER.SCORE_ADJUST : score_adjust,
    SHEPHERD_HEADER.GET_SCORES : get_score,
    SHEPHERD_HEADER.START_NEXT_STAGE : to_teleop,
    SHEPHERD_HEADER.ROBOT_CONNECTION_STATUS: set_connections,
    SHEPHERD_HEADER.REQUEST_CONNECTIONS: send_connections
}

TELEOP_FUNCTIONS = {
    SHEPHERD_HEADER.RESET_MATCH : reset,
    SHEPHERD_HEADER.STAGE_TIMER_END : to_end,
    #SHEPHERD_HEADER.CODE_APPLICATION : apply_code,
    SHEPHERD_HEADER.ROBOT_OFF : disable_robot,
    #SHEPHERD_HEADER.CODE_RETRIEVAL : bounce_code,
    SHEPHERD_HEADER.ROBOT_CONNECTION_STATUS: set_connections,
    SHEPHERD_HEADER.REQUEST_CONNECTIONS: send_connections,
    SHEPHERD_HEADER.SUBMIT_RECIPE: submit_recipe,
    SHEPHERD_HEADER.RATS: rats,
    SHEPHERD_HEADER.KING_RATS: king_rat,
    SHEPHERD_HEADER.OVEN_PRESS: oven_done,
    SHEPHERD_HEADER.OVEN_TELEOP: oven_teleop
}

END_FUNCTIONS = {
    SHEPHERD_HEADER.RESET_MATCH : reset,
    SHEPHERD_HEADER.SCORE_ADJUST : score_adjust,
    SHEPHERD_HEADER.GET_SCORES : get_score,
    SHEPHERD_HEADER.SETUP_MATCH : to_setup,
    SHEPHERD_HEADER.GET_MATCH_INFO : get_match,
    SHEPHERD_HEADER.FINAL_SCORE : final_score,
    SHEPHERD_HEADER.ROBOT_CONNECTION_STATUS: set_connections,
    SHEPHERD_HEADER.REQUEST_CONNECTIONS: send_connections
}

###########################################
# Evergreen Variables
###########################################

GAME_STATE = STATE.END
GAME_TIMER = Timer(TIMER_TYPES.MATCH)

MATCH_NUMBER = -1
ALLIANCES = {ALLIANCE_COLOR.GOLD: None, ALLIANCE_COLOR.BLUE: None}
EVENTS = None

LAST_HEADER = None

###########################################
# Game Specific Variables
###########################################
BUTTONS = {'gold_1': False, 'gold_2': False, 'blue_1': False, 'blue_2': False}
STARTING_SPOTS = ["unknown", "unknown", "unknown", "unknown"]
MASTER_ROBOTS = {ALLIANCE_COLOR.BLUE: None, ALLIANCE_COLOR.GOLD: None}

STUDENT_DECODE_TIMER = Timer(TIMER_TYPES.STUDENT_DECODE)

CODES_USED = []

tstart = 0

#nothing

def main():
    """Main function"""
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
