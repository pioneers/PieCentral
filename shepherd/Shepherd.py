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
        elif GAME_STATE == STATE.PERK_SELCTION:
            func = PERK_SELECTION_FUNCTIONS.get(payload[0])
            if func is not None:
                func(payload[1])
            else:
                print("Invalid Event in Perk_selection")
        elif GAME_STATE == STATE.AUTO_WAIT:
            func = AUTO_WAIT_FUNCTIONS.get(payload[0])
            if func is not None:
                func(payload[1])
            else:
                print("Invalid Event in Auto_wait")
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

    code_setup()

    ALLIANCES[ALLIANCE_COLOR.BLUE] = Alliance(ALLIANCE_COLOR.BLUE, b1_name,
                                              b1_num, b2_name, b2_num, b1_custom_ip, b2_custom_ip)
    ALLIANCES[ALLIANCE_COLOR.GOLD] = Alliance(ALLIANCE_COLOR.GOLD, g1_name,
                                              g1_num, g2_name, g2_num, g1_custom_ip, g2_custom_ip)

    msg = {"b1num":b1_num, "b2num":           b2_num, "g1num":g1_num, "g2num":g2_num}
    lcm_send(LCM_TARGETS.TABLET, TABLET_HEADER.TEAMS, msg)

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


def to_perk_selection(args):
    bot.announce_next_match(int(MATCH_NUMBER))

    global GAME_STATE
    GAME_TIMER.start_timer(CONSTANTS.PERK_SELECTION_TIME + 2)
    GAME_STATE = STATE.PERK_SELCTION
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.STAGE, {"stage": GAME_STATE})
    lcm_send(LCM_TARGETS.TABLET, TABLET_HEADER.COLLECT_PERKS)
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.STAGE_TIMER_START,
             {"time" : CONSTANTS.PERK_SELECTION_TIME})
    print("ENTERING PERK SELECTION STATE")
    # audio.play_perk_music()

def to_auto_wait(args):
    global GAME_STATE
    GAME_STATE = STATE.AUTO_WAIT
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.STAGE, {"stage": GAME_STATE})
    lcm_send(LCM_TARGETS.TABLET, TABLET_HEADER.COLLECT_CODES)
    print("ENTERING AUTO_WAIT STATE")

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
    GAME_STATE = STATE.TELEOP
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.STAGE, {"stage": GAME_STATE})

    Timer.reset_all()
    GAME_TIMER.start_timer(CONSTANTS.TELEOP_TIME + 2)
    overdrive_time = random.randint(0, CONSTANTS.TELEOP_TIME -
                                    CONSTANTS.OVERDRIVE_TIME)
    OVERDRIVE_TIMER.start_timer(overdrive_time)
    overdrive_time = CONSTANTS.TELEOP_TIME - overdrive_time
    print("overdrive will happen at " + str(overdrive_time // 60) + ":" +
          str(overdrive_time % 60))

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
    file.write("extended teleop timer running?: " + str(EXTENDED_TELEOP_TIMER.is_running())+"\n")
    file.write("launch button timers running(g1 g2 b1 b2)?: " +
               str(LAUNCH_BUTTON_TIMER_GOLD_1.is_running()) + " " +
               str(LAUNCH_BUTTON_TIMER_GOLD_2.is_running()) + " " +
               str(LAUNCH_BUTTON_TIMER_BLUE_1.is_running()) + " " +
               str(LAUNCH_BUTTON_TIMER_BLUE_2.is_running())+"\n")
    file.write("overdrive timer active?: " + str(OVERDRIVE_TIMER.is_running())+"\n")
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

def next_code():
    if CODES_USED == []:
        CODES_USED.append(codes[0])
        return codes[0]
    index = len(CODES_USED)
    CODES_USED.append(codes[index])
    return codes[index]

def code_setup():
    '''
    Set up code_solution and code_effect dictionaries and send code_solution to Dawn
    '''
    global code_solution
    global code_effect
    code_solution = assign_code_solution()
    code_effect = assign_code_effect()

def bounce_code(args):
    """bounce the code"""
    try:
        student_solutions = clients.get_challenge_solutions()
        print(student_solutions)
        for ss in student_solutions.keys():
            if student_solutions[ss] is not None:
                alliance = None
                if int(ALLIANCES[ALLIANCE_COLOR.BLUE].team_1_number) == int(ss):
                    alliance = ALLIANCE_COLOR.BLUE
                if int(ALLIANCES[ALLIANCE_COLOR.GOLD].team_1_number) == int(ss):
                    alliance = ALLIANCE_COLOR.GOLD
                if int(ALLIANCES[ALLIANCE_COLOR.BLUE].team_2_number) == int(ss):
                    alliance = ALLIANCE_COLOR.BLUE
                if int(ALLIANCES[ALLIANCE_COLOR.GOLD].team_2_number) == int(ss):
                    alliance = ALLIANCE_COLOR.GOLD
                msg = {"alliance": alliance, "result": student_solutions[ss]}
                lcm_send(LCM_TARGETS.TABLET, TABLET_HEADER.CODE, msg)
    except Exception as exc:
        log(exc)

def auto_apply_code(args):
    '''
    Send Scoreboard the effect if the answer is correct
    '''
    alliance = ALLIANCES[args["alliance"]]
    answer = int(args["answer"])
    print('Codegen answers:', answer, code_solution)
    if (answer is not None and answer in code_solution.values()):
        #code = [k for k, v in code_solution.items() if v == answer][0]
        alliance.change_score(10)
    else:
        msg = {"alliance": alliance.name}
        lcm_send(LCM_TARGETS.SENSORS, SENSORS_HEADER.FAILED_POWERUP, msg)
        # msg2 = {"alliance": alliance.name, "feedback": False}
        # lcm_send(LCM_TARGETS.TABLET, TABLET_HEADER.CODE_FEEDBACK, msg2)
def apply_code(args):
    '''
    Send Scoreboard the new score if the answer is correct #TODO
    '''
    alliance = ALLIANCES[args["alliance"]]
    answer = int(args["answer"])
    if (answer is not None and answer in code_solution.values()):
        code = [k for k, v in code_solution.items() if v == answer][0]
        if code_effect[code] == EFFECTS.TWIST:
            if alliance.name == ALLIANCE_COLOR.BLUE:
                msg = {"alliance": ALLIANCE_COLOR.GOLD, "effect": code_effect[code]}
            else:
                msg = {"alliance": ALLIANCE_COLOR.BLUE, "effect": code_effect[code]}
        else:
            msg = {"alliance": alliance.name, "effect": code_effect[code]}
        lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.APPLIED_EFFECT, msg)
    else:
        msg = {"alliance": alliance.name}
        # msg2 = {"alliance": alliance.name, "feedback": False}
        lcm_send(LCM_TARGETS.SENSORS, SENSORS_HEADER.FAILED_POWERUP, msg)
        # lcm_send(LCM_TARGETS.TABLET, TABLET_HEADER.CODE_FEEDBACK, msg2)


def end_teleop(args):
    """Ending teleop"""
    blue_robots_disabled = False
    gold_robots_disabled = False
    if PERKS.TAFFY not in alliance_perks(ALLIANCES[ALLIANCE_COLOR.BLUE]):
        blue_robots_disabled = True
    if PERKS.TAFFY not in alliance_perks(ALLIANCES[ALLIANCE_COLOR.GOLD]):
        gold_robots_disabled = True
    if (PERKS.TAFFY in alliance_perks(ALLIANCES[ALLIANCE_COLOR.BLUE]) or PERKS.TAFFY
            in alliance_perks(ALLIANCES[ALLIANCE_COLOR.GOLD])):
        EXTENDED_TELEOP_TIMER.start_timer(CONSTANTS.TAFFY_TIME)
        lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.STAGE_TIMER_START,
                 {"time" : CONSTANTS.TAFFY_TIME})
    else:
        to_end(args)
    if gold_robots_disabled:
        disable_robot({"team_number":ALLIANCES[ALLIANCE_COLOR.GOLD].team_1_number})
        disable_robot({"team_number":ALLIANCES[ALLIANCE_COLOR.GOLD].team_2_number})
    if blue_robots_disabled:
        disable_robot({"team_number":ALLIANCES[ALLIANCE_COLOR.BLUE].team_1_number})
        disable_robot({"team_number":ALLIANCES[ALLIANCE_COLOR.BLUE].team_2_number})

def alliance_perks(alliance):
    return (alliance.perk_1, alliance.perk_2, alliance.perk_3)

def apply_perks(args):
    alliance = ALLIANCES[args['alliance']]
    alliance.perk_1 = args['perk_1']
    alliance.perk_2 = args['perk_2']
    alliance.perk_3 = args['perk_3']
    msg = {"alliance": args['alliance'], "perk_1":args['perk_1'],
           "perk_2":args['perk_2'], "perk_3":args['perk_3']}
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.PERKS_SELECTED, msg)

def launch_button_triggered(args):
    '''
    check if allowed once every 30 seconds, give one of the codes to the correct
    alliance through Dawn, update scoreboard
    '''
    try:
        alliance = ALLIANCES[args['alliance']]
        button = args["button"]
        l_b = alliance.name + "_" + str(button)
        if not TIMER_DICTIONARY[l_b].is_running():
            msg = {"alliance": alliance.name, "button": button}
            code = next_code()
            client = clients.clients[int(MASTER_ROBOTS[alliance.name])]
            if client:
                client.run_challenge(code)
            STUDENT_DECODE_TIMER.start_timer(CONSTANTS.STUDENT_DECODE_TIME)
            TIMER_DICTIONARY[l_b].start_timer(CONSTANTS.COOLDOWN)
            lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.LAUNCH_BUTTON_TIMER_START, msg)
    except Exception as exc:
        log(exc)

def auto_launch_button_triggered(args):
    """trigger automatic launch button"""
    ##  mark button as dirty, sent to sc (both things)
    ## Isn't this already done in auto_apply_code?
    try:
        alliance = ALLIANCES[args['alliance']]
        button = args["button"]
        temp_str = alliance.name + "_" + str(button)
        if not BUTTONS[temp_str]:
            msg = {"alliance": alliance.name, "button": button}
            code = next_code()
            client = clients.clients[int(MASTER_ROBOTS[alliance.name])]
            if client:
                client.run_challenge(code, timeout=1)

            STUDENT_DECODE_TIMER.start_timer(CONSTANTS.STUDENT_DECODE_TIME)
            BUTTONS[temp_str] = True
            msg = {"alliance": alliance.name, "button": button}
            lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.LAUNCH_BUTTON_TIMER_START, msg)
    except Exception as exc:
        log(exc)


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


def overdrive_triggered(args):
    """Trigger Overdrive"""
    size = random.choice(CONSTANTS.CRATE_SIZES)
    msg = {"size": size}
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.OVERDRIVE_START, msg)
    print("overdrive is active for the next 30 seconds for "+size+" size crates.")
    audio.play_horn()

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

###########################################
# Event to Function Mappings for each Stage
###########################################

SETUP_FUNCTIONS = {
    SHEPHERD_HEADER.SETUP_MATCH: to_setup,
    SHEPHERD_HEADER.SCORE_ADJUST : score_adjust,
    SHEPHERD_HEADER.GET_MATCH_INFO : get_match,
    SHEPHERD_HEADER.START_NEXT_STAGE: to_perk_selection
}

PERK_SELECTION_FUNCTIONS = {
    SHEPHERD_HEADER.RESET_MATCH : reset,
    SHEPHERD_HEADER.APPLY_PERKS: apply_perks,
    SHEPHERD_HEADER.MASTER_ROBOT: set_master_robot,
    SHEPHERD_HEADER.STAGE_TIMER_END: to_auto_wait,
    SHEPHERD_HEADER.ROBOT_CONNECTION_STATUS: set_connections,
    SHEPHERD_HEADER.REQUEST_CONNECTIONS: send_connections
}

AUTO_WAIT_FUNCTIONS = {
    SHEPHERD_HEADER.RESET_MATCH : reset,
    SHEPHERD_HEADER.SCORE_ADJUST : score_adjust,
    SHEPHERD_HEADER.APPLY_PERKS: apply_perks,
    SHEPHERD_HEADER.MASTER_ROBOT: set_master_robot,
    SHEPHERD_HEADER.CODE_APPLICATION : auto_apply_code,
    SHEPHERD_HEADER.GET_SCORES : get_score,
    SHEPHERD_HEADER.START_NEXT_STAGE : to_auto,
    SHEPHERD_HEADER.ROBOT_CONNECTION_STATUS: set_connections,
    SHEPHERD_HEADER.REQUEST_CONNECTIONS: send_connections
}

AUTO_FUNCTIONS = {
    SHEPHERD_HEADER.RESET_MATCH : reset,
    SHEPHERD_HEADER.STAGE_TIMER_END : to_wait,
    SHEPHERD_HEADER.LAUNCH_BUTTON_TRIGGERED : auto_launch_button_triggered,
    SHEPHERD_HEADER.CODE_APPLICATION : auto_apply_code,
    SHEPHERD_HEADER.ROBOT_OFF : disable_robot,
    SHEPHERD_HEADER.CODE_RETRIEVAL : bounce_code,
    SHEPHERD_HEADER.ROBOT_CONNECTION_STATUS: set_connections,
    SHEPHERD_HEADER.REQUEST_CONNECTIONS: send_connections

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
    SHEPHERD_HEADER.STAGE_TIMER_END : end_teleop,
    SHEPHERD_HEADER.LAUNCH_BUTTON_TRIGGERED : launch_button_triggered,
    SHEPHERD_HEADER.CODE_APPLICATION : apply_code,
    SHEPHERD_HEADER.ROBOT_OFF : disable_robot,
    SHEPHERD_HEADER.END_EXTENDED_TELEOP : to_end,
    SHEPHERD_HEADER.TRIGGER_OVERDRIVE : overdrive_triggered,
    SHEPHERD_HEADER.CODE_RETRIEVAL : bounce_code,
    SHEPHERD_HEADER.ROBOT_CONNECTION_STATUS: set_connections,
    SHEPHERD_HEADER.REQUEST_CONNECTIONS: send_connections

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
EXTENDED_TELEOP_TIMER = Timer(TIMER_TYPES.EXTENDED_TELEOP)

MATCH_NUMBER = -1
ALLIANCES = {ALLIANCE_COLOR.GOLD: None, ALLIANCE_COLOR.BLUE: None}
EVENTS = None

LAST_HEADER = None

###########################################
# Game Specific Variables
###########################################
BUTTONS = {'gold_1': False, 'gold_2': False, 'blue_1': False, 'blue_2': False}
STARTING_SPOTS = ["unknown", "unknown", "unknown", "unknown"]
LAUNCH_BUTTON_TIMER_GOLD_1 = Timer(TIMER_TYPES.LAUNCH_BUTTON)
LAUNCH_BUTTON_TIMER_GOLD_2 = Timer(TIMER_TYPES.LAUNCH_BUTTON)
LAUNCH_BUTTON_TIMER_BLUE_1 = Timer(TIMER_TYPES.LAUNCH_BUTTON)
LAUNCH_BUTTON_TIMER_BLUE_2 = Timer(TIMER_TYPES.LAUNCH_BUTTON)
TIMER_DICTIONARY = {'gold_1': LAUNCH_BUTTON_TIMER_GOLD_1, 'gold_2': LAUNCH_BUTTON_TIMER_GOLD_2,
                    'blue_1': LAUNCH_BUTTON_TIMER_BLUE_1, 'blue_2': LAUNCH_BUTTON_TIMER_BLUE_2}
MASTER_ROBOTS = {ALLIANCE_COLOR.BLUE: None, ALLIANCE_COLOR.GOLD: None}

STUDENT_DECODE_TIMER = Timer(TIMER_TYPES.STUDENT_DECODE)

OVERDRIVE_TIMER = Timer(TIMER_TYPES.OVERDRIVE_DELAY)
CODES_USED = []

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
