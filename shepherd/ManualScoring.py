from LCM import *
from Utils import *

def get_goal(goal_input, alliance):
    input_to_goal = {
        "a"     : GOAL.A,
        "b"     : GOAL.B,
        "c"     : GOAL.C,
        "d"     : GOAL.D,
        "e"     : GOAL.E,
        "g"     : "base",
    }
    alliance_to_base_goal = {
        ALLIANCE_COLOR.GOLD : GOAL.GOLD,
        ALLIANCE_COLOR.BLUE : GOAL.BLUE,
    }
    goal_name = input_to_goal.get(goal_input)
    if goal_name == "base":
        goal_name = alliance_to_base_goal.get(alliance)
    return goal_name

def get_alliance(alliance_input):
    input_to_alliance = {
        "gold"  : ALLIANCE_COLOR.GOLD,
        "blue"  : ALLIANCE_COLOR.BLUE,
    }
    return input_to_alliance.get(alliance_input)

def main():
    while True:
        event = input("Command: [gold|blue][a|b|c|d|e|g]")
        alliance = get_alliance(event[0:4])
        goal_name = get_goal(event[4], alliance)
        if alliance is None or goal_name is None:
            print("Invalid Input")
            continue
        lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.GOAL_SCORE,
                 {"alliance" : alliance, "goal" : goal_name})

if __name__ == "__main__":
    main()
