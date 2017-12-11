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
    bid_increase_constant = CONSTANTS.BID_INCREASE_CONSTANT
    def __init__(self, name, value, start_bid):
        self.name = name
        self.value = value
        self.owner = None
        self.current_bid = start_bid
        self.current_bid_team = None
        self.previous_bid = start_bid
        self.previous_bid_team = None
        self.bid_timer = Timer(TIMER_TYPES.BID, name)
        self.gold_two_x_timer = Timer(TIMER_TYPES.DURATION)
        self.gold_zero_x_timer = Timer(TIMER_TYPES.DURATION)
        self.blue_two_x_timer = Timer(TIMER_TYPES.DURATION)
        self.blue_zero_x_timer = Timer(TIMER_TYPES.DURATION)

    def reset(self):
        #TODO
        pass

    def set_autonomous(self):
        self.value = 2 * self.value
        self.current_bid = self.current_bid / 2

    def set_teleop(self):
        self.value = self.value / 2
        self.current_bid = self.current_bid * 2

    def set_owner(self, alliance):
        self.owner = alliance

    def score(self, alliance):
        """ modifies the owner alliance's score based on the value of the goal,
            the current multipliers,and the alliances multiplier, if the
            scoring Alliance is the owning alliance.

            alliance - Alliance object representing the scoring team
        """
        if self.owner is alliance:
            alliance.change_score(self.value * self.calc_multiplier() *\
                alliance.alliance_multiplier)

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
                if blue_timer.is_running():
                    lcm_send(LCM_TARGETS.SENSORS,
                             SENSOR_HEADER.FAILED_POWERUP)
                else:
                    blue_timer.start_timer(constants_cooldown)
                    lcm_send(LCM_TARGETS.SCOREBOARD,
                             SCOREBOARD_HEADER.POWERUPS,
                             [self.name, alliance.name, powerup_type])
            elif alliance.name == ALLIANCE_COLOR.GOLD:
                if gold_timer.is_running():
                    lcm_send(LCM_TARGETS.SENSORS,
                             SENSOR_HEADER.FAILED_POWERUP)
                else:
                    gold_timer.start_timer(constants_cooldown)
                    lcm_send(LCM_TARGETS.SCOREBOARD,
                             SCOREBOARD_HEADER.POWERUPS,
                             [self.name, alliance.name, powerup_type])


        if effect == POWERUP_TYPES.TWO_X:
            process_powerup(self.blue_two_x_timer, self.gold_two_x_timer,
                            CONSTANTS.TWO_X_COOLDOWN, POWERUP_TYPES.TWO_X)
        elif effect == POWERUP_TYPES.ZERO_X:
            process_powerup(self.blue_zero_x_timer, self.gold_zero_x_timer,
                            CONSTANTS.ZERO_X_COOLDOWN, POWERUP_TYPES.ZERO_X)
        elif effect == POWERUP_TYPES.STEAL:
            if self.owner is alliance:
                lcm_send(LCM_TARGETS.SENSORS,
                         SENSOR_HEADER.FAILED_POWERUP)
            else:
                self.owner = alliance
                lcm_send(LCM_TARGETS.SCOREBOARD,
                         SCOREBOARD_HEADER.POWERUPS,
                         [self.name, alliance.name, POWERUP_TYPES.STEAL])
        else:
            lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.FAILED_POWERUP)
        return
