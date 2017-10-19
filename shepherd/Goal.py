from Utils import *
from Timer import *

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
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.owner = None
        self.current_bid = 0
        self.current_bid_team = None
        self.previous_bid = 0
        self.previous_bid_team = None
        self.bid_timer = Timer(TIMER_TYPES.BID, name)
        self.gold_two_x_timer = Timer(TIMER_TYPES.DURATION)
        self.gold_zero_x_timer = Timer(TIMER_TYPES.DURATION)
        self.blue_two_x_timer = Timer(TIMER_TYPES.DURATION)
        self.blue_zero_x_timer = Timer(TIMER_TYPES.DURATION)

    def score(self, alliance):
        """ modifies the owner alliance's score based on the value of the goal,
            the current multipliers,and the alliances multiplier, if the
            scorring Alliance is the owning alliance.
                alliance - Alliance object representing the scoring team
        """
        pass

    def calc_multiplier(self):
        """ returns an integer that represents the overall multiplier for this
            goal, by checking each timer in the goal
        """
        pass

    def apply_powerup(self, effect, alliance):
        """ applies effect passed in from an alliance, and determines what
            should happen, based on the allianced passed in, and the alliance
            of the goal.
            return an Integer signifying what the result of the call was.
                1 - success
                -1 - cannot be applied to this goal
                -2 - cannot steal your own goal
                -3 - other error
            effect - enum representing an effect to be applied to the goal
            alliance - the alliance trying to apply the effect to the goal
        """
        pass
