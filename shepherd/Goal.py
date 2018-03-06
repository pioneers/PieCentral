import math
from Utils import *
from Timer import *
from LCM import *

class Goal:
    """This class holds the state values for the goal, such as its point value,
       it's multipliers, and it's alliance.
            name - A String holding the name of the goal
            value - An Integer representing the inherent point value of the Goal
            owner - An Alliance object representing the current owner of
                    the goal
            current_bid - An Integer representing the value of the current bid
                          on this goal
            current_bid_team - An Alliance object representing the team that
                               has submited the most recent bid
            previous_bid - An Integer representing the value of the previous
                           bid
            previous_bid_team - An Alliance object representing the team that
                                made the previous bid
            bid_timer - A timer tracking the time left to bid
            gold_two_x_timer - A Timer tracking how long the 2x powerup applied
                               by the gold team will last
            gold_zero_x_timer - A Timer tracking how long the 0x powerup
                                applied by the gold team will last
            blue_two_x_timer - A Timer tracking how long the 2x powerup applied
                               by the blue team will last
            blue_zero_x_timer - A Timer tracking how long the 0x powerup applied
                                by the blue team will last
    """
    def __init__(self, name, value, start_bid):
        self.name = name
        self.initial_value = value
        self.value = value
        self.owner = None
        self.start_bid = start_bid
        self.current_bid = self.start_bid
        self.current_bid_team = None
        self.previous_bid = self.start_bid
        self.previous_bid_team = None
        self.next_bid = self.start_bid
        self.bid_timer = Timer(TIMER_TYPES.BID, name)
        self.gold_two_x_timer = Timer(TIMER_TYPES.DURATION)
        self.gold_zero_x_timer = Timer(TIMER_TYPES.DURATION)
        self.blue_two_x_timer = Timer(TIMER_TYPES.DURATION)
        self.blue_zero_x_timer = Timer(TIMER_TYPES.DURATION)

    def calc_next_bid(self):
        return math.floor((self.current_bid * CONSTANTS.BID_INCREASE_CONSTANT) + 0.5)

    def reset(self):
        self.value = self.initial_value
        self.owner = None
        self.current_bid = self.start_bid
        self.current_bid_team = None
        self.previous_bid = self.start_bid
        self.previous_bid_team = None
        self.next_bid = self.start_bid
        self.bid_timer.reset()
        self.gold_zero_x_timer.reset()
        self.gold_two_x_timer.reset()
        self.blue_two_x_timer.reset()
        self.blue_zero_x_timer.reset()
        lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.GOAL_OWNED,
                 {"goal" : self.name, "alliance" : None})
        lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.BID_AMOUNT,
                 {"goal" : self.name, "alliance" : None, "bid"
                  : self.next_bid})
        #TODO: Send info to sensors about reset
        #TODO: Send info to UI about reset

    def set_autonomous(self):
        self.value = self.initial_value * 2
        self.current_bid = self.start_bid / 2
        self.next_bid = self.current_bid

    def set_teleop(self):
        self.value = self.initial_value
        self.current_bid = self.start_bid
        self.next_bid = self.start_bid

    def set_owner(self, alliance):
        self.owner = alliance
        if self.name != GOAL.BLUE and self.name != GOAL.GOLD:
            alliance.score -= self.current_bid

        #TODO: send updated score to scoreboard and sensors
        lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.GOAL_OWNED,
                 {"goal" : self.name, "alliance" : self.owner.name})

    def bid(self, alliance):
        if self.owner is not None:
            return
        if self.current_bid_team == alliance:
            return
        if alliance.score < self.next_bid:
            return

        self.previous_bid = self.current_bid
        self.current_bid = self.next_bid
        self.next_bid = self.calc_next_bid()

        self.previous_bid_team = self.current_bid_team
        self.current_bid_team = alliance

        if self.bid_timer.is_running():
            time_increase = CONSTANTS.BID_TIME_INCREASE
        else:
            time_increase = CONSTANTS.BID_TIME_INITIAL

        self.bid_timer.start_timer(time_increase)
        lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.BID_AMOUNT,
                 {"goal" : self.name,
                  "alliance" : self.current_bid_team.name,
                  "bid" : self.next_bid})
        lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.BID_TIMER,
                 {"goal" : self.name, "time" : time_increase})
        #TODO: Send bid amount, and curr bid owner to sensors


    def score(self, alliance):
        """ modifies the owner alliance's score based on the value of the goal,
            the current multipliers,and the alliances multiplier, if the
            scoring Alliance is the owning alliance.

            alliance - Alliance object representing the scoring team
        """
        if self.owner is alliance:
            alliance.change_score(self.value * self.calc_multiplier() *\
                alliance.alliance_multiplier + 0.0001)

    def calc_multiplier(self):
        """ returns an integer that represents the overall multiplier for this
            goal, by checking each timer in the goal
        """
        multiplier = 1
        if self.gold_two_x_timer.is_running():
            multiplier *= 2
        if self.blue_two_x_timer.is_running():
            multiplier *= 2
        if self.gold_zero_x_timer.is_running():
            multiplier *= 0
        if self.blue_zero_x_timer.is_running():
            multiplier *= 0
        return multiplier

    def apply_powerup(self, effect, alliance):
        """ applies effect passed in from an alliance, and determines what
            should happen, based on the allianced passed in, and the alliance
            of the goal.
            effect - enum representing an effect to be applied to the goal
            alliance - the alliance trying to apply the effect to the goal
        """

        def process_powerup(blue_timer, gold_timer, constants_cooldown, powerup_type):
            if alliance.name == ALLIANCE_COLOR.BLUE:
                blue_timer.start_timer(constants_cooldown)
                lcm_send(LCM_TARGETS.SCOREBOARD,
                         SCOREBOARD_HEADER.POWERUPS,
                         {"goal" : self.name,
                          "alliance" : alliance.name,
                          "powerup" : powerup_type})
            elif alliance.name == ALLIANCE_COLOR.GOLD:
                gold_timer.start_timer(constants_cooldown)

                lcm_send(LCM_TARGETS.SCOREBOARD,
                         SCOREBOARD_HEADER.POWERUPS,
                         {"goal" : self.name,
                          "alliance" : alliance.name,
                          "powerup" : powerup_type})

        if effect == POWERUP_TYPES.TWO_X:
            process_powerup(self.blue_two_x_timer, self.gold_two_x_timer,
                            CONSTANTS.TWO_X_DURATION, POWERUP_TYPES.TWO_X)
        elif effect == POWERUP_TYPES.ZERO_X:
            process_powerup(self.blue_zero_x_timer, self.gold_zero_x_timer,
                            CONSTANTS.ZERO_X_DURATION, POWERUP_TYPES.ZERO_X)
        elif effect == POWERUP_TYPES.STEAL:
            self.owner = alliance
            lcm_send(LCM_TARGETS.SCOREBOARD,
                     SCOREBOARD_HEADER.POWERUPS,
                     {"goal" : self.name,
                      "alliance" : alliance.name,
                      "powerup" : POWERUP_TYPES.STEAL})
        else:
            lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.CODE_RESULT, {"alliance" : alliance.name,
                                                                      "result" : 0})
